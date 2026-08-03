from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Query, Path
from src.domains.reservations.schemas import ReservationResponse, ReservationCreate
from src.dependencies import get_db, get_current_user
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.service import get_reservations, create_reservation, approve_reservation

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"]
)


@router.get(
    "/",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene todas las reservas del usuario autenticado"
)
async def get_reservations_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:read"])],
    start: Annotated[int, Query(
        description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[int, Query(
        description="Número máximo de reservas a devolver (opcional)")] = 10
):
    
    """

    Obtiene todas las reservas asociadas al usuario autenticado.
    ### Detalles:
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0)
    - **limit**: Número máximo de reservas a devolver (opcional, por defecto 10)

    """
    
    return await get_reservations(user_id=current_user["id"], db=db, start=start, limit=limit)



@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nueva reserva"
)
async def create_reservation_endpoint(
    reservation: Annotated[ReservationCreate, Body(description="Datos de la reserva a crear")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:create"])]
):
    
    """

    Crea una nueva reserva en el sistema.
    ### Detalles:
    - **resource_id**: ID del recurso a reservar (obligatorio)
    - **title**: Título de la reserva (obligatorio)
    - **description**: Descripción opcional de la reserva
    - **start_time**: Fecha y hora de inicio de la reserva (obligatorio)
    - **end_time**: Fecha y hora de fin de la reserva (obligatorio)

    """
    
    return await create_reservation(user_id=current_user["id"], reservation=reservation, db=db)



@router.patch(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Aprobar una reserva ya existente"
)
async def update_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a actualizar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:approve"])]
):
    
    """

    Actualiza una reserva existente en el sistema, cambiándola a aprobada.
    ### Detalles:
    - **reservation_id**: ID de la reserva a actualizar (obligatorio)

    """
    
    return await approve_reservation(reservation_id=reservation_id, db=db)