from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.resources.models import Resources


# Prueba la creación exitosa de un recurso.
async def test_create_resource_success(admin_client: AsyncClient):

    response = await admin_client.post(
        "/resources/",
        json={"name": "Sala Test", "capacity": 10, "description": "Sala de pruebas"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sala Test"
    assert data["capacity"] == 10


# Prueba obtener la lista de recursos.
async def test_get_resources_success(
    admin_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Lista", capacity=5)
    db_session.add(resource)
    await db_session.commit()

    response = await admin_client.get("/resources/")
    assert response.status_code == 200
    assert len(response.json()) == 1


# Prueba obtener un recurso por su ID.
async def test_get_resource_by_id_success(
    admin_client: AsyncClient, db_session: AsyncSession
):

    resource = Resources(name="Sala Unica", capacity=5)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    response = await admin_client.get(f"/resources/{resource.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Sala Unica"


# Prueba la actualización de un recurso con éxito.
async def test_update_resource_success(
    admin_client: AsyncClient, db_session: AsyncSession
):
    create_response = Resources(name="Sala Update", capacity=10)
    db_session.add(create_response)
    await db_session.commit()
    await db_session.refresh(create_response)
    resource_id = create_response.id

    update_response = await admin_client.patch(
        f"/resources/{resource_id}", json={"capacity": 20}
    )
    assert update_response.status_code == 200
    assert update_response.json()["capacity"] == 20


# Prueba eliminar un recurso con éxito.
async def test_delete_resource_success(
    admin_client: AsyncClient, db_session: AsyncSession
):
    """Prueba eliminar un recurso."""
    create_response = Resources(name="Sala Delete", capacity=10)
    db_session.add(create_response)
    await db_session.commit()
    await db_session.refresh(create_response)
    resource_id = create_response.id

    delete_response = await admin_client.delete(f"/resources/{resource_id}")
    assert delete_response.status_code == 204

    get_response = await admin_client.get(f"/resources/{resource_id}")
    assert get_response.status_code == 404


# Prueba obtener la lista de recursos como usuario normal
async def test_user_get_resources_success(
    user_client: AsyncClient, db_session: AsyncSession
):

    resource = Resources(name="Resource User 1", capacity=10)
    db_session.add(resource)
    await db_session.commit()

    response = await user_client.get("/resources/")
    assert response.status_code == 200


# Prueba filtrado dinámico de recursos por capacidad mínima
async def test_get_resources_filter_min_capacity(
    admin_client: AsyncClient, db_session: AsyncSession
):
    res_small = Resources(name="Pequeña Sala", capacity=5)
    res_large = Resources(name="Gran Auditorio", capacity=50)
    db_session.add_all([res_small, res_large])
    await db_session.commit()

    response = await admin_client.get("/resources/?min_capacity=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Gran Auditorio"
    assert data[0]["capacity"] == 50


# Prueba filtrado dinámico de recursos por disponibilidad en rango horario
async def test_get_resources_filter_availability_slot(
    admin_client: AsyncClient, db_session: AsyncSession
):
    from datetime import datetime, timezone
    from src.domains.reservations.models import Reservation, StatusReservation

    res_busy = Resources(name="Sala Ocupada", capacity=10)
    res_free = Resources(name="Sala Libre", capacity=15)
    db_session.add_all([res_busy, res_free])
    await db_session.commit()
    await db_session.refresh(res_busy)

    # Crear una reserva dinámica para res_busy
    now = datetime.now(timezone.utc)
    start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end = now.replace(hour=12, minute=0, second=0, microsecond=0)

    resv = Reservation(
        user_id=1,
        resource_id=res_busy.id,
        title="Reserva Conferencia",
        start_time=start,
        end_time=end,
        status_reservation=StatusReservation.CONFIRMED,
    )
    db_session.add(resv)
    await db_session.commit()

    # Consulta durante el horario ocupado (10:30 a 11:30)
    search_start = start.replace(minute=30).strftime("%Y-%m-%dT%H:%M:%SZ")
    search_end = start.replace(hour=11, minute=30).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = await admin_client.get(
        f"/resources/?start_time={search_start}&end_time={search_end}"
    )
    assert response.status_code == 200
    data = response.json()

    # Solo debe retornar la sala libre
    resource_names = [r["name"] for r in data]
    assert "Sala Libre" in resource_names
    assert "Sala Ocupada" not in resource_names
