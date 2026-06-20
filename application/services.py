from .event_bus import bus
from domain.detector import AnomalyDetector
from infrastructure.database import save_metric, save_alert
from infrastructure.traffic_simulator import TrafficSimulator
from infrastructure.packet_capture import PacketCapture
from config import settings
import threading
import time

class AppService:
    def __init__(self):
        self.detector = AnomalyDetector(
            window_size=settings.DEFAULT_WINDOW_SIZE, 
            k=settings.DEFAULT_K_THRESHOLD
        )
        self.simulator = None
        self.capture = None
        self.running = False
        
        # Suscribir al bus de eventos
        bus.subscribe('nuevo_dato', self.handle_new_metric)
        bus.subscribe('alerta_detectada', self.handle_alert)
        
    def start_demo_mode(self):
        print("Iniciando en modo DEMO (Simulador)...")
        self.running = True
        self.simulator = TrafficSimulator(bus)
        
        # Ejecutar en hilo separado para no bloquear la app
        self.thread = threading.Thread(target=self.simulator.start, daemon=True)
        self.thread.start()
        
    def start_real_mode(self):
        print("Intentando iniciar en modo REAL (Scapy)...")
        self.capture = PacketCapture(bus)
        if self.capture.check_permissions():
            self.running = True
            self.thread = threading.Thread(target=self.capture.start, daemon=True)
            self.thread.start()
        else:
            print("No se pudo iniciar captura real por falta de permisos. Cayendo a modo DEMO.")
            self.start_demo_mode()
            
    def stop(self):
        self.running = False
        if self.simulator:
            self.simulator.stop()
        if self.capture:
            self.capture.stop()
            
    def handle_new_metric(self, metric):
        # 1. Pasar por el detector matemático
        alerts = self.detector.process_metric(metric)
        
        # 2. Guardar métrica en base de datos local SQLite
        save_metric(metric)
        
        # 3. Notificar que se calculó y guardó la métrica para el dashboard
        bus.publish('metrica_calculada', metric)
        
        # 4. Procesar las alertas si las hay
        for alert in alerts:
            bus.publish('alerta_detectada', alert)
            
    def handle_alert(self, alert):
        # Guardar en base de datos
        save_alert(alert)
        # Publicar para que el dashboard se actualice
        bus.publish('alerta_guardada', alert)
        
    def update_settings(self, k, window_size):
        self.detector.update_settings(k, window_size)
