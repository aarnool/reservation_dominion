from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.notifications.models import Notification


# Prueba para obtener todas las notificaciones y espera un código de estado 200 OK
async def test_get_all_notifications(
    admin_client: AsyncClient, db_session: AsyncSession
):
    notification = Notification(
        type_notification="info",
        message="Este es un mensaje de prueba",
        user_id=1,
    )
    db_session.add(notification)
    await db_session.commit()

    response = await admin_client.get("/notifications/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_notification_by_id(
    admin_client: AsyncClient, db_session: AsyncSession
):
    notification = Notification(
        type_notification="info",
        message="Este es un mensaje de prueba",
        user_id=1,
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)

    response = await admin_client.get(f"/notifications/{notification.id}")
    assert response.status_code == 200
    assert response.json()["id"] == notification.id


# Prueba para filtrar notificaciones por estado de lectura (is_read)
async def test_filter_notifications_by_is_read(
    admin_client: AsyncClient, db_session: AsyncSession
):
    notif_unread = Notification(
        type_notification="info", message="No leída", is_read=False, user_id=1
    )
    notif_read = Notification(
        type_notification="info", message="Leída", is_read=True, user_id=1
    )
    db_session.add_all([notif_unread, notif_read])
    await db_session.commit()

    response = await admin_client.get("/notifications/?is_read=false")
    assert response.status_code == 200
    messages = [n["message"] for n in response.json()]
    assert "No leída" in messages
    assert "Leída" not in messages


# Prueba para filtrar notificaciones por tipo de notificación
async def test_filter_notifications_by_type(
    admin_client: AsyncClient, db_session: AsyncSession
):
    notif_res = Notification(
        type_notification="reservation", message="Notif Reserva", user_id=1
    )
    notif_acc = Notification(
        type_notification="account", message="Notif Cuenta", user_id=1
    )
    db_session.add_all([notif_res, notif_acc])
    await db_session.commit()

    response = await admin_client.get("/notifications/?type_notification=reservation")
    assert response.status_code == 200
    messages = [n["message"] for n in response.json()]
    assert "Notif Reserva" in messages
    assert "Notif Cuenta" not in messages
