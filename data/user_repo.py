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
                cursor.execute("SELECT id, name, docket FROM users")
                rows = cursor.fetchall()
                logger.info("Usuarios obtenidos: %s", len(rows))
                return rows
        except Exception as e:
            logger.exception("Error al listar usuarios")
            raise ErrorDeBaseDeDatos(f"Error al listar usuarios: {e}")

    @staticmethod
    def delete_user(id):
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

    @staticmethod
    def get_by_id(id):
        """Obtiene un usuario por id (id, name, docket) o None si no existe."""
        logger.debug("Obteniendo usuario id=%s", id)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, docket FROM users WHERE id = ?", (id,))
                row = cursor.fetchone()
                logger.info("Usuario encontrado=%s id=%s", bool(row), id)
                return row
        except Exception as e:
            logger.exception("Error al obtener usuario id=%s", id)
            raise ErrorDeBaseDeDatos(f"Error al obtener usuario: {e}")

    @staticmethod
    def update(id, name, docket):
        """Actualiza nombre/docket del usuario por id."""
        logger.debug("Actualizando usuario id=%s name=%s docket=%s", id, name, docket)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET name = ?, docket = ? WHERE id = ?",
                    (name, docket, id),
                )
                conn.commit()
                logger.info("Usuario actualizado id=%s", id)
        except Exception as e:
            logger.exception("Error al actualizar usuario id=%s", id)
            if "UNIQUE constraint failed" in str(e):
                raise UsuarioYaExiste("El usuario ya existe.")
            raise ErrorDeBaseDeDatos(f"Error al actualizar usuario: {e}")

    @staticmethod
    def exist_by_name(name):
        """Devuelve True si existe un usuario con ese name; False en caso contrario."""
        logger.debug("Verificando existencia de usuario name=%s", name)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE name = ?)", (name,))
                exists_flag = bool(cursor.fetchone()[0])
                logger.info("Existe usuario name=%s: %s", name, exists_flag)
                return exists_flag
        except Exception as e:
            logger.exception("Error al verificar existencia de usuario name=%s", name)
            raise ErrorDeBaseDeDatos(f"Error al verificar existencia: {e}")


