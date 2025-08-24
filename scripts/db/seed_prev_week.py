"""Inserta un registro en la semana pasada para probar la validación de 'no repetir día'.

Uso:
    python scripts/seed_prev_week.py --user-id 1 --weekday jueves

Si el usuario no existe, muestra un mensaje de error. Si el registro ya existe, lo ignora.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
import sys

# Habilitar imports del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.assignament_repo import RecordRespository
from data.user_repo import UserRepository
from data.db_utils import get_connection

_WEEKDAY_NAME = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
}

_NAME_TO_NUM = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
}


def target_date_for_prev_week(weekday_num: int) -> date:
    today = date.today()
    start = today - timedelta(days=today.weekday())  # lunes esta semana
    target_this_week = start + timedelta(days=weekday_num)
    return target_this_week - timedelta(days=7)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int, required=True, help="ID del usuario existente")
    parser.add_argument(
        "--weekday", type=str, required=True, choices=list(_NAME_TO_NUM.keys()),
        help="Día de la semana a registrar en la semana pasada (minusculas, ej: jueves)",
    )
    args = parser.parse_args()

    user_id = args.user_id
    weekday_num = _NAME_TO_NUM[args.weekday.lower()]
    dt = target_date_for_prev_week(weekday_num)
    date_iso = dt.isoformat()
    week_day_name = _WEEKDAY_NAME[weekday_num]

    # Verificar usuario
    row = UserRepository.get_by_id(user_id)
    if not row:
        print(f"Usuario id={user_id} no existe")
        sys.exit(1)

    # Insertar registro si no existe
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM records WHERE user_id = ? AND date = ?)",
            (user_id, date_iso),
        )
        if cur.fetchone()[0]:
            print(f"Ya existe un registro para user_id={user_id} en {date_iso}")
            return

    try:
        RecordRespository.create_record(user_id, date_iso, week_day_name)
        print(f"Registro creado para user_id={user_id} fecha={date_iso} dia={week_day_name}")
    except Exception as e:
        print(f"No se pudo crear el registro: {e}")


if __name__ == "__main__":
    main()


