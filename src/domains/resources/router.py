from fastapi import APIRouter, Body, Depends, HTTPException, Request, status, Query, Security, Path
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.dependencies import get_db
from src.domains.resources.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from src.domains.resources.service import create_resource, get_resources, update_resource, remove_resource, get_resource_by_id
from src.dependencies import get_current_user

router = APIRouter(
    prefix="/resources",
    tags=["Reservas"]
)


@router.post(
    "/", 
    tags=["admin"],
    response_model=ResourceResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo recurso"
)
async def create_resource_endpoint(
    resource: Annotated[ResourceCreate, Body(description="Datos del recurso a crear")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["resources:create"])]
):
    
    """

    Crea un nuevo recurso en el sistema.
    ### Detalles:
    - **name**: Nombre del recurso (obligatorio)
    - **description**: Descripción opcional del recurso
    - **capacity**: Capacidad del recurso (obligatorio)

    """

    return await create_resource(resource=resource, db=db)
    


@router.get(
    "/",
    response_model=list[ResourceResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener una lista de recursos con paginación"
)
async def get_resources_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["resources:read"])],
    start: Annotated[int, Query(
        description="Índice de inicio para la paginación")] = 0,
    limit: Annotated[int, Query(
        description="Número máximo de recursos a devolver")] = 10
    
):
    
    """

    Obtiene una lista de recursos desde la base de datos con paginación.
    ### Detalles:
    - **start**: Índice de inicio para la paginación (opcional, por defecto 0)
    - **limit**: Número máximo de recursos a devolver (opcional, por defecto 10)

    """
    
    return await get_resources(db=db, start=start, limit=limit)


@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un recurso específico por ID"
)
async def get_resource_by_id_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a obtener")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["resources:read"])]
):
    """
    Obtiene un recurso específico por su ID desde la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a obtener (obligatorio)
    """
    
    return await get_resource_by_id(resource_id=resource_id, db=db)


@router.patch(
    "/{resource_id}",
    tags=["admin"],
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un recurso existente"
)
async def update_resource_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a actualizar")],
    resource_data: Annotated[ResourceUpdate, Body(description="Datos actualizados del recurso")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["resources:update"])]
):
    """
    Actualiza un recurso existente en la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a actualizar (obligatorio)
    - **resource_data**: Datos actualizados del recurso (obligatorio)
    """
    
    return await update_resource(resource_id=resource_id, resource_data=resource_data, db=db)



@router.delete(
    "/{resource_id}",
    tags=["admin"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un recurso existente"
)
async def delete_resource_endpoint(
    resource_id: Annotated[int, Path(description="ID del recurso a eliminar")],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Security(get_current_user, scopes=["resources:delete"])]
):
    """
    Elimina un recurso existente de la base de datos.
    ### Detalles:
    - **resource_id**: ID del recurso a eliminar (obligatorio)
    """
    
    await remove_resource(resource_id=resource_id, db=db)
 