# Servicio para traer todos los usuarios del sistema
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domains.auth.models import User
from sqlalchemy import func

async def get_all_users(
    db: AsyncSession,
    start: int = 0,
    limit: int = 10
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

    result = await db.execute(
        select(User)
        .where(User.role_id != 2)
        .offset(start)
        .limit(limit)
    )

    count_result = await db.execute(
        select(func.count())
        .where(User.role_id != 2)
        .select_from(User)
    )
    
    total_count = count_result.scalar_one()
    users = result.scalars().all()
    return users, total_count