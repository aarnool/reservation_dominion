from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Esquemas para la creación, actualización y respuesta de recursos
class ResourceBase(BaseModel):
    name: str = Field(description="Nombre del recurso")
    description: str | None = Field(
        default=None, description="Descripción opcional del recurso"
    )
    capacity: int = Field(
        description="Capacidad del recurso",
        ge=1,  # La capacidad debe ser al menos 1
        examples=[10],
    )


# Esquemas para la creación de un recurso inyectable para usar en los endpoints Body
class ResourceCreate(ResourceBase):
    pass


# Esquemas para la respuesta de un recurso, incluyendo campos adicionales que deberia tener un recurso en la base de datos
class ResourceResponse(ResourceBase):
    id: int = Field(description="Unico identificador del recurso")
    created_at: datetime = Field(
        description="Marca de tiempo cuando el recurso fue creado"
    )
    updated_at: datetime = Field(
        description="Marca de tiempo cuando el recurso fue actualizado"
    )

    # Configuración para permitir la creación de instancias de ResourceResponse a partir de atributos de un objeto ORM.
    model_config = ConfigDict(from_attributes=True)


# Esquemas para la actualización de un recurso, permitiendo campos opcionales para actualizar solo los que se proporcionen
class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, description="Nombre del recurso")
    description: str | None = Field(
        default=None, description="Descripción opcional del recurso"
    )
    capacity: int | None = Field(
        default=None,
        description="Capacidad del recurso",
        ge=1,  # La capacidad debe ser al menos 1
        examples=[10],
    )
