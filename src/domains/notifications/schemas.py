from datetime import datetime

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    message: str = Field(description="Mensaje de la notificación")
    type_notification: str = Field(description="Tipo de notificación")
    is_read: bool = Field(
        default=False, description="Indica si la notificación ha sido leída"
    )
    user_id: int = Field(description="ID del usuario al que pertenece la notificación")
    reservation_id: int | None = Field(
        default=None, description="ID de la reserva asociada a la notificación"
    )


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int = Field(description="ID de la notificación")

    created_at: datetime = Field(description="Fecha de creación de la notificación")
    updated_at: datetime = Field(
        description="Fecha de actualización de la notificación"
    )
    model_config = {
        "from_attributes": True,
    }
