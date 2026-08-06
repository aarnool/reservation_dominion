from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.domains.auth.schemas import UserResponse
from src.domains.users import service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene todos los usuarios del sistema (SOLO ADMINISTRADOR 🚫)",
)
async def get_all_users(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["users:read"])],
    start: Annotated[
        int, Query(description="Índice de inicio para la paginación", ge=0)
    ] = 0,
    limit: Annotated[
        int, Query(description="Número máximo de usuarios a devolver", ge=1)
    ] = 10,
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Obtiene todos los usuarios registrados en el sistema.
    ### Detalles:
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0).
    - **limit**: Número máximo de usuarios a devolver (opcional, por defecto 10).

    """
    users, total = await service.get_all_users(db=db, start=start, limit=limit)

    response.headers["X-Total-Count"] = str(total)
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtiene un usuario por su ID (SOLO ADMINISTRADOR 🚫)",
)
async def get_user_by_id(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["users:read"])],
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Obtiene un usuario por su ID.
    ### Detalles:
    - **user_id**: ID del usuario a buscar.

    """
    return await service.get_user_by_id(db=db, user_id=user_id)
