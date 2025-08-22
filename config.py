"""Configuración global: rutas y parámetros compartidos."""

import sys
import os
from pathlib import Path

# Detectar si corre empaquetado (PyInstaller) o en desarrollo
if getattr(sys, 'frozen', False):
    # PyInstaller expone la carpeta temporal con los recursos en sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
else:
    # En desarrollo, base = carpeta de este archivo
    BASE_DIR = Path(__file__).resolve().parent

# Carpeta de datos del usuario (persistente entre ejecuciones y fuera del bundle)
LOCAL_APPDATA = os.getenv("LOCALAPPDATA") or str(Path.home())
APP_DIR = Path(LOCAL_APPDATA) / "TrabajoRemoto"
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DIR / "trabajo_remoto.db"  # SQLite local persistente
RESOURCES_DIR = BASE_DIR / "ui" / "resources"
LOG_DIR = APP_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "Trabajo Remoto"
VERSION = "1.0"

