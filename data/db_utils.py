from config import DB_PATH

"""Conexión centralizada a SQLite (usa la ruta de config)."""

def get_connection():
    """Devuelve una conexión sqlite3 a DB_PATH con foreign_keys activado."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass
    return conn