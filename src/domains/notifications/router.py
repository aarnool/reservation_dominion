from fastapi import APIRouter, Depends, Body, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.notifications.schemas import NotificationCreate, NotificationResponse
from src.dependencies import get_db
from src.domains.notifications import service


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    notification: Annotated[NotificationCreate, Body()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Crea una nueva notificación.

    Args:
        notification: Datos de la notificación a crear.
        db: Sesión de la base de datos.

    Returns:
        La notificación creada.
    """
    # Aquí deberías llamar a tu servicio para crear la notificación en la base de datos
    # Por ejemplo:
    # new_notification = await create_notification_service(notification)
    # return new_notification

    return await service.create_notification(db, notification)
