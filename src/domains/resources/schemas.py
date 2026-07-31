from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime

class ResourceBase(BaseModel):
    name: str = Field(
        description="Nombre del recurso")
    description: str | None = Field(
        default=None, description="Descripción opcional del recurso")
    capacity: int = Field(
        description="Capacidad del recurso")


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: int = Field(
        description="Unico identificador del recurso")
    created_at: datetime = Field(
        description="Marca de tiempo cuando el recurso fue creado")
    updated_at: datetime = Field(
        description="Marca de tiempo cuando el recurso fue actualizado")

    # Configuración para permitir la creación de instancias de ResourceResponse a partir de atributos de un objeto ORM.
    model_config = ConfigDict(
        from_attributes=True
    )

class ResourceUpdate(BaseModel):
    name: str | None = Field(
        default=None, description="Nombre del recurso")
    description: str | None = Field(
        default=None, description="Descripción opcional del recurso")
    capacity: int | None = Field(
        default=None, description="Capacidad del recurso")
    
    