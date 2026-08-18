from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Security, status
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
    start: Annotated[
        int, Query(description="Índice de inicio para la paginación", ge=0)
    ] = 0,
    limit: Annotated[
        int,
        Query(description="Número máximo de notificaciones a devolver", ge=1, le=100),
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


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_notification_by_id_endpoint(
    notification_id: Annotated[int, Path(description="ID de la notificación", ge=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["notifications:read"])
    ],
) -> NotificationResponse | None:
    """
    Obtiene una notificación por su ID.

    Args:
        notification_id: ID de la notificación a obtener.
        db: Sesión de la base de datos.
        current_user: Usuario actual.

    Returns:
        La notificación encontrada o None si no existe.
    """
    notification = await service.get_notification_by_id(db, notification_id)
    return notification
