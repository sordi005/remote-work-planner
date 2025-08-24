"""Resetea la base de datos: elimina el archivo SQLite y recrea el esquema.

Uso:
    python scripts/reset_db.py
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

# Habilitar imports del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import DB_PATH
from data.schema import create_tables


def main() -> None:
    db_path = Path(DB_PATH)
    if db_path.exists():
        try:
            os.remove(db_path)
            print(f"DB eliminada: {db_path}")
        except Exception as e:
            print(f"No se pudo eliminar la DB: {e}")
            raise
    else:
        print(f"DB no existía: {db_path}")

    # Recrear esquema en DB nueva
    create_tables()
    print("Esquema recreado correctamente.")


if __name__ == "__main__":
    main()


