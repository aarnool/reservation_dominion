from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.resources.models import Resources
from src.domains.reservations.models import Reservation
from datetime import datetime, timezone


# Prueba la creación exitosa de un recurso.
async def test_create_resource_success(admin_client: AsyncClient):

    response = await admin_client.post(
        "/resources/",
        json={"name": "Sala Test", "capacity": 10, "description": "Sala de pruebas"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sala Test"
    assert data["capacity"] == 10



# Prueba crear un recurso duplicado y espera un 409 Conflict. 
async def test_create_resource_duplicate(admin_client: AsyncClient):

    resource_data = {"name": "Sala Duplicada", "capacity": 10}
    await admin_client.post("/resources/", json=resource_data)
    response = await admin_client.post("/resources/", json=resource_data)
    assert response.status_code == 409



# Prueba crear un recurso con capacidad inválida y espera un 422 Unprocessable Entity.
async def test_create_resource_invalid_capacity(admin_client: AsyncClient):

    response = await admin_client.post(
        "/resources/",
        json={"name": "Sala Invalida", "capacity": 0}
    )
    assert response.status_code == 422




# Prueba obtener la lista de recursos como administrador.
async def test_get_resources_success(admin_client: AsyncClient, db_session: AsyncSession):
    resource = Resources(name="Sala Lista", capacity=5)
    db_session.add(resource)
    await db_session.commit()
    
    response = await admin_client.get("/resources/")
    assert response.status_code == 200
    assert len(response.json()) == 1



# Prueba obtener un recurso por su ID como administrador.
async def test_get_resource_by_id_success(admin_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Sala Unica", 
        capacity=5)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    response = await admin_client.get(f"/resources/{resource.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Sala Unica"



# Prueba obtener un recurso inexistente y espera un 404.
async def test_get_resource_by_id_not_found(admin_client: AsyncClient):
   
    response = await admin_client.get("/resources/99999")
    assert response.status_code == 404



# Prueba la actualización de un recurso con éxito.
async def test_update_resource_success(admin_client: AsyncClient, db_session: AsyncSession):
    create_response = Resources(
        name="Sala Update", 
        capacity=10
    )
    db_session.add(create_response)
    await db_session.commit()
    await db_session.refresh(create_response)
    resource_id = create_response.id
    
    update_response = await admin_client.patch(
        f"/resources/{resource_id}",
        json={"capacity": 20}
    )
    assert update_response.status_code == 200
    assert update_response.json()["capacity"] == 20




# Prueba actualizar un recurso inexistente y espera un 404.
async def test_update_resource_not_found(admin_client: AsyncClient):
    
    response = await admin_client.patch("/resources/99999", json={"capacity": 20})
    assert response.status_code == 404




# Prueba actualizar un recurso con un nombre duplicado y espera un 409 Conflict.
async def test_update_resource_duplicate_name(admin_client: AsyncClient, db_session: AsyncSession):
    
    
    res1 = Resources(
        name="Sala A", 
        capacity=10
    )
    db_session.add(res1)
    await db_session.commit()
    await db_session.refresh(res1)

    res2 = Resources(
        name="Sala B", 
        capacity=15
    )
    db_session.add(res2)
    await db_session.commit() 
    await db_session.refresh(res2)
    res2_id = res2.id
    
    response = await admin_client.patch(
        f"/resources/{res2_id}",
        json={"name": "Sala A"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre del recurso ya está en uso por otro recurso."




# Prueba eliminar un recurso con éxito.
async def test_delete_resource_success(admin_client: AsyncClient, db_session: AsyncSession):
    """Prueba eliminar un recurso."""
    create_response = Resources(
        name="Sala Delete", 
        capacity=10
    )
    db_session.add(create_response)
    await db_session.commit()
    await db_session.refresh(create_response)
    resource_id = create_response.id
    
    delete_response = await admin_client.delete(f"/resources/{resource_id}")
    assert delete_response.status_code == 204
    
    get_response = await admin_client.get(f"/resources/{resource_id}")
    assert get_response.status_code == 404




# Prueba eliminar un recurso inexistente y espera un 404.
async def test_delete_resource_not_found(admin_client: AsyncClient):
   
    response = await admin_client.delete("/resources/99999")
    assert response.status_code == 404



# Prueba eliminar un recurso que tiene reservas asociadas y espera un 400 Bad Request.
async def test_delete_resource_with_reservations(admin_client: AsyncClient, db_session: AsyncSession):
    
    resource = Resources(
        name="Sala con Reserva", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    reservation = Reservation(
        user_id=1,
        resource_id=resource.id,
        title="Test",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    )
    db_session.add(reservation)
    await db_session.commit()
    
    response = await admin_client.delete(f"/resources/{resource.id}")
    assert response.status_code == 400
