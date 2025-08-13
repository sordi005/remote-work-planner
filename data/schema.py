from data.db_utils import get_connection
import logging

logger = logging.getLogger(__name__)

"""
Módulo encargado de la creación de las tablas principales de la base de datos.
Se debe ejecutar una vez al inicio de la aplicación para asegurar que las tablas existen.
"""

def create_tables():
    """
    Crea o verifica las tablas 'users' y 'records'.
    """
    logger.debug("Iniciando creación/verificación de tablas 'users' y 'records'")
    with get_connection() as conn:
        cursor = conn.cursor()
        # crear table users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                docket TEXT NOT NULL UNIQUE
            )
        """)
        # crear tabla records (único por usuario y fecha para evitar duplicar el mismo día)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                week_day TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        """)
        # Índice recomendado para consultas por usuario y fecha
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_records_user_date
            ON records(user_id, date DESC)
        """)
        conn.commit()
    logger.info("Tablas 'users' y 'records' creadas/verificadas")