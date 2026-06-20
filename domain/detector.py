import numpy as np
from collections import deque
from .models import TrafficMetric, Alert

class AnomalyDetector:
    def __init__(self, window_size=60, k=3.0):
        self.window_size = window_size
        self.k = k
        
        # Historial de métricas para cálculo de derivadas
        self.history = deque(maxlen=window_size)
        
        # Historial de derivadas para calcular media y desviación estándar
        self.deriv_packets_hist = deque(maxlen=window_size)
        self.deriv_ports_hist = deque(maxlen=window_size)
        
    def process_metric(self, metric: TrafficMetric) -> list[Alert]:
        alerts = []
        
        if len(self.history) > 0:
            prev_metric = self.history[-1]
            dt = metric.timestamp - prev_metric.timestamp
            
            if dt > 0:
                # Primera derivada: f'(t) ≈ [f(t) - f(t - Δt)] / Δt
                metric.derivative_packets = (metric.packets_per_second - prev_metric.packets_per_second) / dt
                metric.derivative_bytes = (metric.bytes_per_second - prev_metric.bytes_per_second) / dt
                metric.derivative_ports = (metric.unique_ports_per_second - prev_metric.unique_ports_per_second) / dt
                
                # Segunda derivada: f''(t) ≈ [f'(t) - f'(t - Δt)] / Δt
                if hasattr(prev_metric, 'derivative_packets') and prev_metric.derivative_packets != 0.0:
                    metric.second_derivative_packets = (metric.derivative_packets - prev_metric.derivative_packets) / dt
                
                # Evaluar umbrales
                if len(self.deriv_packets_hist) > 10: # Esperar a tener algo de estadística
                    # Detección de DDoS (Foco en paquetes)
                    mu_packets = np.mean(self.deriv_packets_hist)
                    sigma_packets = np.std(self.deriv_packets_hist)
                    threshold_packets = mu_packets + (self.k * sigma_packets)
                    
                    # Evitar falsos positivos por ruido estadístico usando un mínimo de aceleración (100 paq/s^2)
                    if abs(metric.derivative_packets) > threshold_packets and metric.derivative_packets > 100:
                        alerts.append(Alert(
                            timestamp=metric.timestamp,
                            alert_type="Posible DDoS",
                            severity="alta",
                            metric_name="packets_per_second",
                            metric_value=metric.packets_per_second,
                            derivative_value=metric.derivative_packets,
                            threshold_value=threshold_packets,
                            description=f"Aumento abrupto en paquetes/seg. Derivada supera umbral: {metric.derivative_packets:.2f} > {threshold_packets:.2f}",
                            source=metric.source
                        ))
                    
                    # Detección de Port Scanning (Foco en puertos únicos)
                    mu_ports = np.mean(self.deriv_ports_hist)
                    sigma_ports = np.std(self.deriv_ports_hist)
                    threshold_ports = mu_ports + (self.k * sigma_ports)
                    
                    # Evitar falsos positivos por ruido estadístico usando un mínimo de aceleración (10 puertos/s^2)
                    if abs(metric.derivative_ports) > threshold_ports and metric.derivative_ports > 10:
                        alerts.append(Alert(
                            timestamp=metric.timestamp,
                            alert_type="Posible Port Scanning",
                            severity="media",
                            metric_name="unique_ports_per_second",
                            metric_value=metric.unique_ports_per_second,
                            derivative_value=metric.derivative_ports,
                            threshold_value=threshold_ports,
                            description=f"Aumento abrupto de puertos destino únicos. Derivada supera umbral: {metric.derivative_ports:.2f} > {threshold_ports:.2f}",
                            source=metric.source
                        ))
                
                # Guardar historiales
                self.deriv_packets_hist.append(metric.derivative_packets)
                self.deriv_ports_hist.append(metric.derivative_ports)
                
        self.history.append(metric)
        return alerts
        
    def update_settings(self, k, window_size):
        self.k = k
        if self.window_size != window_size:
            self.window_size = window_size
            self.history = deque(self.history, maxlen=window_size)
            self.deriv_packets_hist = deque(self.deriv_packets_hist, maxlen=window_size)
            self.deriv_ports_hist = deque(self.deriv_ports_hist, maxlen=window_size)
