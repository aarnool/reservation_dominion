from httpx import AsyncClient


# Prueba obtener una notificación inexistente y espera 404 Not Found
async def test_get_notification_by_id_not_found(admin_client: AsyncClient):
    response = await admin_client.get("/notifications/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Notificación con ID 99999 no encontrada"


# Prueba obtener notificacion salienose del rango de paginación
async def test_get_notifications_out_of_range(admin_client: AsyncClient):
    response = await admin_client.get("/notifications/?start=0&limit=101")
    assert response.status_code == 422
