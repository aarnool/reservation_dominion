from fastapi import Request, Response, Body, Security, HTTPException, status
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.dependencies import get_db, get_current_user
from typing import Annotated, List
from src.domains.resources.schemas import ResourceCreate, ResourceUpdate
from src.domains.resources.models import Resources


# Servicio para crear un recurso en la base de datos, verifica si el recurso ya existe y maneja la transacción de manera segura
async def create_resource( 
    resource: ResourceCreate,
    db: AsyncSession
) -> Resources:

    """

    Crea un nuevo recurso en el sistema.
    Args:
        response (Response): La respuesta HTTP que se enviará al cliente.
        current_user (dict): Información del usuario actual obtenida a partir del token de acceso JWT.
    Returns:
        dict: Un diccionario que contiene un mensaje de éxito y la información del recurso creado.
    Raises:
        HTTPException: Si el usuario no tiene los permisos necesarios para crear un recurso.

    """

    

    smtm = select(Resources).where(Resources.name == resource.name) # Verificar si el recurso ya existe en la base de datos
    result = await db.execute(smtm)
    existing_resource = result.scalar_one_or_none()

    if existing_resource:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso con este nombre ya existe."
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



# Servicio para obtener una lista de recursos desde la base de datos con paginación
async def get_resources(
    db: AsyncSession,
    start: int = 0, 
    limit: int = 10      
):
    """

    Obtiene una lista de recursos desde la base de datos con paginación.
    Args:
        db (AsyncSession): Sesión de base de datos asincrónica.
        start (int): Índice inicial para la paginación (por defecto es 0).
        limit (int): Número máximo de recursos a devolver (por defecto es 10).
    Returns:
        List[Resources]: Una lista de objetos Resources que representan los recursos obtenidos.

    """

    smtm = select(Resources).offset(start).limit(limit)
    result = await db.execute(smtm)
    resources = result.scalars().all()

    return resources



# Servicio para obtener un recurso específico por su ID desde la base de datos, verifica si el recurso existe antes de devolverlo
async def get_resource_by_id(
    resource_id: int,
    db: AsyncSession
):
    """

    Obtiene un recurso específico por su ID desde la base de datos.
    Args:
        resource_id (int): ID del recurso a obtener.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el recurso no existe.
    Returns:
        Resources: Objeto del recurso obtenido.


    """

    smtm = select(Resources).where(Resources.id == resource_id) # Verificar si el recurso existe en la base de datos
    result = await db.execute(smtm)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El recurso no existe."
        )

    return resource


# Servicio para eliminar un recurso de la base de datos, verifica si el recurso existe antes de eliminarlo
async def remove_resource(
    resource_id: int,
    db: AsyncSession
):
    """

    Elimina un recurso de la base de datos.
    Args:
        resource_id (int): ID del recurso a eliminar.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el recurso no existe.

    """

    smtm = select(Resources).where(Resources.id == resource_id) # Verificar si el recurso existe antes de eliminarlo
    result = await db.execute(smtm)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El recurso no existe."
        )

    await db.delete(resource)
    await db.commit()



# Servicio para actualizar un recurso existente en la base de datos, verifica si el recurso existe antes de actualizarlo.
async def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    db: AsyncSession,
):
    """

    Actualiza un recurso existente en la base de datos.
    Args:
        resource_id (int): ID del recurso a actualizar.
        resource_data (ResourceUpate): Datos actualizados del recurso.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el recurso no existe.
    Returns:
        Resources: Objeto del recurso actualizado.
        
    """

    smtm = select(Resources).where(Resources.id == resource_id)  # Asegurarse de que el recurso existe antes de intentar actualizarlo
    result = await db.execute(smtm)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El recurso no existe."
        )

    # Actualizar los campos del recurso con los datos proporcionados
    resource_data_dict = resource_data.model_dump(exclude_unset=True) # Obtener datos que solo han sido proporcionados

    for key, value in resource_data_dict.items(): # Actualizar solo los campos que han sido proporcionados en la solicitud
        setattr(resource, key, value)

    await db.commit()
    await db.refresh(resource)

    return resource

    