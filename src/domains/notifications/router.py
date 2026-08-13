from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.domains.notifications import service
from src.domains.notifications.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/", response_model=list[NotificationResponse], status_code=status.HTTP_200_OK
)
async def get_notifications_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["notifications:read"])
    ],
    start: Annotated[int, Query(description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[
        int, Query(description="Número máximo de notificaciones a devolver")
    ] = 10,
) -> list[NotificationResponse]:
    """
    Obtiene todas las notificaciones de un usuario específico.

    Args:
        db: Sesión de la base de datos.
        current_user: Usuario actual.
        start: Índice de inicio para la paginación.
        limit: Número máximo de notificaciones a devolver.

    Returns:
        Una lista de notificaciones del usuario.
    """
    notifications = await service.get_notifications(db, start, limit)
    return notifications
