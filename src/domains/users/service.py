# Servicio para traer todos los usuarios del sistema
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domains.auth.models import User


# Servicio para obtener todos los usuarios registrados en el sistema
async def get_all_users(
    db: AsyncSession, start: int = 0, limit: int = 10
) -> tuple[Sequence[User], int]:
    """
    Obtiene todos los usuarios registrados en el sistema.
    Args:
        db (AsyncSession): Sesión de base de datos asíncrona.
        start (int): Índice de inicio para la paginación (opcional, por defecto 0).
        limit (int): Número máximo de usuarios a devolver (opcional, por defecto 10).
    Returns:
        Sequence[User]: Lista de usuarios obtenidos de la base de datos.
    """

    result = await db.execute(select(User).offset(start).limit(limit))

    count_result = await db.execute(select(func.count()).select_from(User))

    total_count = count_result.scalar_one()
    users = result.scalars().all()
    return users, total_count


# Servicio para obtener un usuario por su ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Obtiene un usuario por su ID.
    Args:
        db (AsyncSession): Sesión de base de datos asíncrona.
        user_id (int): ID del usuario a buscar.
    Returns:
        User | None: Usuario encontrado o None si no existe.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )

    return result.scalar_one_or_none()
