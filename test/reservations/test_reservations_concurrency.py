from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources


# Verifica que no se puedan crear dos reservas en el mismo rango de tiempo para el mismo recurso
async def test_create_reservation_conflict(user_client: AsyncClient, db_session: AsyncSession):
    
    resource = Resources(
        name='Sala Conflict', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    payload = {
        "title": "Reserva 1",
        "resource_id": resource.id,
        "start_time": "2026-08-11T10:00:00Z",
        "end_time": "2026-08-11T12:00:00Z"
    }
    resp1 = await user_client.post("/reservations/", json=payload)
    assert resp1.status_code == 201
    
    payload["title"] = "Reserva 2"
    resp2 = await user_client.post("/reservations/", json=payload)
    assert resp2.status_code == 409


