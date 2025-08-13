from data.db_utils import get_connection

"""
Módulo encargado de la creación de las tablas principales de la base de datos.
Se debe ejecutar una vez al inicio de la aplicación para asegurar que las tablas existen.
"""

def create_tables():
    """
    Crea las tablas 'users' y 'records' si no existen.
    'users': almacena los empleados.
    'records': almacena los días remotos asignados a cada usuario.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                docket TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                week_day TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()