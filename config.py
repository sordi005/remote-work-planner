"""Configuración global: rutas y parámetros compartidos."""

import sys
from pathlib import Path

# Detectar si corre empaquetado (PyInstaller) o en desarrollo
if getattr(sys, 'frozen', False):
    # PyInstaller expone la carpeta temporal con los recursos en sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
else:
    # En desarrollo, base = carpeta de este archivo
    BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "trabajo_remoto.db"  # SQLite local
RESOURCES_DIR = BASE_DIR / "ui" / "resources"

APP_NAME = "Trabajo Remoto"
VERSION = "1.0"

