"""Punto de entrada de la aplicación."""

from logger_config import logger
from data.db_utils import get_connection
from data.schema import create_tables

logger.info("Aplicación iniciando")

try:
    logger.debug("Creando/verificando tablas de base de datos...")
    create_tables()
    logger.info("Tablas listas")
except Exception:
    logger.exception("Error al crear/verificar tablas")
    raise

try:
    logger.debug("Abriendo conexión a la base de datos...")
    conn = get_connection()
    logger.info("Conexión a la base de datos OK")
finally:
    conn.close()
    logger.debug("Conexión a la base de datos cerrada")



# TODO: UI (PyQt6) e inicio del ciclo principal
