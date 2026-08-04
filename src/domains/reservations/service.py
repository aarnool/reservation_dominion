from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, Date
from src.domains.reservations.models import Reservation
from src.domains.resources.models import Resources
from src.domains.reservations.schemas import ReservationCreate, StatusReservation, ReservationUpdate
from typing import Sequence, List
from datetime import date, datetime, time, timezone


# Servicio para obtener una lista de reservas desde la base de datos con filtros opcionales y paginación
async def get_reservations(
    user_id: int,
    db: AsyncSession,
    status_filter: StatusReservation | None = None,
    filter_date: date | None = None,
    resource_ids: List[int] | None = None,
    resource_name: str | None = None,
    start: int = 0,
    limit: int = 10
) -> Sequence[Reservation]:
    """

    Obtiene una lista de reservas desde la base de datos, con la posibilidad de filtrar por estado, fecha y recurso, incluyendo paginación para un usuario específico.
    Args:
        user_id (int): ID del usuario autenticado.
        db (AsyncSession): Sesión de base de datos asincrónica.
        status_filter (StatusReservation | None): Filtro opcional por estado de la reserva.
        filter_date (date | None): Filtro opcional por fecha exacta de la reserva.
        resource_ids (List[int] | None): Filtro opcional por múltiples identificadores de recurso.
        resource_name (str | None): Filtro opcional por nombre del recurso asociado (búsqueda parcial).
        start (int): Índice inicial para la paginación (por defecto es 0).
        limit (int): Número máximo de reservas a devolver (por defecto es 10).
    Returns:
        Sequence[Reservation]: Una lista de objetos Reservation que representan las reservas obtenidas.

    """

    query = select(Reservation).where(Reservation.user_id == user_id)

    if status_filter is not None:
        query = query.where(Reservation.status_reservation == status_filter)
    
    if filter_date is not None:
      
        # Convertimos la fecha a un rango de tiempo para filtrar las reservas que ocurren en ese día específico
        start_of_day = datetime.combine(filter_date, time.min).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(filter_date, time.max).replace(tzinfo=timezone.utc)
        
        query = query.where(
            Reservation.start_time >= start_of_day,
            Reservation.start_time <= end_of_day
        )
    
    if resource_ids is not None:
        query = query.where(Reservation.resource_id.in_(resource_ids))

    if resource_name is not None:
        query = query.join(Resources).where(Resources.name.ilike(f"%{resource_name}%"))

    query = query.offset(start).limit(limit)
    
    result = await db.execute(query)
    reservations = result.scalars().all()

    return reservations


# Servicio para crear una reserva en la base de datos
async def create_reservation(
    user_id: int,
    reservation: ReservationCreate,
    db: AsyncSession
) -> Reservation:
    """

    Crea una nueva reserva en el sistema.
    Args:
        user_id (int): ID del usuario que crea la reserva.
        reservation (ReservationCreate): Datos de la reserva a crear.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Returns:
        Reservation: Objeto de la reserva creada.

    """
    
    resource = await db.get(Resources, reservation.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El recurso especificado no existe"
        )

    new_reservation = Reservation(
        user_id=user_id,
        resource_id=reservation.resource_id,
        title=reservation.title,
        description=reservation.description,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
    )

    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)

    return new_reservation

# Servicio para actualizar una reserva existente en la base de datos
async def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    db: AsyncSession
) -> Reservation:
    """

    Actualiza una reserva existente en la base de datos.
    Args:
        reservation_id (int): ID de la reserva a actualizar.
        reservation_update (ReservationUpdate): Datos de la reserva a actualizar.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si la reserva no existe.
    Returns:
        Reservation: Objeto de la reserva actualizada.

    """

    smtm = select(Reservation).where(Reservation.id == reservation_id) # Verificar si la reserva existe en la base de datos
    result = await db.execute(smtm)
    reservation = result.scalar_one_or_none()

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )

    # Actualizar los campos proporcionados en la solicitud
    reservation_update_data = reservation_update.model_dump(exclude_unset=True)
    for key, value in reservation_update_data.items():
        setattr(reservation, key, value)

    await db.commit()
    await db.refresh(reservation)

    return reservation
    



# Servicio para actualizar el estado de una reserva existente a confirmada
async def approve_reservation(
    reservation_id: int,
    db: AsyncSession
) -> Reservation:
    """

    Actualiza una reserva existente en la base de datos, cambiando su estado a confirmado.
    Args:
        reservation_id (int): ID de la reserva a actualizar.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si la reserva no existe.
    Returns:
        Reservation: Objeto de la reserva actualizada.

    """

    smtm = select(Reservation).where(Reservation.id == reservation_id) # Verificar si la reserva existe en la base de datos
    result = await db.execute(smtm)
    reservation = result.scalar_one_or_none()

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )

    # Actualizar el estado de la reserva a "confirmada"
    reservation.status_reservation = StatusReservation.CONFIRMED

    await db.commit()
    await db.refresh(reservation)

    return reservation
