from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources


# Prueba la paginación al obtener todas las reservas
async def test_get_all_reservations_pagination(
    admin_client: AsyncClient, db_session: AsyncSession
):

    resource = Resources(name="Reserva Paginacion", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    for i in range(15):
        reservation = Reservation(
            user_id=1,
            resource_id=resource.id,
            title=f"Test Pagina {i}",
            start_time=datetime(2026, 8, 10, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 8, 10, 12, 0, tzinfo=UTC),
        )
        db_session.add(reservation)
    await db_session.commit()

    res1 = await admin_client.get("/reservations/?start=10&limit=10")
    assert res1.status_code == 200
    assert len(res1.json()) == 5


# Prueba filtrar las reservas del usuario por su estado
async def test_get_reservations_filter_by_status(
    user_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Filter", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Filter 1",
        start_time=datetime(2026, 8, 12, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 12, 12, 0, tzinfo=UTC),
    )
    res2 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Filter 2",
        start_time=datetime(2026, 8, 12, 12, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 12, 14, 0, tzinfo=UTC),
        status_reservation=StatusReservation.CANCELLED,
    )
    db_session.add_all([res1, res2])
    await db_session.commit()

    response = await user_client.get("/reservations/?status_reservation=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Solo hay una reserva pendiente
    assert all(r["status_reservation"] == "pending" for r in data)
