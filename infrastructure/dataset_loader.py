import os
import pandas as pd
from config import settings
from domain.models import TrafficMetric

class DatasetLoader:
    def __init__(self, bus):
        self.bus = bus
        self.dataset_path = os.path.join(settings.DATASET_DIR, 'dataset.csv')
        
    def check_dataset_exists(self):
        return os.path.exists(self.dataset_path)
        
    def process_dataset(self):
        if not self.check_dataset_exists():
            print("No se encontró dataset, usando modo demo o real.")
            return False
            
        print(f"Procesando dataset desde {self.dataset_path}...")
        try:
            # Solo leemos algunas columnas relevantes simulando un streaming
            df = pd.read_csv(self.dataset_path)
            
            # Asumimos que el CSV del CIC-IDS-2018 tiene campos como 'Flow Packets/s', 'Flow Bytes/s' etc.
            # Aquí hacemos un mapeo genérico por si los nombres varían en el dataset recortado
            col_packets = next((c for c in df.columns if 'packet' in c.lower() and ('/s' in c.lower() or 'rate' in c.lower())), None)
            col_bytes = next((c for c in df.columns if 'byte' in c.lower() and ('/s' in c.lower() or 'rate' in c.lower())), None)
            col_ports = next((c for c in df.columns if 'port' in c.lower()), None)
            
            if not col_packets or not col_bytes:
                print("El dataset no contiene las columnas necesarias (Packets/s, Bytes/s).")
                return False
                
            for index, row in df.iterrows():
                packets = float(row[col_packets]) if not pd.isna(row[col_packets]) else 0
                bytes_sec = float(row[col_bytes]) if not pd.isna(row[col_bytes]) else 0
                # Simulamos puertos únicos
                ports = float(row[col_ports]) if col_ports and not pd.isna(row[col_ports]) else 1
                
                metric = TrafficMetric(
                    timestamp=time.time(), # Simulamos tiempo real
                    packets_per_second=packets,
                    bytes_per_second=bytes_sec,
                    unique_ports_per_second=ports,
                    source="dataset"
                )
                self.bus.publish('nuevo_dato', metric)
                
                # Pausar ligeramente para simular streaming si es necesario, 
                # o procesar todo en batch según el uso.
            return True
            
        except Exception as e:
            print(f"Error procesando dataset: {e}")
            return False
