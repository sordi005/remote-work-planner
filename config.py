import sys
from pathlib import Path

# Detecta si está empaquetado o en desarrollo
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

# Rutas importantes
DB_PATH = BASE_DIR / "trabajo_remoto.db"
RESOURCES_DIR = BASE_DIR / "ui" / "resources"


APP_NAME = "Trabajo Remoto"
VERSION = "1.0"

