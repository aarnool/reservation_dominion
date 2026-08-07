from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Response, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.domains.reservations import service
from src.domains.reservations.schemas import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    StatusReservation,
)

router = APIRouter(prefix="/reservations", tags=["Reservas"])


# Endpoint para obtener reservas con múltiples filtros opcionales (fecha, estado, recurso)
@router.get(
    "/",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtiene reservas con múltiples filtros opcionales: fecha, estado, recurso (TODOS LOS USUARIOS CON PERMISOS 👥)",
)
async def get_reservations_endpoint(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:read"])
    ],
    status_filter: Annotated[
        StatusReservation | None,
        Query(
            alias="status",
            description="Estado por el que filtrar las reservas (opcional)",
        ),
    ] = None,
    filter_date: Annotated[
        date | None,
        Query(
            alias="date",
            description="Fecha exacta por la que filtrar las reservas en formato YYYY-MM-DD (opcional)",
        ),
    ] = None,
    resource_ids: Annotated[
        list[int] | None,
        Query(
            alias="resource_id",
            description="Filtro opcional por múltiples IDs de recursos (opcional)",
        ),
    ] = None,
    resource_name: Annotated[
        str | None,
        Query(
            alias="resource_name",
            description="Filtro opcional por nombre del recurso reservado (búsqueda parcial)",
        ),
    ] = None,
    start: Annotated[int, Query(description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[
        int, Query(description="Número máximo de reservas a devolver (opcional)")
    ] = 10,
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Obtiene las reservas permitiendo el filtrado opcional.
    Si el usuario tiene permisos de administrador, obtiene todas las reservas del sistema.
    Si es un usuario regular, obtiene solo las suyas.
    ### Detalles:
    - **status**: Estado por el cual se desean filtrar las reservas (opcional).
    - **date**: Fecha exacta por la cual filtrar (opcional).
    - **resource_id**: Uno o múltiples IDs de recursos para filtrar (opcional, se puede repetir: ?resource_id=1&resource_id=2).
    - **resource_name**: Nombre o fragmento del nombre del recurso reservado para filtrar (opcional).
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0).
    - **limit**: Número máximo de reservas a devolver (opcional, por defecto 10).

    """

    is_admin = "reservations:read_all" in current_user.get("scopes", [])

    # Llamamos al mismo servicio unificado para ambos casos
    reservations, total = await service.get_reservations(
        db=db,
        user_id=None if is_admin else current_user["id"],
        status_filter=status_filter,
        filter_date=filter_date,
        resource_ids=resource_ids,
        resource_name=resource_name,
        start=start,
        limit=limit,
    )

    response.headers["X-Total-Count"] = str(total)
    return reservations


# Endpoint para obtener una reserva específica por su ID
@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtiene una reserva específica por su ID (TODOS LOS USUARIOS CON PERMISOS 👥)",
)
async def get_reservation_by_id_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a obtener")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:read"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Obtiene una reserva específica por su ID.
    Si el usuario tiene permisos de administrador, puede obtener cualquier reserva.
    Si es un usuario regular, solo puede obtener sus propias reservas.
    ### Detalles:
    - **reservation_id**: ID de la reserva a obtener (obligatorio)

    """

    is_admin = "reservations:read_all" in current_user.get("scopes", [])

    return await service.get_reservation_by_id(
        db=db,
        reservation_id=reservation_id,
        user_id=None if is_admin else current_user["id"],
    )


# Endpoint para crear una nueva reserva
@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nueva reserva (TODOS LOS USUARIOS CON PERMISOS 👥)",
)
async def create_reservation_endpoint(
    reservation: Annotated[
        ReservationCreate, Body(description="Datos de la reserva a crear")
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:create"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Crea una nueva reserva en el sistema.
    ### Detalles:
    - **resource_id**: ID del recurso a reservar (obligatorio)
    - **title**: Título de la reserva (obligatorio)
    - **description**: Descripción opcional de la reserva
    - **start_time**: Fecha y hora de inicio de la reserva (obligatorio)
    - **end_time**: Fecha y hora de fin de la reserva (obligatorio)

    """

    return await service.create_reservation(
        user_id=current_user["id"], reservation=reservation, db=db
    )


# Endpoint para actualizar una reserva existente (solo ciertos campos)
@router.patch(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualiza una reserva existente (TODOS LOS USUARIOS CON PERMISOS 👥)",
)
async def update_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a actualizar")],
    reservation_update: Annotated[
        ReservationUpdate,
        Body(description="Datos de la reserva a actualizar (solo ciertos campos)"),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:update"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
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
        user_id=current_user["id"],
    )


# Endpoint para actualizar el estado de una reserva existente a aprobada
@router.patch(
    "/{reservation_id}/approve",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Aprobar una reserva ya existente (SOLO ADMINISTRADOR 🚫)",
)
async def approve_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a actualizar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:approve"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Actualiza una reserva existente en el sistema, cambiándola a aprobada.
    ### Detalles:
    - **reservation_id**: ID de la reserva a actualizar (obligatorio)

    """

    return await service.approve_reservation(reservation_id=reservation_id, db=db)


# Endpoint para cancelar una reserva existente
@router.patch(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancela una reserva existente (TODOS LOS USUARIOS CON PERMISOS 👥)",
)
async def cancel_reservation_endpoint(
    reservation_id: Annotated[int, Path(description="ID de la reserva a cancelar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["reservations:cancel"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Cancela una reserva existente en el sistema.
    ### Detalles:
    - **reservation_id**: ID de la reserva a cancelar (obligatorio)

    """

    return await service.cancel_own_reservation(
        user_id=current_user["id"], reservation_id=reservation_id, db=db
    )
