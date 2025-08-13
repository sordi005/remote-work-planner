from logging import INFO, Logger
import sqlite3
from config import DB_PATH

"""
Módulo de utilidades para la base de datos.
Define la función de conexión centralizada usando la ruta configurada en config.py.
Esto permite que todos los repositorios usen la misma lógica de conexión y facilita el mantenimiento.
"""

def get_connection():
    """
    Devuelve una conexión a la base de datos SQLite usando la ruta global DB_PATH.
    Usar siempre esta función para acceder a la base de datos.
    """
    import sqlite3
    return sqlite3.connect(DB_PATH)