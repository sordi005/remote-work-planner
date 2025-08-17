from data.db_utils import get_connection
from exceptions import ErrorDeBaseDeDatos, RegistroDuplicado
import logging

logger = logging.getLogger(__name__)


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
    def exists_in_week(user_id, start_iso, end_iso):
        """Devuelve True si el usuario tiene al menos un registro entre start_iso y end_iso (incluidos)."""
        logger.debug("Verificando existencia en semana user_id=%s inicio=%s fin=%s", user_id, start_iso, end_iso)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT EXISTS(SELECT 1 FROM records WHERE user_id = ? AND date BETWEEN ? AND ?)",
                    (user_id, start_iso, end_iso),
                )
                flag = bool(cursor.fetchone()[0])
                logger.info("Existe registro en semana user_id=%s -> %s", user_id, flag)
                return flag
        except Exception as e:
            logger.exception("Error al verificar existencia en semana user_id=%s", user_id)
            raise ErrorDeBaseDeDatos(f"Error al verificar registros de la semana: {e}")

    @staticmethod
    def get_record_in_week(user_id, start_iso, end_iso):
        """Obtiene el registro más reciente del usuario entre start_iso y end_iso; None si no hay."""
        logger.debug("Obteniendo registro de la semana user_id=%s inicio=%s fin=%s", user_id, start_iso, end_iso)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, date, week_day
                    FROM records
                    WHERE user_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC
                    LIMIT 1
                    """,
                    (user_id, start_iso, end_iso),
                )
                row = cursor.fetchone()
                logger.info("Registro de la semana encontrado user_id=%s -> %s", user_id, bool(row))
                return row
        except Exception as e:
            logger.exception("Error al obtener registro de la semana user_id=%s", user_id)
            raise ErrorDeBaseDeDatos(f"Error al obtener registro de la semana: {e}")

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
            
    @staticmethod
    def update_record_date_and_day(record_id, date, week_day):
        """
        Actualiza la fecha y el nombre de día de un registro existente.
        Lanza ErrorDeBaseDeDatos para errores SQL y respeta UNIQUE(user_id, date).
        """
        logger.debug("Actualizando registro id=%s nueva_fecha=%s nuevo_dia=%s", record_id, date, week_day)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE records SET date = ?, week_day = ? WHERE id = ?",
                    (date, week_day, record_id),
                )
                conn.commit()
                logger.info("Registro actualizado id=%s", record_id)
        except Exception as e:
            logger.exception("Error al actualizar registro id=%s", record_id)
            if "UNIQUE constraint failed" in str(e):
                raise RegistroDuplicado("Ya existe un registro para ese día.")
            raise ErrorDeBaseDeDatos(f"Error al actualizar registro: {e}")
    
    @staticmethod
    def delete_all_records_by_user(user_id):
        """Elimina todos los registros de un usuario."""
        logger.debug("Eliminando todos los registros para user_id=%s", user_id)
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM records WHERE user_id = ?", (user_id,))
                conn.commit()
                logger.info("Todos los registros eliminados para user_id=%s", user_id)
        except Exception as e:
            logger.exception("Error al eliminar todos los registros para user_id=%s", user_id)
            raise ErrorDeBaseDeDatos(f"Error al eliminar todos los registros: {e}")
            