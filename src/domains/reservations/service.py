from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.reservations.models import Reservation
from src.domains.reservations.schemas import ReservationCreate, StatusReservation
from typing import List


# Servicio para obtener una lista de reservas desde la base de datos con paginación
async def get_reservations(
    user_id: int,
    db: AsyncSession,
    start: int = 0,
    limit: int = 10
) -> List[Reservation]:
    """

    Obtiene una lista de reservas desde la base de datos con paginación para un usuario específico.
    Args:
        user_id (int): ID del usuario autenticado.
        db (AsyncSession): Sesión de base de datos asincrónica.
        start (int): Índice inicial para la paginación (por defecto es 0).
        limit (int): Número máximo de reservas a devolver (por defecto es 10).
    Returns:
        List[Reservation]: Una lista de objetos Reservation que representan las reservas obtenidas.

    """

    smtm = select(Reservation).where(Reservation.user_id == user_id).offset(start).limit(limit)
    result = await db.execute(smtm)
    reservations = result.scalars().all()

    return reservations #type: ignore


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

    new_reservation = Reservation(
        user_id=user_id,
        resource_id=reservation.resource_id,
        title=reservation.title,
        description=reservation.description,
        start_time=reservation.start_time,
        end_time=reservation.end_time
    )

    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)

    return new_reservation


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
