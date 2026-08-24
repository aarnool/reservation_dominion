from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Response, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.domains.resources.schemas import (
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from src.domains.resources.service import (
    create_resource,
    get_resource_by_id,
    get_resources,
    remove_resource,
    update_resource,
)

router = APIRouter(prefix="/resources", tags=["Recursos"])


@router.post(
    "/",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo recurso (SOLO ADMINISTRADOR 🚫)",
)
async def create_resource_endpoint(
    resource: Annotated[ResourceCreate, Body(description="Datos del recurso a crear")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["resources:create"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Crea un nuevo recurso en el sistema que se conectara con las reservas.
    ### Detalles:
    - **name**: Nombre del recurso (obligatorio)
    - **description**: Descripción opcional del recurso
    - **capacity**: Capacidad del recurso (obligatorio)

    """

    return await create_resource(resource=resource, db=db)


from datetime import datetime


@router.get(
    "/",
    response_model=list[ResourceResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener una lista de recursos con paginación y filtros de disponibilidad/capacidad (TODOS LOS USUARIOS 👥)",
)
async def get_resources_endpoint(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["resources:read"])
    ],
    min_capacity: Annotated[
        int | None, Query(description="Filtro por capacidad mínima requerida", ge=1)
    ] = None,
    capacity: Annotated[
        int | None, Query(description="Filtro por capacidad exacta requerida", ge=1)
    ] = None,
    start_time: Annotated[
        datetime | None,
        Query(description="Hora de inicio para verificar disponibilidad del recurso"),
    ] = None,
    end_time: Annotated[
        datetime | None,
        Query(description="Hora de fin para verificar disponibilidad del recurso"),
    ] = None,
    start: Annotated[int, Query(description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[
        int, Query(description="Número máximo de recursos a devolver")
    ] = 10,
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Obtiene una lista de recursos desde la base de datos permitiendo filtrar por capacidad y disponibilidad en rango horario.
    ### Detalles:
    - **min_capacity**: Capacidad mínima del recurso (opcional)
    - **capacity**: Capacidad requerida (opcional)
    - **start_time**: Fecha/hora inicial de disponibilidad deseada (opcional)
    - **end_time**: Fecha/hora final de disponibilidad deseada (opcional)
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0)
    - **limit**: Número máximo de recursos a devolver (opcional, por defecto 10)

    """

    resource, total = await get_resources(
        db=db,
        start=start,
        limit=limit,
        min_capacity=min_capacity,
        capacity=capacity,
        start_time=start_time,
        end_time=end_time,
    )

    response.headers["X-Total-Count"] = str(total)
    return resource


@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un recurso específico por ID (TODOS LOS USUARIOS 👥)",
)
async def get_resource_by_id_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a obtener")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["resources:read"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE POSEEN TODOS LOS USUARIOS 👥🔓**
    Obtiene un recurso específico por su ID desde la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a obtener (obligatorio)

    """

    return await get_resource_by_id(resource_id=resource_id, db=db)


@router.patch(
    "/{resource_id}",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un recurso existente (SOLO ADMINISTRADOR 🚫)",
)
async def update_resource_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a actualizar")],
    resource_data: Annotated[
        ResourceUpdate, Body(description="Datos actualizados del recurso")
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["resources:update"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Actualiza un recurso existente en la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a actualizar (obligatorio)
    - **resource_data**: Datos actualizados del recurso (obligatorio)

    """

    return await update_resource(
        resource_id=resource_id, resource_data=resource_data, db=db
    )


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un recurso existente (SOLO ADMINISTRADOR 🚫)",
)
async def delete_resource_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a eliminar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Security(get_current_user, scopes=["resources:delete"])
    ],
):
    """

    ### **REQUIERE PERMISOS QUE SOLO POSEEN LOS ADMINISTRADORES 🚫🔒**
    Elimina un recurso existente de la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a eliminar (obligatorio)

    """

    await remove_resource(resource_id=resource_id, db=db)
