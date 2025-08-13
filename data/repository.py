from sqlite3 import Cursor
from data.db_utils import get_connection
from exceptions import ErrorDeBaseDeDatos, UsuarioYaExiste, RegistroDuplicado
import logging

logger = logging.getLogger(__name__)

# Repositorio para operaciones sobre la tabla de usuarios
class UserRepository:
    @staticmethod
    def create(name, docket):
        """
        Crea un nuevo usuario en la base de datos.
        Lanza UsuarioYaExiste si el usuario ya está registrado (clave única).
        Lanza ErrorDeBaseDeDatos para otros errores de base de datos.
        """
        logger.debug("Intentando crear usuario name=%s docket=%s", name, docket)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users(name, docket) VALUES(?,?)", (name, docket))
                conn.commit()
                user_id = cursor.lastrowid
                logger.info("Usuario creado id=%s name=%s", user_id, name)
                return user_id
        except Exception as e:
            logger.exception("Error al crear usuario name=%s docket=%s", name, docket)
            # Si la base de datos lanza un error de restricción única, el usuario ya existe
            if "UNIQUE constraint failed" in str(e):
                raise UsuarioYaExiste("El usuario ya existe.")
            # Para cualquier otro error, lanzamos una excepción genérica de base de datos
            raise ErrorDeBaseDeDatos(f"Error al crear usuario: {e}")

    @staticmethod
    def list_all():
        """
        Devuelve una lista de todos los usuarios registrados.
        Lanza ErrorDeBaseDeDatos si ocurre un error en la consulta.
        """
        logger.debug("Listando todos los usuarios")
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, docket FROM users")
                rows = cursor.fetchall()
                logger.info("Usuarios obtenidos: %s", len(rows))
                return rows
        except Exception as e:
            logger.exception("Error al listar usuarios")
            raise ErrorDeBaseDeDatos(f"Error al listar usuarios: {e}")

    @staticmethod
    def delete(id):
        """
        Elimina un usuario por su ID.
        Lanza ErrorDeBaseDeDatos si ocurre un error en la operación.
        """
        logger.debug("Eliminando usuario id=%s", id)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (id,))
                conn.commit()
                logger.info("Usuario eliminado id=%s", id)
        except Exception as e:
            logger.exception("Error al eliminar usuario id=%s", id)
            raise ErrorDeBaseDeDatos(f"Error al eliminar usuario: {e}")

# Repositorio para operaciones CRUD sobre la tabla de registros de días remotos
class RecordRespository():
    @staticmethod
    def create_record(user_id, date, week_day):
        """
        Crea un nuevo registro de día remoto para un usuario.
        Lanza RegistroDuplicado si ya existe un registro para ese día.
        Lanza ErrorDeBaseDeDatos para otros errores de base de datos.
        """
        logger.debug("Creando registro user_id=%s date=%s week_day=%s", user_id, date, week_day)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO records (user_id, date, week_day) VALUES (?, ?, ?)",
                    (user_id, date, week_day)
                )
                conn.commit()
                record_id = cursor.lastrowid
                logger.info("Registro creado id=%s para user_id=%s", record_id, user_id)
                return record_id
        except Exception as e:
            logger.exception("Error al crear registro user_id=%s date=%s week_day=%s", user_id, date, week_day)
            # Si la base de datos lanza un error de restricción única, ya existe el registro
            if "UNIQUE constraint failed" in str(e):
                raise RegistroDuplicado("Ya existe un registro para ese día.")
            raise ErrorDeBaseDeDatos(f"Error al crear registro: {e}")

    @staticmethod
    def list_by_user(user_id):
        """
        Devuelve todos los registros de días remotos de un usuario, ordenados por fecha descendente.
        Lanza ErrorDeBaseDeDatos si ocurre un error en la consulta.
        """
        logger.debug("Listando registros para user_id=%s", user_id)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, date, week_day FROM records WHERE user_id = ? ORDER BY date DESC",
                    (user_id,)
                )
                rows = cursor.fetchall()
                logger.info("Registros obtenidos para user_id=%s: %s", user_id, len(rows))
                return rows
        except Exception as e:
            logger.exception("Error al listar registros para user_id=%s", user_id)
            raise ErrorDeBaseDeDatos(f"Error al listar registros: {e}")

    @staticmethod
    def get_latest_record(user_id):
        """
        Devuelve el último registro de día remoto de un usuario (el más reciente).
        Lanza ErrorDeBaseDeDatos si ocurre un error en la consulta.
        """
        logger.debug("Obteniendo último registro para user_id=%s", user_id)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, date, week_day FROM records WHERE user_id = ? ORDER BY date DESC LIMIT 1",
                    (user_id,)
                )
                row = cursor.fetchone()
                logger.info("Último registro para user_id=%s: %s", user_id, bool(row))
                return row
        except Exception as e:
            logger.exception("Error al obtener el último registro para user_id=%s", user_id)
            raise ErrorDeBaseDeDatos(f"Error al obtener el último registro: {e}")
            
