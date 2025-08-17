"""Servicio de usuarios: orquesta reglas y acceso al repositorio."""

import logging
from typing import List, Optional

from data.user_repo import UserRepository
from models.user import User

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository | None = None) -> None:
        self._repo = user_repo or UserRepository

    def create_user(self, name: str, docket: str) -> User:
        """Crea un usuario y devuelve el modelo User."""
        logger.debug("Creando usuario name=%s docket=%s", name, docket)
        user_id = self._repo.create(name, docket)
        return User(id=user_id, name=name, docket=docket)

    def list_users(self) -> List[User]:
        """Lista todos los usuarios como modelos User."""
        rows = self._repo.list_all()
        return [User.from_full_row(row) for row in rows]

    def get_user(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por id, o None si no existe."""
        row = self._repo.get_by_id(user_id)
        return User.from_full_row(row) if row else None

    def update_user(self, user_id: int, name: str, docket: str) -> None:
        """Actualiza nombre/docket del usuario."""
        logger.debug("Actualizando usuario id=%s name=%s docket=%s", user_id, name, docket)
        self._repo.update(user_id, name, docket)

    def delete_user(self, user_id: int) -> None:
        """Elimina un usuario por id."""
        logger.debug("Eliminando usuario id=%s", user_id)
        self._repo.delete(user_id)