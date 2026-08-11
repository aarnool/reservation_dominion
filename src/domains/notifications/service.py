from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.notifications.models import Notification
from src.domains.notifications.schemas import NotificationCreate


async def create_notification(
    db: AsyncSession, notification: NotificationCreate
) -> Notification:
    """
    Crea una nueva notificación en la base de datos.

    Args:
        db: Sesión de la base de datos.
        notification: Datos de la notificación a crear.

    Returns:
        La notificación creada.
    """
    new_notification = Notification(
        message=notification.message,
        type_notification=notification.type_notification,
        is_read=notification.is_read,
        user_id=notification.user_id,
        reservation_id=notification.reservation_id,
    )
    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification
