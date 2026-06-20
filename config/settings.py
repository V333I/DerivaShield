import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuraciones de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'derivashield.db')
DATASET_DIR = os.path.join(DATA_DIR, 'dataset')

# Crear directorios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)

# Configuraciones por defecto de Detección
DEFAULT_K_THRESHOLD = 3.0
DEFAULT_WINDOW_SIZE = 60 # Intervalos de 1 segundo

# Modos de ejecución
MODE_DEMO = "demo"
MODE_REAL = "real"
