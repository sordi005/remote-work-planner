"""Punto de entrada de la aplicación.

Responsabilidades:
- Inicializar logging
- Crear/verificar esquema de base de datos
- Probar conexión
- Lanzar la interfaz gráfica
"""

from logger_config import logger
from data.db_utils import get_connection
from data.schema import create_tables
from ui.main_window import run_app


def main() -> None:
    logger.info("Aplicación iniciando")
    try:
        logger.debug("Creando/verificando tablas de badse de datos...")
        create_tables()
        logger.info("Tablas listas")
    except Exception:
        logger.exception("Error al crear/verificar tablas")
        raise

    try:
        logger.debug("Abriendo conexión de prueba a la base de datos...")
        conn = get_connection()
        logger.info("Conexión a la base de datos OK")
    finally:
        conn.close()
        logger.debug("Conexión a la base de datos cerrada")

    run_app()

    logger.info("Aplicación finalizada")

if __name__ == "__main__":
    main()
