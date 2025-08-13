"""Init/chequeo de esquema de base de datos (ejecución manual).

Hace:
- Crea/verifica users y records
- Chequea existencia en sqlite_master
- Verifica UNIQUE en users.docket y (records.user_id, date)
- Limpia datos de prueba

Uso:
    python scripts/db_init_check.py
"""

# Permitir importar módulos del proyecto al ejecutar este script directamente
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import sqlite3
from logger_config import logger
from data.schema import create_tables
from data.db_utils import get_connection


def _cleanup_test_data(cursor: sqlite3.Cursor) -> None:
    """
    Elimina datos de prueba insertados por este script, para no contaminar la DB real.
    """
    cursor.execute("DELETE FROM records WHERE user_id IN (SELECT id FROM users WHERE docket LIKE 'TEST-DCK-%')")
    cursor.execute("DELETE FROM users WHERE docket LIKE 'TEST-DCK-%'")


def _verify_tables_exist(cursor: sqlite3.Cursor) -> None:
    """
    Verifica que las tablas principales existan en sqlite_master.
    Lanza AssertionError si falta alguna.
    """
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','records')"
    )
    names = {row[0] for row in cursor.fetchall()}
    assert {"users", "records"} <= names, f"Tablas faltantes: { {'users','records'} - names }"


def _verify_unique_constraints(conn: sqlite3.Connection) -> None:
    """
    Verifica restricciones UNIQUE:
    - users.docket debe ser único
    - (records.user_id, date) debe ser único
    Lanza AssertionError si no se respetan.
    """
    cursor = conn.cursor()
    # Limpieza previa por seguridad
    _cleanup_test_data(cursor)
    conn.commit()

    # 1) UNIQUE en users.docket
    logger.debug("Probando UNIQUE en users.docket")
    cursor.execute(
        "INSERT INTO users(name, docket) VALUES (?, ?)",
        ("Test User", "TEST-DCK-UNIQ"),
    )
    conn.commit()
    unique_ok = False
    try:
        cursor.execute(
            "INSERT INTO users(name, docket) VALUES (?, ?)",
            ("Test User", "TEST-DCK-UNIQ"),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        unique_ok = True
        logger.info("Restricción UNIQUE en users.docket verificada correctamente")
    assert unique_ok, "Se esperaba violación de UNIQUE en users.docket y no ocurrió"

    # Obtener user_id para pruebas de records
    cursor.execute("SELECT id FROM users WHERE docket = ?", ("TEST-DCK-UNIQ",))
    user_id = cursor.fetchone()[0]

    # 2) UNIQUE en (records.user_id, date)
    logger.debug("Probando UNIQUE en (records.user_id, date)")
    cursor.execute(
        "INSERT INTO records(user_id, date, week_day) VALUES (?, ?, ?)",
        (user_id, "2025-01-01", "Lunes"),
    )
    conn.commit()
    unique_pair_ok = False
    try:
        cursor.execute(
            "INSERT INTO records(user_id, date, week_day) VALUES (?, ?, ?)",
            (user_id, "2025-01-01", "Lunes"),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        unique_pair_ok = True
        logger.info("Restricción UNIQUE en (records.user_id, date) verificada correctamente")
    assert unique_pair_ok, "Se esperaba violación de UNIQUE en (records.user_id, date) y no ocurrió"

    # Limpieza posterior de datos de prueba
    _cleanup_test_data(cursor)
    conn.commit()


def main() -> None:
    logger.info("Inicializando verificación de esquema de base de datos")

    # 1) Crear/Verificar tablas
    try:
        create_tables()
        logger.info("Tablas creadas/verificadas")
    except Exception:
        logger.exception("Error al crear/verificar tablas")
        raise

    # 2) Verificación de existencia y restricciones
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            _verify_tables_exist(cursor)
            logger.info("Existencia de tablas verificada")
            _verify_unique_constraints(conn)
            logger.info("Restricciones UNIQUE verificadas")
    except AssertionError as ae:
        logger.exception("Fallo en verificación del esquema: %s", ae)
        raise
    except Exception:
        logger.exception("Error inesperado durante verificación del esquema")
        raise

    logger.info("Verificación de esquema completada exitosamente")


if __name__ == "__main__":
    main()


