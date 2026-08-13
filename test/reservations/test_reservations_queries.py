from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources
from src.core.utils import generate_random_reservation_code


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


# Prueba filtrar las reservas por fecha específica
async def test_get_reservations_filter_by_date(
    user_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Date Filter", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    res1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Date 1",
        start_time=datetime(2026, 8, 25, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 25, 12, 0, tzinfo=UTC),
    )
    res2 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Test Date 2",
        start_time=datetime(2026, 8, 26, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 26, 12, 0, tzinfo=UTC),
    )
    db_session.add_all([res1, res2])
    await db_session.commit()

    response = await user_client.get("/reservations/?specific_date=2026-08-25")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Date 1"


# Prueba filtrar las reservas por IDs de recurso
async def test_get_reservations_filter_by_resource_ids(
    user_client: AsyncClient, db_session: AsyncSession
):
    res_a = Resources(name="Sala A Filter", capacity=10)
    res_b = Resources(name="Sala B Filter", capacity=15)
    db_session.add_all([res_a, res_b])
    await db_session.commit()
    await db_session.refresh(res_a)
    await db_session.refresh(res_b)

    reservation1 = Reservation(
        user_id=2,
        resource_id=res_a.id,
        title="Reserva Sala A",
        start_time=datetime(2026, 8, 27, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 27, 12, 0, tzinfo=UTC),
    )
    reservation2 = Reservation(
        user_id=2,
        resource_id=res_b.id,
        title="Reserva Sala B",
        start_time=datetime(2026, 8, 27, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 27, 16, 0, tzinfo=UTC),
    )
    db_session.add_all([reservation1, reservation2])
    await db_session.commit()

    response = await user_client.get(f"/reservations/?resource_ids={res_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resource_id"] == res_a.id


# Prueba filtrar las reservas por código de reserva
async def test_get_reservations_filter_by_code(
    user_client: AsyncClient, db_session: AsyncSession
):
    resource = Resources(name="Sala Code Filter", capacity=10)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)

    code_reservation_filter = generate_random_reservation_code()
    reservation1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Reserva Código 1",
        code_reservation=code_reservation_filter,
        start_time=datetime(2026, 8, 28, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
    )
    code_reservation_no_filter = generate_random_reservation_code()
    reservation2 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title="Reserva Código 2",
        code_reservation=code_reservation_no_filter,
        start_time=datetime(2026, 8, 28, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 28, 16, 0, tzinfo=UTC),
    )
    db_session.add_all([reservation1, reservation2])
    await db_session.commit()

    response = await user_client.get(
        f"/reservations/?code_reservation={code_reservation_filter}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code_reservation"] == code_reservation_filter
