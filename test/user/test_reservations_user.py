from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.models import Reservation, StatusReservation
from src.domains.resources.models import Resources
from datetime import datetime, timezone


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



# Prueba filtrar las reservas del usuario por su estado
async def test_get_reservations_filter_by_status(user_client: AsyncClient, db_session: AsyncSession):
    resource = Resources(name=
        'Sala Filter', 
        capacity=10
    )
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    
    res1 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title='Test Filter 1',
        start_time=datetime(2026,8,12,10,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,12,12,0,tzinfo=timezone.utc),
    )
    res2 = Reservation(
        user_id=2,
        resource_id=resource.id,
        title='Test Filter 2',
        start_time=datetime(2026,8,12,12,0,tzinfo=timezone.utc),
        end_time=datetime(2026,8,12,14,0,tzinfo=timezone.utc),
        status_reservation=StatusReservation.CANCELLED
    )
    db_session.add_all([res1, res2])
    await db_session.commit()
    
    response = await user_client.get("/reservations/?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1 # Solo hay una reserva pendiente
    assert all(r['status_reservation'] == 'pending' for r in data)


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



# Verifica que un usuario normal no tenga permisos para ver las reservas de todos
async def test_user_cannot_get_all_reservations(user_client: AsyncClient):

    response = await user_client.get("/reservations/all")
    assert response.status_code == 403
