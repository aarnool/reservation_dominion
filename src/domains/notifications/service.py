from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.models import User
from src.domains.notifications.models import Notification
from src.domains.notifications.schemas import NotificationCreate, NotificationResponse


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


async def create_notifications_by_admins(db: AsyncSession, reservation_id: int) -> None:
    """
    Crea notificaciones para todos los administradores.

    Args:
        db: Sesión de la base de datos.
        reservation_id: ID de la reserva para la cual se crean las notificaciones.
    Returns:
        None.
    """
    # Obtiene todos los usuarios con el rol de administrador (role_id = 2)
    result = await db.execute(select(User).where(User.role_id == 2))
    admins_list = result.scalars().all()

    for admin in admins_list:
        new_notification = Notification(
            message=f"Se ha creado una nueva reserva con ID {reservation_id}",
            type_notification="reservation",
            is_read=False,
            user_id=admin.id,
            reservation_id=reservation_id,
        )
        db.add(new_notification)
        await db.commit()
        await db.refresh(new_notification)


async def get_notifications(
    db: AsyncSession, start: int, limit: int
) -> list[NotificationResponse]:
    """
    Obtiene todas las notificaciones de la base de datos.

    Args:
        db: Sesión de la base de datos.
        start: Índice de inicio para la paginación.
        limit: Número máximo de notificaciones a devolver.

    Returns:
        Lista de notificaciones.
    """
    result = await db.execute(select(Notification).offset(start).limit(limit))
    notifications = result.scalars().all()
    return notifications  # type: ignore
