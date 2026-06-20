import time
import threading
from collections import defaultdict
from scapy.all import sniff, IP, TCP, UDP
from domain.models import TrafficMetric

class PacketCapture:
    def __init__(self, bus):
        self.bus = bus
        self.running = False
        self.packets_count = 0
        self.bytes_count = 0
        self.ports_set = set()
        self.lock = threading.Lock()
        
    def check_permissions(self):
        try:
            # Intento rápido de sniff para ver si tenemos permisos
            sniff(count=1, timeout=1)
            return True
        except Exception as e:
            print(f"Error de permisos Scapy: {e}")
            return False
            
    def packet_handler(self, packet):
        if IP in packet:
            with self.lock:
                self.packets_count += 1
                self.bytes_count += len(packet)
                
                if TCP in packet:
                    self.ports_set.add(packet[TCP].dport)
                elif UDP in packet:
                    self.ports_set.add(packet[UDP].dport)

    def process_interval(self):
        while self.running:
            time.sleep(1.0)
            
            with self.lock:
                packets = self.packets_count
                bytes_sec = self.bytes_count
                ports = len(self.ports_set)
                
                # Reset counters
                self.packets_count = 0
                self.bytes_count = 0
                self.ports_set = set()
                
            metric = TrafficMetric(
                timestamp=time.time(),
                packets_per_second=packets,
                bytes_per_second=bytes_sec,
                unique_ports_per_second=ports,
                source="real"
            )
            
            self.bus.publish('nuevo_dato', metric)
            
    def start(self):
        self.running = True
        
        # Hilo para procesar intervalos de 1 segundo y enviar métricas
        interval_thread = threading.Thread(target=self.process_interval, daemon=True)
        interval_thread.start()
        
        print("Iniciando captura de paquetes...")
        # Bucle de sniffing bloqueante
        sniff(prn=self.packet_handler, store=0, stop_filter=lambda x: not self.running)
        
    def stop(self):
        self.running = False
