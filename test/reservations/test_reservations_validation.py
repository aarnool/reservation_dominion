from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources

# Prueba aprobar una reserva inexistente
async def test_approve_reservation_not_found(admin_client: AsyncClient):

    response = await admin_client.patch("/reservations/99999/approve")
    assert response.status_code == 404


# Prueba aprobar una reserva ya confirmada
async def test_approve_reservation_already_confirmed(admin_client: AsyncClient, db_session: AsyncSession):
    """Prueba aprobar reserva ya confirmada."""
    resource = Resources(name="Reserva Ya Confirmada", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    reservation = Reservation(
        user_id=1,
        resource_id=resource.id,
        title="Test Ya Confirmada",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc),
        status_reservation=StatusReservation.CONFIRMED
    )
    db_session.add(reservation)
    await db_session.commit()
    await db_session.refresh(reservation)
    
    response = await admin_client.patch(f"/reservations/{reservation.id}/approve")
    assert response.status_code == 409


# Prueba aprobar una reserva cancelada
async def test_approve_reservation_cancelled(admin_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Reserva Cancelada", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    reservation = Reservation(
        user_id=1,
        resource_id=resource.id,
        title="Test Cancelada",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc),
        status_reservation=StatusReservation.CANCELLED
    )
    db_session.add(reservation)
    await db_session.commit()
    await db_session.refresh(reservation)
    
    response = await admin_client.patch(f"/reservations/{reservation.id}/approve")
    assert response.status_code == 409



# Verifica que un usuario no pueda crear una reserva con un recurso que no existe
async def test_create_reservation_invalid_resource(user_client: AsyncClient):
    
    payload = {
        "title": "Mi Reserva",
        "resource_id": 99999,
        "start_time": "2026-08-10T10:00:00Z",
        "end_time": "2026-08-10T12:00:00Z"
    }
    response = await user_client.post("/reservations/", json=payload)
    assert response.status_code == 404


# Verifica que un usuario no pueda crear una reserva con fechas inválidas (inicio después del fin)
async def test_create_reservation_start_after_end(user_client: AsyncClient, db_session: AsyncSession):
   
    resource = Resources(
        name='Sala Error', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    payload = {
        "title": "Reserva Invalida",
        "resource_id": resource.id,
        "start_time": "2026-08-10T12:00:00Z",
        "end_time": "2026-08-10T10:00:00Z"
    }
    response = await user_client.post("/reservations/", json=payload)
    assert response.status_code == 422 # El error lo maneja Pydantic no FastApi


# Verifica que un usuario no pueda actualizar una reserva con fechas inválidas (inicio después del fin)
async def test_update_reservation_start_after_end(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Update Error', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
   
    resp1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Update Time",
        start_time=datetime(2026,8,16,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,16,12,0,tzinfo=timezone.utc),
    )
    db_session.add(resp1)
    await db_session.commit()
    await db_session.refresh(resp1)
    res_id = resp1.id
    
    resp2 = await user_client.patch(f"/reservations/{res_id}", json={
        "start_time": "2026-08-16T14:00:00Z",
        "end_time": "2026-08-16T12:00:00Z"
    })
    assert resp2.status_code == 409


# Verificar que un usuario quiere actualizar una reserva con un recurso que no existe, se devuelva un error 404
async def test_update_reservation_invalid_resource(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Update Invalid', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    response = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Update Invalid",
        start_time=datetime(2026,8,16,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,16,12,0,tzinfo=timezone.utc),
    )
    db_session.add(response)
    await db_session.commit()
    await db_session.refresh(response)
    res_id = response.id
    
    resp2 = await user_client.patch(f"/reservations/{res_id}", json={
        "resource_id": 99999
    })
    assert resp2.status_code == 404


# Verifica que no se pueda cancelar una reserva que ya está cancelada
async def test_cancel_reservation_already_cancelled(user_client: AsyncClient, db_session: AsyncSession):
    
    resource = Resources(
        name='Sala Double Cancel', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    
    resp1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Double Cancel",
        start_time=datetime(2026,8,18,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,18,12,0,tzinfo=timezone.utc),
    )
    db_session.add(resp1)
    await db_session.commit()
    await db_session.refresh(resp1)

    res_id = resp1.id
    
    await user_client.patch(f"/reservations/{res_id}/cancel")
    resp3 = await user_client.patch(f"/reservations/{res_id}/cancel")
    assert resp3.status_code == 409


