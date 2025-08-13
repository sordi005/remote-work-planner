import logging
import os
from datetime import datetime

# Carpeta de logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Nombre de archivo con fecha
log_filename = os.path.join(LOG_DIR, f"{datetime.now():%Y-%m-%d}.log")

# Configuración básica
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a INFO en producción
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()  # También muestra en consola
    ]
)

# Logger principal para usar en toda la app
logger = logging.getLogger("GestorEmpleados")
