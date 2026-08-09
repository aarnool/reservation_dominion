from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources


# Verifica que un usuario no pueda actualizar una reserva que le pertenece a otro (Protección IDOR)
async def test_update_reservation_not_own(
    user_client: AsyncClient, db_session: AsyncSession
):

    resource = Resources(name="Sala Not Own", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res = Reservation(
        user_id=999,
        resource_id=resource.id,
        title="Test Not Own",
        start_time=datetime(2026, 8, 15, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 15, 12, 0, tzinfo=UTC),
        status_reservation=StatusReservation.PENDING,
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)

    response = await user_client.patch(
        f"/reservations/{res.id}", json={"title": "Hacked"}
    )
    assert response.status_code == 404


# Verifica que un usuario normal no tenga permisos para aprobar reservas
async def test_user_cannot_approve_reservation(
    user_client: AsyncClient, db_session: AsyncSession
):

    resource = Resources(name="Sala Not Approve", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Not Approve",
        start_time=datetime(2026, 8, 19, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 19, 12, 0, tzinfo=UTC),
        status_reservation=StatusReservation.PENDING,
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)

    response = await user_client.patch(f"/reservations/{res.id}/approve")
    assert response.status_code == 403


# Verifica que un usuario no pueda obtener una reserva que le pertenece a otro (Protección IDOR -> 404)
async def test_get_reservation_by_id_not_own_idor(
    user_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Get IDOR", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res = Reservation(
        user_id=999,  # No le pertenece al user_client (id 2)
        resource_id=resource.id,
        title="Test Get IDOR",
        start_time=datetime(2026, 8, 22, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 22, 12, 0, tzinfo=UTC),
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)

    response = await user_client.get(f"/reservations/{res.id}")
    assert response.status_code == 404


# Verifica que un usuario no pueda cancelar una reserva que le pertenece a otro (Protección IDOR -> 404)
async def test_cancel_reservation_not_own_idor(
    user_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Cancel IDOR", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res = Reservation(
        user_id=999,  # No le pertenece al user_client (id 2)
        resource_id=resource.id,
        title="Test Cancel IDOR",
        start_time=datetime(2026, 8, 23, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 23, 12, 0, tzinfo=UTC),
    )
    db_session.add(res)
    await db_session.commit()
    await db_session.refresh(res)

    response = await user_client.patch(f"/reservations/{res.id}/cancel")
    assert response.status_code == 404

