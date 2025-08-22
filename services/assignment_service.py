"""Servicio de asignaciones: reglas de negocio para días remotos.

Responsabilidades principales:
- Determinar los límites de semana ISO (lunes..domingo)
- Validar reglas de negocio antes de crear o cambiar un registro
- Orquestar acceso a repositorios sin exponer detalles SQL a la UI
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import logging

from data.user_repo import  UserRepository
from data.assignament_repo import RecordRespository

from models.record import Record
from models.user import User
from exceptions import (
    AppError,
    DiaNoPermitido,
    YaRegistradoEstaSemana,
    NoHayRegistroEstaSemana,
    FechaFueraDeSemanaActual,
)

logger = logging.getLogger(__name__)


_WEEKDAY_MAP = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def _parse_iso(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _week_bounds(d: date) -> Tuple[str, str]:
    """Devuelve (inicio_iso, fin_iso) de la semana ISO [lunes..domingo] que contiene d."""
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


class AsignacionService:
   
    def __init__(self, record_repo: RecordRespository | None = None, user_repo: UserRepository | None = None) -> None:
        self._records = record_repo or RecordRespository
        self._users = user_repo or UserRepository

    def is_registered_this_week(self, user_id: int, ref_date: Optional[date] = None) -> bool:
        """True si el usuario tiene un registro en la semana de `ref_date` (por defecto hoy)."""
        ref = ref_date or date.today()
        start_iso, end_iso = _week_bounds(ref)
        logger.debug("Esta registrado esta semana user_id=%s start=%s end=%s", user_id, start_iso, end_iso)
        return self._records.exists_in_week(user_id, start_iso, end_iso)

    def latest_for_user(self, user_id: int) -> Optional[Record]:
        """Último registro del usuario o None."""
        row = self._records.get_latest_record(user_id)
        return Record.from_row(row) if row else None

    def list_by_user(self, user_id: int) -> List[Record]:
        """Lista registros del usuario como modelos Record (ordenados por fecha desc)."""
        rows = self._records.list_by_user(user_id)
        logger.debug("Listando registros del usuario user_id=%s total=%s", user_id, len(rows))
        return [Record.from_row(r) for r in rows]

    # === Validaciones separadas ===
    def _validate_day_allowed(self, d: date) -> None:
        """No se permite Lunes (0) ni Sábado (5) ni Domingo (6)."""
        weekday = d.weekday()
        if weekday in (0, 5, 6):
            raise DiaNoPermitido("No se permite registrar Lunes ni fines de semana.")

    def _validate_in_current_week(self, d: date, now: Optional[date] = None) -> None:
        """La fecha debe pertenecer a la semana actual del sistema.

        Evita que la UI envíe fechas de otras semanas por error.
        """
        today = now or date.today()
        cur_start, cur_end = _week_bounds(today)
        if not (cur_start <= d.isoformat() <= cur_end):
            raise FechaFueraDeSemanaActual("La fecha no pertenece a la semana actual.")

    def _validate_not_same_weekday_as_prev_week(self, user_id: int, d: date) -> None:
        """No repetir el mismo día que la semana anterior para el mismo usuario."""
        week_day = _WEEKDAY_MAP[d.weekday()]
        prev_week_day = d - timedelta(days=7)
        prev_start, prev_end = _week_bounds(prev_week_day)
        prev = self._records.get_record_in_week(user_id, prev_start, prev_end)
        if prev is not None:
            _prev_id, _prev_date, prev_week_day_name = prev
            if prev_week_day_name == week_day:
                logger.debug(
                    "Regla violada user_id=%s date=%s week_day=%s prev_week=(%s..%s) prev_day=%s",
                    user_id, d.isoformat(), week_day, prev_start, prev_end, prev_week_day_name,
                )
                raise AppError("No puede repetir el mismo día que la semana anterior.")

    def is_same_weekday_as_prev_week(self, user_id: int, date_iso: str) -> bool:
        """True si la fecha cae en el mismo día de semana que el registro de la semana anterior."""
        d = _parse_iso(date_iso)
        week_day = _WEEKDAY_MAP[d.weekday()]
        prev_week_day = d - timedelta(days=7)
        prev_start, prev_end = _week_bounds(prev_week_day)
        prev = self._records.get_record_in_week(user_id, prev_start, prev_end)
        if prev is None:
            return False
        _prev_id, _prev_date, prev_week_day_name = prev
        return prev_week_day_name == week_day

    def prev_week_record(self, user_id: int, date_iso: str) -> Optional[Record]:
        """Devuelve el registro de la semana anterior respecto a `date_iso`, si existe."""
        d = _parse_iso(date_iso)
        prev_ref = d - timedelta(days=7)
        start_iso, end_iso = _week_bounds(prev_ref)
        row = self._records.get_record_in_week(user_id, start_iso, end_iso)
        return Record.from_row(row) if row else None

    def _ensure_not_registered_this_week(self, user_id: int, ref_date: Optional[date] = None) -> None:
        """Valida que el usuario no posea ya un registro en la semana actual."""
        if self.is_registered_this_week(user_id, ref_date):
            raise YaRegistradoEstaSemana("El empleado ya tiene un registro esta semana.")

    # === Operaciones principales ===
    def assign_day(self, user_id: int, date_iso: str, allow_repeat_prev_week: bool = False) -> Record:
        """Asigna fecha aplicando todas las validaciones de negocio."""
        urow = self._users.get_by_id(user_id)
        if not urow:
            raise AppError("El usuario no existe.")

        d = _parse_iso(date_iso)
        self._validate_in_current_week(d)
        self._validate_day_allowed(d)
        self._ensure_not_registered_this_week(user_id, d)
        if not allow_repeat_prev_week:
            self._validate_not_same_weekday_as_prev_week(user_id, d)

        week_day = _WEEKDAY_MAP[d.weekday()]
        logger.debug("Creando registro user_id=%s fecha=%s dia=%s", user_id, date_iso, week_day)
        rec_id = self._records.create_record(user_id, date_iso, week_day)
        logger.info("Registro creado id=%s user_id=%s date=%s day=%s", rec_id, user_id, date_iso, week_day)
        return Record(id=rec_id, user_id=user_id, date=date_iso, week_day=week_day)

    def users_week_status(self, users: List[User], ref_date: Optional[date] = None) -> List[tuple[User, bool]]:
        """Devuelve [(User, registrado_esta_semana)] para pintar en la UI."""
        ref = ref_date or date.today()
        start_iso, end_iso = _week_bounds(ref)
        result: List[tuple[User, bool]] = []
        for u in users:
            flag = self._records.exists_in_week(u.id, start_iso, end_iso) if u.id is not None else False
            result.append((u, flag))
        return result

    def current_week_record(self, user_id: int, ref_date: Optional[date] = None) -> Optional[Record]:
        """Devuelve el Record de la semana actual para `user_id`, o None si no hay.

        Útil para que la UI pueda resaltar el día ya registrado en la semana.
        """
        ref = ref_date or date.today()
        start_iso, end_iso = _week_bounds(ref)
        row = self._records.get_record_in_week(user_id, start_iso, end_iso)
        return Record.from_row(row) if row else None

    def change_week_assignment(self, user_id: int, date_iso: str, allow_repeat_prev_week: bool = False) -> Record:
        """Cambia el registro existente de la semana actual a una nueva fecha válida."""
        urow = self._users.get_by_id(user_id)
        if not urow:
            raise AppError("El usuario no existe.")

        d = _parse_iso(date_iso)
        self._validate_in_current_week(d)
        self._validate_day_allowed(d)
        if not allow_repeat_prev_week:
            self._validate_not_same_weekday_as_prev_week(user_id, d)

        # Buscar el registro actual de la semana
        start_iso, end_iso = _week_bounds(d)
        current = self._records.get_record_in_week(user_id, start_iso, end_iso)
        if current is None:
            raise NoHayRegistroEstaSemana("No hay registro esta semana para cambiar.")

        rec_id, _cur_date, _cur_day = current
        week_day = _WEEKDAY_MAP[d.weekday()]
        self._records.update_record_date_and_day(rec_id, date_iso, week_day)
        logger.info("Registro cambiado id=%s user_id=%s nueva_fecha=%s nuevo_dia=%s", rec_id, user_id, date_iso, week_day)
        return Record(id=rec_id, user_id=user_id, date=date_iso, week_day=week_day)

    # Compatibilidad: método previo usado en algunos puntos
    def validate_repeat_week_day(self, user_id: int, date_iso: str) -> None:
        d = _parse_iso(date_iso)
        self._validate_not_same_weekday_as_prev_week(user_id, d)

    def delete_all_records_by_user(self, user_id: int) -> None:
        """Elimina todos los registros de un usuario."""
        logger.debug("Eliminando todos los registros para user_id=%s", user_id)
        # Primero registros, luego usuario (respeta claves foráneas)
        self._records.delete_all_records_by_user(user_id)
        self._users.delete_user(user_id)
        logger.info("Todos los registros eliminados para user_id=%s", user_id)

    def delete_user_and_records(self, user_id: int) -> None:
        """Elimina los registros de un usuario y luego el usuario (orden correcto)."""
        logger.debug("Eliminando usuario y sus registros user_id=%s", user_id)
        self._records.delete_all_records_by_user(user_id)
        self._users.delete_user(user_id)
        logger.info("Usuario y registros eliminados user_id=%s", user_id)