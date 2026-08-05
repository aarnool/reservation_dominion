from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.resources.models import Resources
from src.domains.reservations.models import Reservation, StatusReservation
from datetime import datetime, timezone


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



# Prueba la paginación al obtener todas las reservas
async def test_get_all_reservations_pagination(admin_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name="Reserva Paginacion", 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    for i in range(15):
        reservation = Reservation(
            user_id=1,
            resource_id=resource.id,
            title=f"Test Pagina {i}",
            start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
        )
        db_session.add(reservation)
    await db_session.commit()
    
    res1 = await admin_client.get("/reservations/?start=10&limit=10")
    assert res1.status_code == 200
    assert len(res1.json()) == 5
    


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
