import sqlite3
from config import settings
from domain.models import TrafficMetric, Alert

def get_connection():
    return sqlite3.connect(settings.DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de métricas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS traffic_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        packets_per_second REAL,
        bytes_per_second REAL,
        unique_ports_per_second REAL,
        derivative_packets REAL,
        derivative_bytes REAL,
        derivative_ports REAL,
        second_derivative_packets REAL,
        source TEXT
    )
    ''')
    
    # Tabla de alertas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        alert_type TEXT,
        severity TEXT,
        metric_name TEXT,
        metric_value REAL,
        derivative_value REAL,
        threshold_value REAL,
        description TEXT,
        source TEXT
    )
    ''')
    
    # Tabla de configuración
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def save_metric(metric: TrafficMetric):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO traffic_metrics (
        timestamp, packets_per_second, bytes_per_second, unique_ports_per_second,
        derivative_packets, derivative_bytes, derivative_ports, second_derivative_packets, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metric.timestamp, metric.packets_per_second, metric.bytes_per_second, metric.unique_ports_per_second,
        metric.derivative_packets, metric.derivative_bytes, metric.derivative_ports, metric.second_derivative_packets,
        metric.source
    ))
    conn.commit()
    conn.close()

def save_alert(alert: Alert):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (
        timestamp, alert_type, severity, metric_name, metric_value, 
        derivative_value, threshold_value, description, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        alert.timestamp, alert.alert_type, alert.severity, alert.metric_name, alert.metric_value,
        alert.derivative_value, alert.threshold_value, alert.description, alert.source
    ))
    conn.commit()
    conn.close()

def get_recent_metrics(limit=60):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM traffic_metrics ORDER BY timestamp DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_alerts(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
    
def clear_alerts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alerts')
    conn.commit()
    conn.close()
