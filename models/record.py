from dataclasses import dataclass
from typing import Optional, Tuple

"""Modelo de dominio: registro de día remoto (tabla 'records')."""


@dataclass(frozen=True)
class Record:
    id: Optional[int]
    user_id: int
    date: str       # YYYY-MM-DD
    week_day: str   # Lunes, Martes, ...

    @staticmethod
    def from_row(row: Tuple[int, str, str]) -> "Record":
        """Crea Record desde fila (id, date, week_day) de listados por usuario."""
        rec_id, date, week_day = row
        # user_id no viene en esa consulta, se setea a -1 como placeholder
        return Record(id=rec_id, user_id=-1, date=date, week_day=week_day)

    def to_insert_tuple(self) -> Tuple[int, str, str]:
        """Tupla (user_id, date, week_day) para INSERT."""
        return (self.user_id, self.date, self.week_day)


