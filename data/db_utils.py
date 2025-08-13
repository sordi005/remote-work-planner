from config import DB_PATH

"""Conexión centralizada a SQLite (usa la ruta de config)."""

def get_connection():
    """Devuelve una conexión sqlite3 a DB_PATH."""
    import sqlite3
    return sqlite3.connect(DB_PATH)