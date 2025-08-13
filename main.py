"""
Punto de entrada de la aplicación donde se inicia todo el sistema.
"""

from logger_config import logger
from data.db_utils import get_connection
from data.schema import create_tables

# Inicialización y verificación del entorno
logger.info("Aplicación iniciando")

# Creación/validación de tablas
try:
    logger.debug("Creando/verificando tablas de base de datos...")
    create_tables()
    logger.info("Tablas creadas/verificadas correctamente")
except Exception as e:
    logger.exception("Error al crear/verificar las tablas de la base de datos")
    raise

# Prueba de conexión a la base de datos
try:
    logger.debug("Abriendo conexión a la base de datos...")
    conn = get_connection()
    logger.info("¡Conexión a la base de datos exitosa!")
finally:
    conn.close()
    logger.debug("Conexión a la base de datos cerrada")



# TODO: Aquí se debe agregar:
# 1. Inicialización de la interfaz gráfica (PyQt6)
# 2. Ciclo principal de la aplicación
