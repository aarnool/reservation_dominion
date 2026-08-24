# Servicio para traer todos los usuarios del sistema
import uuid
from collections.abc import Sequence

from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config import settings
from src.core.utils import get_r2_client
from src.domains.auth.models import User
from src.domains.auth.schemas import UserUpdate


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
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )

    return user


# Servicio para actualizar el perfil del usuario
async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
    avatar: UploadFile | None = None,
) -> User:
    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )

    if user_update.first_name is not None:
        assert user is not None
        user.first_name = user_update.first_name
    if user_update.last_name is not None and user is not None:
        user.last_name = user_update.last_name

    if avatar is not None and avatar.filename:
        file_extencion = (
            avatar.filename.split(".")[-1] if "." in avatar.filename else "png"
        )
        unique_filename = f"{uuid.uuid4()}.{file_extencion}"

        try:
            get_r2_client().upload_fileobj(
                avatar.file,
                settings.R2_BUCKET_AVATAR,
                unique_filename,
                ExtraArgs={"ContentType": avatar.content_type},
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir el avatar: {e}",
            )
        finally:
            avatar.file.close()

        assert user is not None
        user.avatar_url = f"{unique_filename}"

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
