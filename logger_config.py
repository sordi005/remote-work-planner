"""Configuración centralizada de logging para la aplicación.

Define un formato consistente, salida a archivo rotado por fecha y a consola.
El nivel por defecto es DEBUG para desarrollo; en producción conviene INFO.
"""
import logging
from datetime import datetime
from config import LOG_DIR
import os

# Carpeta de logs ya creada en config
log_filename = os.path.join(str(LOG_DIR), f"{datetime.now():%Y-%m-%d}.log")

# Configuración básica de logging: nivel, formato y handlers
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a INFO en producción
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()  # También muestra en consola
    ]
)

# Logger raíz de la app (nivel se configura en basicConfig). Usar logging.getLogger(__name__) en módulos.
logger = logging.getLogger("GestorEmpleados")
