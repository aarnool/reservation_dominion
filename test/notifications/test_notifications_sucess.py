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
