from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.reservations.models import Reservation
from src.domains.resources.models import Resources
from src.domains.reservations.schemas import ReservationCreate, StatusReservation, ReservationUpdate
from typing import Sequence, List
from datetime import date, datetime, time, timezone

# Servicio para obtener todas las reservas de todos los usuarios, con paginacion
async def get_all_reservations(
    db: AsyncSession,
    start: int = 0,
    limit: int = 10
) -> Sequence[Reservation]:
    """
    Obtiene todas las reservas de todos los usuarios desde la base de datos, incluyendo paginación.
    Args:
        db (AsyncSession): Sesión de base de datos asincrónica.
        start (int): Índice inicial para la paginación (por defecto es 0).
        limit (int): Número máximo de reservas a devolver (por defecto es 10).
    Returns:
        Sequence[Reservation]: Una lista de objetos Reservation que representan las reservas obtenidas.

    """

    query = select(Reservation).offset(start).limit(limit)
    
    result = await db.execute(query)
    reservations = result.scalars().all()

    return reservations
    


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


# Verificar si la fecha del recurso está disponible para la reserva, considerando las reservas existentes y el estado de las mismas
async def is_resource_available(
    resource_id: int,
    start_time: datetime,
    end_time: datetime,
    db: AsyncSession,
    exclude_reservation_id: int | None = None  # ID de la reserva a excluir (útil al actualizar para no chocar consigo misma)
) -> bool:
    """

    Verifica si un recurso está disponible para una reserva en un rango de tiempo específico, considerando las reservas existentes y su estado.
    Args:
        resource_id (int): ID del recurso a verificar.
        start_time (datetime): Fecha y hora de inicio de la reserva.
        end_time (datetime): Fecha y hora de finalización de la reserva.
        db (AsyncSession): Sesión de base de datos asincrónica.
        exclude_reservation_id (int | None): ID de la reserva a excluir de la verificación (por defecto None). Se usa al actualizar una reserva para que no choque consigo misma.
    Returns:
        bool: True si el recurso está disponible, False si no lo está.

    """

    smtm = select(Reservation).where(
        Reservation.resource_id == resource_id,
        Reservation.status_reservation.not_in([StatusReservation.CANCELLED, StatusReservation.COMPLETED]),
        Reservation.end_time > start_time,
        Reservation.start_time < end_time,
    )

    # Si se proporciona un ID de reserva a excluir, lo filtramos para que no choque consigo misma al actualizar
    if exclude_reservation_id is not None:
        smtm = smtm.where(Reservation.id != exclude_reservation_id)

    result = await db.execute(smtm)
    overlapping_reservations = result.scalars().all()

    return len(overlapping_reservations) == 0


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

    if not await is_resource_available(reservation.resource_id, reservation.start_time, reservation.end_time, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso no está disponible en el rango de tiempo especificado"
        )
    
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
    db: AsyncSession,
    user_id: int
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

    
    smtm = select(Reservation).where(
        Reservation.id == reservation_id,
        Reservation.user_id == user_id) # Verificar si la reserva existe en la base de datos
    result = await db.execute(smtm)
    reservation = result.scalar_one_or_none()

    # Si la reserva no existe, lanzar una excepción HTTP 404
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )

    # Si se proporciona un nuevo resource_id, verificar si el recurso existe
    if reservation_update.resource_id is not None:
        resource = await db.get(Resources, reservation_update.resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El recurso especificado no existe"
            )

    start_time = reservation_update.start_time or reservation.start_time
    end_time = reservation_update.end_time or reservation.end_time

    if reservation_update.start_time is not None or reservation_update.end_time is not None:
        # Se excluye la reserva actual para que no choque consigo misma al verificar disponibilidad
        if not await is_resource_available(
            resource_id=reservation.resource_id, 
            db=db, 
            exclude_reservation_id=reservation_id,
             # Ignorar los errores de tipo ya que start_time y end_time son opcionales datetime y choca con el tipado de Pydantic
            start_time=start_time, #type: ignore
            end_time=end_time,  #type: ignore
        ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El recurso no está disponible en el rango de tiempo especificado"
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



async def cancel_own_reservation(
    reservation_id: int,
    user_id: int,
    db: AsyncSession
) -> Reservation:
    """
    Cancela una reserva existente realizada por el usuario autenticado.
    Args:
        reservation_id (int): ID de la reserva a cancelar.
        user_id (int): ID del usuario autenticado que realiza la cancelación.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si la reserva no existe o no pertenece al usuario autenticado.
    Returns:
        Reservation: Objeto de la reserva cancelada.

    """

    smtm = select(Reservation).where(Reservation.id == reservation_id, Reservation.user_id == user_id)
    result = await db.execute(smtm)
    reservation = result.scalar_one_or_none()

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada o no pertenece al usuario autenticado"
        )


    if reservation.status_reservation == StatusReservation.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La reserva ya ha sido cancelada"
        )
    
    # Actualizar el estado de la reserva a "cancelada"
    reservation.status_reservation = StatusReservation.CANCELLED

    await db.commit()
    await db.refresh(reservation)

    return reservation