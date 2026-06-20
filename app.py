import argparse
from infrastructure.database import init_db
from application.services import AppService
from presentation.dashboard import app, server
import presentation.dashboard as dashboard_module
import os

def main():
    parser = argparse.ArgumentParser(description="DerivaShield - Detección de Anomalías con Cálculo Diferencial")
    parser.add_argument('--mode', choices=['demo', 'real'], default='demo', help="Modo de ejecución (demo o captura real)")
    args = parser.parse_args()
    
    print("Iniciando DerivaShield...")
    print("Inicializando Base de Datos local...")
    init_db()
    
    # Crear servicio principal
    service = AppService()
    
    # Inyectar el servicio al dashboard para que pueda enviar actualizaciones de settings
    dashboard_module.app_service = service
    
    if args.mode == 'demo':
        service.start_demo_mode()
    else:
        service.start_real_mode()
        
    print("\n=======================================================")
    print("DerivaShield esta corriendo!")
    print("Abre tu navegador en: http://127.0.0.1:8050")
    print("Presiona CTRL+C para detener el sistema.")
    print("=======================================================\n")
    
    try:
        # Dash corre en un servidor bloqueante, ideal para el hilo principal
        app.run(debug=False, host='127.0.0.1', port=8050)
    except KeyboardInterrupt:
        print("Deteniendo sistema...")
        service.stop()

if __name__ == '__main__':
    main()
