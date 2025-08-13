from data.db_utils import get_connection
import logging

logger = logging.getLogger(__name__)

"""Creación/verificación de tablas principales de la base de datos."""

def create_tables():
    """Crea o verifica 'users' y 'records', e índice de consultas por usuario/fecha."""
    logger.debug("Creando/verificando tablas 'users' y 'records'")
    with get_connection() as conn:
        cursor = conn.cursor()
        # users: empleados (docket único)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                docket TEXT NOT NULL UNIQUE
            )
        """)
        # records: días remotos; único por (user_id, date)
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
        # Índice para consultas por usuario y fecha
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_records_user_date
            ON records(user_id, date DESC)
        """)
        conn.commit()
    logger.info("Tablas listas: users, records")