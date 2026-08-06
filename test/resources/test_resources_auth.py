from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.resources.models import Resources


# Verifica que un usuario no administrador no pueda crear un recurso (403 Forbidden).
async def test_user_cannot_create_resource(user_client: AsyncClient):

    response = await user_client.post(
        "/resources/", json={"name": "New Res", "capacity": 30}
    )
    assert response.status_code == 403


# Verifica que un usuario no administrador no pueda actualizar un recurso (403 Forbidden).
async def test_user_cannot_update_resource(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Resource User 3", 
        capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    response = await user_client.patch(f"/resources/{resource.id}", json={"capacity": 50})
    assert response.status_code == 403


# Verifica que un usuario no administrador no pueda eliminar un recurso (403 Forbidden).
async def test_user_cannot_delete_resource(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Resource User 4", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    response = await user_client.delete(f"/resources/{resource.id}")
    assert response.status_code == 403


