from httpx import AsyncClient


# Prueba de ver las notificaciones sin los permisos necesarios y espera un código de estado 403 Forbidden
async def test_get_notifications_without_permissions(
    user_client: AsyncClient,
):
    response = await user_client.get("/notifications/")
    assert response.status_code == 403
