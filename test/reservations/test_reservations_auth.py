from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources


# Verifica que un usuario no pueda actualizar una reserva que le pertenece a otro (Protección IDOR)
async def test_update_reservation_not_own(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(name='Sala Not Own', capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    res = Reservation(
        user_id=999,
        resource_id=resource.id,
        title='Test Not Own',
        start_time=datetime(2026,8,15,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,15,12,0,tzinfo=timezone.utc),
        status_reservation=StatusReservation.PENDING
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)
    
    response = await user_client.patch(f"/reservations/{res.id}", json={"title": "Hacked"})
    assert response.status_code == 404


# Verifica que un usuario normal no tenga permisos para aprobar reservas
async def test_user_cannot_approve_reservation(user_client: AsyncClient, db_session: AsyncSession):

    resource = Resources(
        name='Sala Not Approve', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    res = Reservation(
        user_id=2,
        resource_id=resource.id,
        title='Test Not Approve',
        start_time=datetime(2026,8,19,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,19,12,0,tzinfo=timezone.utc),
        status_reservation=StatusReservation.PENDING
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)
    
    response = await user_client.patch(f"/reservations/{res.id}/approve")
    assert response.status_code == 403


