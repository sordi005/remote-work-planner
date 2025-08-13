"""
Archivo de configuración global de la aplicación.
Define rutas, parámetros y configuraciones que se usan en toda la aplicación.

"""

import sys
from pathlib import Path

# Detecta si la aplicación está corriendo como ejecutable empaquetado (PyInstaller) o en desarrollo
if getattr(sys, 'frozen', False):
    # Si está empaquetado, PyInstaller crea una carpeta temporal donde están todos los recursos
    # sys._MEIPASS contiene la ruta a esa carpeta temporal
    BASE_DIR = Path(sys._MEIPASS)
else:
    # En desarrollo, la ruta base es la carpeta donde está este archivo config.py
    BASE_DIR = Path(__file__).resolve().parent

# carpeta donde se almacenan recursos como iconos, imágenes, etc.
DB_PATH = BASE_DIR / "trabajo_remoto.db" #  ubicación del archivo de base de datos SQLite

RESOURCES_DIR = BASE_DIR / "ui" / "resources"# carpeta donde se almacenan recursos como iconos, imágenes, etc.


# Información de la aplicación

APP_NAME = "Trabajo Remoto"
VERSION = "1.0"

