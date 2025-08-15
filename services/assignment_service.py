"""Servicio de asignaciones: reglas de negocio para días remotos."""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from data.repository import RecordRespository, UserRepository
from models.record import Record
from models.user import User
from exceptions import AppError

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
        """True si el usuario tiene un registro en la semana de ref_date (por defecto hoy)."""
        ref = ref_date or date.today()
        start_iso, end_iso = _week_bounds(ref)
        logger.debug("is_registered_this_week user_id=%s start=%s end=%s", user_id, start_iso, end_iso)
        return self._records.exists_in_week(user_id, start_iso, end_iso)

    def latest_for_user(self, user_id: int) -> Optional[Record]:
        """Último registro del usuario o None."""
        row = self._records.get_latest_record(user_id)
        return Record.from_row(row) if row else None

    def list_by_user(self, user_id: int) -> List[Record]:
        """Lista registros del usuario como modelos Record (ordenados por fecha desc)."""
        rows = self._records.list_by_user(user_id)
        return [Record.from_row(r) for r in rows]

    def assign_day(self, user_id: int, date_iso: str) -> Record:
        """Asigna fecha a usuario aplicando regla: no repetir el mismo día que la semana anterior."""
        # Validaciones básicas
        urow = self._users.get_by_id(user_id)
        if not urow:
            raise AppError("El usuario no existe.")

        d = _parse_iso(date_iso)
        week_day = _WEEKDAY_MAP[d.weekday()]

        # Regla: no repetir el mismo día que la semana anterior
        prev_week_day = d - timedelta(days=7)
        prev_start, prev_end = _week_bounds(prev_week_day)
        prev = self._records.get_record_in_week(user_id, prev_start, prev_end)
        if prev is not None:
            _prev_id, _prev_date, prev_week_day_name = prev
            if prev_week_day_name == week_day:
                logger.debug(
                    "Regla violada user_id=%s date=%s week_day=%s prev_week=(%s..%s) prev_day=%s",
                    user_id, date_iso, week_day, prev_start, prev_end, prev_week_day_name,
                )
                raise AppError("No puede repetir el mismo día que la semana anterior.")

        # Crear registro
        logger.debug("Creando registro user_id=%s date=%s week_day=%s", user_id, date_iso, week_day)
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


