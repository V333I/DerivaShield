import socket
import time
import argparse

def simulate_udp_flood(target_ip="127.0.0.1", target_port=9999, duration=5):
    print(f"⚠️ Iniciando simulación LOCAL de inundación UDP hacia {target_ip}:{target_port}")
    print(f"Duración de la prueba: {duration} segundos...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b"X" * 1024  # Carga de 1 KB
    
    end_time = time.time() + duration
    packets_sent = 0
    
    # Bucle rápido para generar la mayor cantidad de tráfico posible
    while time.time() < end_time:
        try:
            sock.sendto(payload, (target_ip, target_port))
            packets_sent += 1
        except Exception as e:
            pass # Ignorar errores menores del socket
            
    print(f"✅ Prueba terminada. Se enviaron aproximadamente {packets_sent} paquetes ({packets_sent / 1024:.2f} MB de datos).")
    print("Revisa tu Dashboard de DerivaShield para ver el pico y la alerta generada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta local inofensiva para disparar alertas en DerivaShield")
    parser.add_argument("--time", type=int, default=10, help="Duración en segundos")
    args = parser.parse_args()
    
    simulate_udp_flood(duration=args.time)
