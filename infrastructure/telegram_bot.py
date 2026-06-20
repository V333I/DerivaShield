import requests
from config import settings

def send_telegram_alert(alert_title, alert_description, severity, source):
    """
    Envía un mensaje de alerta por Telegram utilizando la API oficial de bots.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("Telegram Bot Token o Chat ID no configurados.")
        return
        
    emoji = "🚨" if severity.lower() == "alta" else "⚠️"
    
    text = f"{emoji} <b>DerivaShield Alerta</b>\n\n"
    text += f"<b>Ataque:</b> {alert_title}\n"
    text += f"<b>Severidad:</b> {severity.upper()}\n"
    text += f"<b>Origen:</b> {source}\n\n"
    text += f"<b>Detalles:</b> {alert_description}"
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        # Hacemos la petición POST con un timeout corto para no bloquear recursos
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Error de Telegram API: {response.text}")
    except Exception as e:
        print(f"Error de conexión enviando alerta a Telegram: {e}")
