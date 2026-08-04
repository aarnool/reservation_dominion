from fastapi import APIRouter, Body, Depends, HTTPException, status, Security, Query, Path
from src.domains.reservations.schemas import ReservationResponse, ReservationCreate, StatusReservation, ReservationUpdate
from src.dependencies import get_db, get_current_user
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.reservations import service
from datetime import date

router = APIRouter(
    prefix="/reservations",
    tags=["Reservas"]
)


# Endpoint para obtener reservas con múltiples filtros opcionales (fecha, estado, recurso)
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
    
    return await service.get_reservations(
        user_id=current_user["id"], 
        db=db, 
        status_filter=status_filter, 
        filter_date=filter_date, 
        resource_ids=resource_ids, 
        resource_name=resource_name,
        start=start, 
        limit=limit
    )



# Endpoint para crear una nueva reserva
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
    
    return await service.create_reservation(
        user_id=current_user["id"], 
        reservation=reservation, 
        db=db)



# Endpoint para actualizar una reserva existente (solo ciertos campos)
@router.patch(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualiza una reserva existente (solo ciertos campos)"
)
async def update_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a actualizar")],
    reservation_update: Annotated[ReservationUpdate, Body(description="Datos de la reserva a actualizar (solo ciertos campos)")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:update"])]
):
    
    """

    Actualiza una reserva existente en el sistema, permitiendo modificar solo ciertos campos.
    ### Detalles:
    - **reservation_id**: ID de la reserva a actualizar (obligatorio)
    - **title**: Nuevo título de la reserva (opcional)
    - **description**: Nueva descripción de la reserva (opcional)
    - **end_time**: Nueva fecha y hora de fin de la reserva (opcional)

    """
    
    return await service.update_reservation(
        reservation_id=reservation_id, 
        reservation_update=reservation_update, 
        db=db,
        user_id=current_user["id"]
    )



# Endpoint para actualizar el estado de una reserva existente a aprobada
@router.patch(
    "/{reservation_id}/approve",
    tags=["Admin"],
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Aprobar una reserva ya existente"
)
async def approve_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a actualizar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:approve"])]
):
    
    """

    Actualiza una reserva existente en el sistema, cambiándola a aprobada.
    ### Detalles:
    - **reservation_id**: ID de la reserva a actualizar (obligatorio)

    """
    
    return await service.approve_reservation(
        reservation_id=reservation_id, 
        db=db)




@router.get(
    "/all",
    tags=["Admin"],
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene todas las reservas del sistema (solo para administradores)"
)
async def get_all_reservations_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:read_all"])],
    start: Annotated[int, Query(
        description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[int, Query(
        description="Número máximo de reservas a devolver (opcional)")] = 10,
    
):
    
    """

    Obtiene todas las reservas del sistema, sin importar el usuario que las haya creado. Este endpoint es exclusivo para administradores.
    ### Detalles:
    - **current_user**: Usuario autenticado con rol de administrador (obligatorio)

    """
    
    return await service.get_all_reservations(
        db=db,
        start=start,
        limit=limit
    )



# Endpoint para cancelar una reserva existente
@router.patch(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancela una reserva existente"
)
async def cancel_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a cancelar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["reservations:cancel"])]
):
    
    """

    Cancela una reserva existente en el sistema.
    ### Detalles:
    - **reservation_id**: ID de la reserva a cancelar (obligatorio)

    """
    
    return await service.cancel_own_reservation(
        user_id=current_user["id"],
        reservation_id=reservation_id, 
        db=db)