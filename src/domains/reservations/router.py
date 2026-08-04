from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Query, Path
from src.domains.reservations.schemas import ReservationResponse, ReservationCreate, StatusReservation
from src.dependencies import get_db, get_current_user
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations.service import get_reservations, create_reservation, approve_reservation
from datetime import date

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"]
)


@router.get(
    "/",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene reservas con múltiples filtros opcionales (fecha, estado, recurso)"
)
async def get_reservations_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:read"])],
    status_filter: Annotated[StatusReservation | None, Query(
        alias="status", description="Estado por el que filtrar las reservas (opcional)")] = None,
    filter_date: Annotated[date | None, Query(
        alias="date", description="Fecha exacta por la que filtrar las reservas en formato YYYY-MM-DD (opcional)")] = None,
    resource_ids: Annotated[List[int] | None, Query(
        alias="resource_id", description="Filtro opcional por múltiples IDs de recursos (opcional)")] = None,
    resource_name: Annotated[str | None, Query(
        alias="resource_name", description="Filtro opcional por nombre del recurso reservado (búsqueda parcial)")] = None,
    start: Annotated[int, Query(
        description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[int, Query(
        description="Número máximo de reservas a devolver (opcional)")] = 10
):
    
    """

    Obtiene las reservas asociadas al usuario autenticado, permitiendo el filtrado opcional por múltiples campos al mismo tiempo.
    ### Detalles:
    - **status**: Estado por el cual se desean filtrar las reservas (opcional).
    - **date**: Fecha exacta por la cual filtrar (opcional).
    - **resource_id**: Uno o múltiples IDs de recursos para filtrar (opcional, se puede repetir: ?resource_id=1&resource_id=2).
    - **resource_name**: Nombre o fragmento del nombre del recurso reservado para filtrar (opcional).
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0).
    - **limit**: Número máximo de reservas a devolver (opcional, por defecto 10).

    """
    
    return await get_reservations(
        user_id=current_user["id"], 
        db=db, 
        status_filter=status_filter, 
        filter_date=filter_date, 
        resource_ids=resource_ids, 
        resource_name=resource_name,
        start=start, 
        limit=limit
    )



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
    tags=["admin"],
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