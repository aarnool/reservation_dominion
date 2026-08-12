from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


# Schema base para la autenticación de usuarios
class UserBase(BaseModel):
    username: str = Field(
        description="Nombre de usuario único para el sistema", examples=["adsawdsa92"]
    )
    email: EmailStr = Field(
        description="Correo electrónico único del usuario",
        examples=["adsawdsa92@gmail.com"],
    )
    first_name: str = Field(description="Primer nombre del usuario", examples=["Arnol"])
    last_name: str = Field(description="Apellido del usuario", examples=["Diestra"])


# Schema para la creación de usuarios
class UserCreate(UserBase):
    password: str = Field(
        description="Contraseña del usuario", min_length=8, examples=["123456"]
    )


# Funcion intermeda para aplastar el formulario de registro en un objeto UserCreate
def user_create_from_form(
    username: str = Form(),
    email: EmailStr = Form(),  # noqa: B008
    first_name: str = Form(),
    last_name: str = Form(),
    password: str = Form(),
) -> UserCreate:
    return UserCreate(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )


# Schema para la respuesta de usuario para el Response de los ENDPOINTS
class UserResponse(UserBase):
    id: int = Field(description="ID único del usuario", examples=[1])
    avatar_full_url: str | None = Field(
        description="URL del avatar del usuario (opcional)",
        examples=["https://example.com/avatar.png"],
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del usuario",
        examples=["2023-01-01T12:00:00"],
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del usuario",
        examples=["2023-01-01T12:00:00"],
    )

    model_config = {
        "from_attributes": True  # Permite que Pydantic cree instancias del modelo a partir de objetos de base de datos
    }
