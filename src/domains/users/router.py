from fastapi import APIRouter, Depends, Response, Security, Query, status
from src.domains.auth.schemas import UserResponse
from src.dependencies import get_db, get_current_user
from src.domains.users import service
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene todos los usuarios del sistema"
)
async def get_all_users(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["users:read"])],
    start: Annotated[int, Query(
        description="Índice de inicio para la paginación", ge=0)] = 0,
    limit: Annotated[int, Query(
        description="Número máximo de usuarios a devolver", ge=1)] = 10
):
    """

    Obtiene todos los usuarios registrados en el sistema.
    ### Detalles:
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0).
    - **limit**: Número máximo de usuarios a devolver (opcional, por defecto 10).
    
    """
    users, total = await service.get_all_users(
        db=db,
        start=start,
        limit=limit
    )

    response.headers["X-Total-Count"] = str(total)
    return users