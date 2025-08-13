from dataclasses import dataclass
from typing import Optional, Tuple

"""Modelo de dominio: usuario (alineado con tabla 'users')."""


@dataclass(frozen=True)
class User:
    id: Optional[int]
    name: str
    docket: str

    @staticmethod
    def from_full_row(row: Tuple[int, str, str]) -> "User":
        """Crea User desde fila (id, name, docket)."""
        user_id, name, docket = row
        return User(id=user_id, name=name, docket=docket)

    @staticmethod
    def from_list_row(row: Tuple[str, str]) -> "User":
        """Crea User desde fila (name, docket) usada en listados sin id."""
        name, docket = row
        return User(id=None, name=name, docket=docket)

    def to_insert_tuple(self) -> Tuple[str, str]:
        """Tupla (name, docket) para INSERT."""
        return (self.name, self.docket)

class User: 
    
    id 
    

    def __init__(self) -> None:
        pass
