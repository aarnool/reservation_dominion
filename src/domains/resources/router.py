from fastapi import APIRouter, Body, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from src.dependencies import get_db
from src.domains.resources.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from sqlalchemy import select
from src.models import Resources, Reservation


router = APIRouter(
    prefix="/resources",
    tags=["Reservas"]
)


# Endpoint para crear un nuevo recurso, recibiendo un objeto ResourceCreate 
@router.post(
    "/",
    summary="Crear un nuevo recurso",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_resource(
    db: Annotated[AsyncSession, Depends(get_db)],
    resource: Annotated[ResourceCreate, Body()]
):
    """
    Endpoint para crear un nuevo recurso.
    """

    stmt = select(Resources).where(Resources.name == resource.name)
    resource_exists = await db.scalar(stmt)

    if resource_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso ya existe"
        )

    new_resource = Resources(
        name=resource.name,
        description=resource.description,
        capacity=resource.capacity
    )

    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)

    return new_resource



# Endpoint para obtener todos los recursos, con soporte para paginación mediante los parámetros start y limit
@router.get(
    "/",
    summary="Obtener todos los recursos",
    response_model=list[ResourceResponse],
    status_code=status.HTTP_200_OK
)
async def get_resources(
    db: Annotated[AsyncSession, Depends(get_db)],
    start: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1)] = 10
):
    """
    Endpoint para obtener todos los recursos.
    """

    query = select(Resources).offset(start).limit(limit) # Query para obtener los recursos con paginación
    result = await db.scalars(query)
    resources = result.all()

    return resources



# Endpoint para actualizar un recurso existente, recibiendo un objeto ResourceUpdate
@router.patch(
    "/{resource_id}",
    summary="Actualizar un recurso existente",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK
)
async def update_resource(
    resource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    resource_update: Annotated[ResourceUpdate, Body()]
):
    """
    Endpoint para actualizar un recurso existente.
    """

    stmt = select(Resources).where(Resources.id == resource_id)
    resource = await db.scalar(stmt)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )

    # Actualizar los campos del recurso solo si se proporcionan en la solicitud
    resource_parcial = resource_update.model_dump(exclude_unset=True)
    for key, value in resource_parcial.items(): # Iterar sobre los campos proporcionados en la solicitud y actualizar el recurso
        setattr(resource, key, value)

    await db.commit()
    await db.refresh(resource)

    return resource    



# Endpoint para eliminar un recurso existente, verificando si tiene reservas asociadas antes de eliminarlo
@router.delete(
    "/{resource_id}",
    summary="Eliminar un recurso existente",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_resource(
    resource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Endpoint para eliminar un recurso existente.
    """

    stmt = select(Resources).where(Resources.id == resource_id)
    resource = await db.scalar(stmt)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )

    # Verificar si el recurso tiene reservas asociadas antes de eliminarlo
    reservation_stmt = select(Reservation).where(Reservation.resource_id == resource_id)
    reservations = await db.execute(reservation_stmt)

    if reservations.scalar_one_or_none():  # Si hay al menos una reserva asociada, no se puede eliminar el recurso
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el recurso porque tiene reservas asociadas"
        )

    await db.delete(resource)
    await db.commit()