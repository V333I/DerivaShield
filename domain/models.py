from dataclasses import dataclass
from typing import Optional

@dataclass
class TrafficMetric:
    timestamp: float
    packets_per_second: float
    bytes_per_second: float
    unique_ports_per_second: float
    source: str
    
    # Derivadas (calculadas posteriormente)
    derivative_packets: float = 0.0
    derivative_bytes: float = 0.0
    derivative_ports: float = 0.0
    second_derivative_packets: float = 0.0

@dataclass
class Alert:
    timestamp: float
    alert_type: str # "Posible DDoS", "Posible Port Scanning"
    severity: str # "baja", "media", "alta"
    metric_name: str
    metric_value: float
    derivative_value: float
    threshold_value: float
    description: str
    source: str
    id: Optional[int] = None
