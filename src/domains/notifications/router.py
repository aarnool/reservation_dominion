from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.domains.notifications import service
from src.domains.notifications.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


from src.domains.notifications.models import TypeNotification


@router.get(
    "/", response_model=list[NotificationResponse], status_code=status.HTTP_200_OK
)
async def get_notifications_endpoint(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["notifications:read"])
    ],
    is_read: Annotated[
        bool | None, Query(description="Filtro por estado de lectura")
    ] = None,
    type_notification: Annotated[
        TypeNotification | None, Query(description="Filtro por tipo de notificación")
    ] = None,
    user_id: Annotated[
        int | None, Query(description="Filtro por ID de usuario destinatario")
    ] = None,
    start: Annotated[
        int, Query(description="Índice de inicio para la paginación", ge=0)
    ] = 0,
    limit: Annotated[
        int,
        Query(description="Número máximo de notificaciones a devolver", ge=1, le=100),
    ] = 10,
) -> list[NotificationResponse]:
    """
    Obtiene todas las notificaciones de la base de datos con filtrado opcional.

    Args:
        response: Objeto de respuesta HTTP para adjuntar cabeceras.
        db: Sesión de la base de datos.
        current_user: Usuario actual.
        is_read: Estado de lectura opcional.
        type_notification: Tipo de notificación opcional.
        user_id: ID de usuario opcional.
        start: Índice de inicio para la paginación.
        limit: Número máximo de notificaciones a devolver.

    Returns:
        Una lista de notificaciones del usuario.
    """
    notifications, total = await service.get_notifications(
        db=db,
        start=start,
        limit=limit,
        is_read=is_read,
        type_notification=type_notification,
        user_id=user_id,
    )
    response.headers["X-Total-Count"] = str(total)
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
