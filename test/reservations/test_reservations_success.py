from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources


# Prueba obtener todas las reservas como administrador
async def test_get_all_reservations_success(admin_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Reserva Admin Test", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    reservation = Reservation(
        user_id=1,
        resource_id=resource.id,
        title="Admin Test",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc),
        status_reservation=StatusReservation.PENDING
    )
    db_session.add(reservation)
    await db_session.commit()
    
    response = await admin_client.get("/reservations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# Prueba aprobar una reserva con exito
async def test_approve_reservation_success(admin_client: AsyncClient, db_session: AsyncSession):
    """Prueba aprobar una reserva."""
    resource = Resources(
        name="Reserva Aprobar", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    reservation = Reservation(
        user_id=1,
        resource_id=resource.id,
        title="Test Aprobar",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
    )
    db_session.add(reservation)
    await db_session.commit()
    await db_session.refresh(reservation)
    
    response = await admin_client.patch(f"/reservations/{reservation.id}/approve")
    assert response.status_code == 200
    assert response.json()["status_reservation"] == "confirmed"


# Prueba que un usuario pueda crear exitosamente una reserva
async def test_create_reservation_success(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Test', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    payload = {
        "title": "Mi Reserva",
        "resource_id": resource.id,
        "start_time": "2026-08-10T10:00:00Z",
        "end_time": "2026-08-10T12:00:00Z"
    }
    response = await user_client.post("/reservations/", json=payload)
    assert response.status_code == 201


# Prueba obtener las reservas del usuario autenticado
async def test_get_reservations_success(user_client: AsyncClient, db_session: AsyncSession):
    """Prueba obtener las reservas del usuario autenticado."""
    resource = Resources(name='Sala List', capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    res = Reservation(
        user_id=2,
        resource_id=resource.id,
        title='Test List',
        start_time=datetime(2026,8,10,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,10,12,0,tzinfo=timezone.utc),
    )
    db_session.add(res)
    await db_session.commit()
    
    response = await user_client.get("/reservations/")
    assert response.status_code == 200


# Prueba actualizar una reserva propia con exito
async def test_update_reservation_success(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Update', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
   
    response = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Update",
        start_time=datetime(2026,8,14,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,14,12,0,tzinfo=timezone.utc),
    )
    db_session.add(response)
    await db_session.commit()
    await db_session.refresh(response)
    res_id = response.id
    
    resp2 = await user_client.patch(f"/reservations/{res_id}", json={"title": "Titulo Actualizado"})
    assert resp2.status_code == 200
    assert resp2.json()["title"] == "Titulo Actualizado"


# Verifica que un usuario pueda cancelar una reserva propia con éxito
async def test_cancel_reservation_success(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Cancel', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    resp1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Cancel",
        start_time=datetime(2026,8,17,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,17,12,0,tzinfo=timezone.utc),
    )
    db_session.add(resp1)
    await db_session.commit()
    await db_session.refresh(resp1)
    res_id = resp1.id
    
    resp2 = await user_client.patch(f"/reservations/{res_id}/cancel")
    assert resp2.status_code == 200
    assert resp2.json()["status_reservation"] == "cancelled"


