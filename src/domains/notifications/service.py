from fastapi import HTTPException, status
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


from src.domains.notifications.models import Notification, TypeNotification
from src.domains.notifications.schemas import NotificationCreate, NotificationResponse


async def get_notifications(
    db: AsyncSession,
    start: int = 0,
    limit: int = 10,
    is_read: bool | None = None,
    type_notification: TypeNotification | None = None,
    user_id: int | None = None,
) -> tuple[list[NotificationResponse], int]:
    """
    Obtiene todas las notificaciones de la base de datos con filtros opcionales.

    Args:
        db: Sesión de la base de datos.
        start: Índice de inicio para la paginación.
        limit: Número máximo de notificaciones a devolver.
        is_read: Filtro por estado de lectura (opcional).
        type_notification: Filtro por tipo de notificación (opcional).
        user_id: Filtro por ID de usuario destinatario (opcional).

    Returns:
        Tupla con lista de notificaciones y el conteo total.
    """
    from sqlalchemy import func

    query = select(Notification)

    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    if type_notification is not None:
        query = query.where(Notification.type_notification == type_notification)
    if user_id is not None:
        query = query.where(Notification.user_id == user_id)

    # Conteo total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Ejecutar paginación
    result = await db.execute(query.offset(start).limit(limit))
    notifications = result.scalars().all()
    return notifications, total  # type: ignore


async def get_notification_by_id(
    db: AsyncSession, notification_id: int
) -> NotificationResponse | None:
    """
    Obtiene una notificación por su ID.

    Args:
        db: Sesión de la base de datos.
        notification_id: ID de la notificación a obtener.

    Returns:
        La notificación encontrada o None si no existe.
    """
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notificación con ID {notification_id} no encontrada",
        )
    return notification  # type: ignore
