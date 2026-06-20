import time
import random
from domain.models import TrafficMetric

class TrafficSimulator:
    def __init__(self, bus):
        self.bus = bus
        self.running = False
        self.scenario_timer = 0
        self.current_scenario = "normal"
        self.source = "demo"
        
    def start(self):
        self.running = True
        while self.running:
            self.generate_traffic()
            time.sleep(1) # Generar cada 1 segundo
            
    def stop(self):
        self.running = False
        
    def generate_traffic(self):
        self.scenario_timer += 1
        
        # Alternar escenarios cada ~30-40 segundos
        if self.scenario_timer > random.randint(30, 40):
            self.scenario_timer = 0
            scenarios = ["normal", "ddos", "port_scan"]
            # Siempre intentamos volver a normal o lanzar un ataque
            if self.current_scenario != "normal":
                self.current_scenario = "normal"
            else:
                self.current_scenario = random.choice(["ddos", "port_scan"])
        
        # Base normal
        base_packets = random.uniform(50, 150)
        base_bytes = base_packets * random.uniform(200, 800)
        base_ports = random.uniform(5, 20)
        
        if self.current_scenario == "normal":
            # Variaciones leves
            packets = base_packets
            bytes_sec = base_bytes
            ports = base_ports
            
        elif self.current_scenario == "ddos":
            # Aumento masivo y abrupto de paquetes y bytes
            packets = base_packets + random.uniform(5000, 15000)
            bytes_sec = packets * random.uniform(500, 1500)
            ports = base_ports + random.uniform(0, 10) # Puertos no suben tanto
            
        elif self.current_scenario == "port_scan":
            # Aumento masivo de puertos únicos, paquetes aumentan pero no exagerado
            packets = base_packets + random.uniform(500, 1500)
            bytes_sec = packets * random.uniform(60, 100) # Paquetes pequeños (SYN)
            ports = base_ports + random.uniform(500, 2000)
            
        metric = TrafficMetric(
            timestamp=time.time(),
            packets_per_second=packets,
            bytes_per_second=bytes_sec,
            unique_ports_per_second=ports,
            source=self.source
        )
        
        # Publicar evento al bus
        self.bus.publish('nuevo_dato', metric)
