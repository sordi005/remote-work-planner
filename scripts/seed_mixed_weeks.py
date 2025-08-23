"""Crea 10 empleados y siembra registros divididos:

- E01..E05: 1 registro en la semana pasada (Martes..Sábado)
- E06..E10: 1 registro hace dos semanas (Martes..Sábado)

Nadie tiene registro esta semana.

Uso:
    python scripts/seed_mixed_weeks.py
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys

# Habilitar imports del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.user_repo import UserRepository
from data.assignament_repo import RecordRespository
from data.db_utils import get_connection

WEEKDAYS = [1, 2, 3, 4, 5]  # Martes..Sábado (evitamos lunes=0 y domingo=6)
WEEKDAY_NAME = {1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado"}


def week_start(ref: date) -> date:
    return ref - timedelta(days=ref.weekday())


def date_for_week_and_weekday(weeks_ago: int, weekday_num: int) -> date:
    today = date.today()
    start_this = week_start(today)
    target_start = start_this - timedelta(days=7 * weeks_ago)
    return target_start + timedelta(days=weekday_num)


def ensure_clean_prefix(prefix: str = "EMP-") -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE user_id IN (SELECT id FROM users WHERE docket LIKE ?)", (f"{prefix}%",))
        cur.execute("DELETE FROM users WHERE docket LIKE ?", (f"{prefix}%",))
        conn.commit()


def main() -> None:
    ensure_clean_prefix()

    # Crear 10 empleados EMP-01..EMP-10
    user_ids: list[int] = []
    for i in range(1, 11):
        name = f"Empleado {i:02d}"
        docket = f"EMP-{i:02d}"
        uid = UserRepository.create(name, docket)
        assert uid is not None
        user_ids.append(int(uid))

    # E01..E05 => semana pasada (weeks_ago=1)
    for idx, uid in enumerate(user_ids[:5], start=0):
        weekday_num = WEEKDAYS[idx % len(WEEKDAYS)]
        d = date_for_week_and_weekday(1, weekday_num)
        RecordRespository.create_record(uid, d.isoformat(), WEEKDAY_NAME[weekday_num])

    # E06..E10 => hace dos semanas (weeks_ago=2)
    for idx, uid in enumerate(user_ids[5:], start=0):
        weekday_num = WEEKDAYS[idx % len(WEEKDAYS)]
        d = date_for_week_and_weekday(2, weekday_num)
        RecordRespository.create_record(uid, d.isoformat(), WEEKDAY_NAME[weekday_num])

    print("Seed completado: 5 con semana pasada, 5 con hace dos semanas. Semana actual sin registros.")


if __name__ == "__main__":
    main()


