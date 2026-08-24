from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domains.resources.models import Resources
from src.domains.resources.schemas import ResourceCreate, ResourceUpdate


# Servicio para crear un recurso en la base de datos, verifica si el recurso ya existe y maneja la transacción de manera segura
async def create_resource(resource: ResourceCreate, db: AsyncSession) -> Resources:
    """

    Crea un nuevo recurso en la base de datos.
    Args:
        resource (ResourceCreate): Datos del recurso a crear.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el recurso con el mismo nombre ya existe.
    Returns:
        Resources: Objeto del recurso creado.

    """

    smtm = select(Resources).where(
        Resources.name == resource.name
    )  # Verificar si el recurso ya existe en la base de datos
    result = await db.execute(smtm)
    existing_resource = result.scalar_one_or_none()

    if existing_resource:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recurso con este nombre ya existe.",
        )

    new_resource = Resources(
        name=resource.name, description=resource.description, capacity=resource.capacity
    )

    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)

    return new_resource


from datetime import datetime


# Servicio para obtener una lista de recursos desde la base de datos con paginación y filtros
async def get_resources(
    db: AsyncSession,
    start: int = 0,
    limit: int = 10,
    min_capacity: int | None = None,
    capacity: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    """
    Obtiene una lista de recursos desde la base de datos con paginación y filtros.

    Args:
        db (AsyncSession): Sesión de base de datos asincrónica.
        start (int): Índice inicial para la paginación.
        limit (int): Número máximo de recursos a devolver.
        min_capacity (int | None): Capacidad mínima requerida.
        capacity (int | None): Capacidad exacta requerida.
        start_time (datetime | None): Hora de inicio para verificar disponibilidad.
        end_time (datetime | None): Hora de fin para verificar disponibilidad.

    Returns:
        Tuple[List[Resources], int]: Lista de recursos y conteo total.
    """
    smtm = select(Resources)

    # Filtro por capacidad mínima o exacta
    target_capacity = min_capacity if min_capacity is not None else capacity
    if target_capacity is not None:
        smtm = smtm.where(Resources.capacity >= target_capacity)

    # Filtro por disponibilidad en rango horario [start_time, end_time]
    if start_time is not None and end_time is not None:
        from src.domains.reservations.models import Reservation, StatusReservation
        overlapping = (
            select(Reservation.id)
            .where(
                Reservation.resource_id == Resources.id,
                Reservation.status_reservation != StatusReservation.CANCELLED,
                Reservation.start_time < end_time,
                Reservation.end_time > start_time,
            )
            .exists()
        )
        smtm = smtm.where(~overlapping)

    # Conteo de recursos totales con filtros aplicados
    count_smtm = select(func.count()).select_from(smtm.subquery())
    result_count = await db.execute(count_smtm)
    total_count = result_count.scalar_one()

    # Paginación
    result = await db.execute(smtm.offset(start).limit(limit))
    resources = result.scalars().all()

    return resources, total_count


# Servicio para obtener un recurso específico por su ID desde la base de datos, verifica si el recurso existe antes de devolverlo
async def get_resource_by_id(resource_id: int, db: AsyncSession):
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

    # smtm = select(Resources).where(Resources.id == resource_id) # Verificar si el recurso existe en la base de datos
    # result = await db.execute(smtm)
    resource = await db.get(Resources, resource_id)

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El recurso no existe."
        )

    return resource


# Servicio para eliminar un recurso de la base de datos, verifica si el recurso existe antes de eliminarlo
async def remove_resource(resource_id: int, db: AsyncSession):
    """

    Elimina un recurso de la base de datos.
    Args:
        resource_id (int): ID del recurso a eliminar.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el recurso no existe.

    """

    smtm = (
        select(Resources)
        .options(selectinload(Resources.reservations))
        .where(Resources.id == resource_id)
    )  # Verificar si el recurso existe antes de eliminarlo
    result = await db.execute(smtm)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El recurso no existe."
        )

    # Verificar si el recurso tiene reservas asociadas antes de eliminarlo
    if resource.reservations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el recurso porque tiene reservas asociadas.",
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

    smtm = select(Resources).where(
        Resources.id == resource_id
    )  # Asegurarse de que el recurso existe antes de intentar actualizarlo
    result = await db.execute(smtm)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El recurso no existe."
        )

    # Verificar si el nuevo nombre del recurso ya está en uso por otro recurso
    if resource_data.name:
        smtm = select(Resources).where(
            Resources.name == resource_data.name, Resources.id != resource_id
        )
        result = await db.execute(smtm)
        existing_resource = result.scalar_one_or_none()

        if existing_resource:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre del recurso ya está en uso por otro recurso.",
            )

    # Actualizar los campos del recurso con los datos proporcionados
    resource_data_dict = resource_data.model_dump(
        exclude_unset=True
    )  # Obtener datos que solo han sido proporcionados

    for (
        key,
        value,
    ) in (
        resource_data_dict.items()
    ):  # Actualizar solo los campos que han sido proporcionados en la solicitud
        setattr(resource, key, value)

    await db.commit()
    await db.refresh(resource)

    return resource
