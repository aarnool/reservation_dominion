from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from src.domains.reservations.models import StatusReservation


# Modelo para filtros
class ReservationFilter(BaseModel):
    status_reservation: StatusReservation | None = Field(default=None)
    filter_date: AwareDatetime | None = Field(default=None)
    resource_ids: list[int] | None = Field(default=None)
    resource_name: str | None = Field(default=None)
    start: int = Field(default=0)
    limit: int = Field(default=10)


# Esquemas para la creación, actualización y respuesta de reservas
class ReservationBase(BaseModel):
    title: str = Field(description="Nombre del recurso")
    description: str | None = Field(default=None, description="Descripción del recurso")
    resource_id: int = Field(description="Identificador del recurso a reservar")
    start_time: AwareDatetime = Field(
        description="Fecha y hora de inicio de la reserva"
    )
    end_time: AwareDatetime = Field(
        description="Fecha y hora de finalización de la reserva"
    )

    # Validador a nivel de modelo: la fecha de inicio debe ser estrictamente anterior a la fecha de fin
    @model_validator(mode="after")
    def validate_start_before_end(self):
        if self.start_time >= self.end_time:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        return self


# Esquemas para la creación de una reserva inyectable para usar en los endpoints Body
class ReservationCreate(ReservationBase):
    pass


# Esquemas para la respuesta de una reserva, incluyendo campos adicionales que deberia tener una reserva en la base de datos
class ReservationResponse(ReservationBase):
    id: int = Field(description="Identificador único de la reserva")
    user_id: int = Field(description="Identificador del usuario que realizó la reserva")
    status_reservation: StatusReservation = Field(
        default=StatusReservation.PENDING, description="Estado de la reserva"
    )
    resource_id: int = Field(description="Identificador del recurso reservado")
    created_at: datetime = Field(description="Fecha y hora de creación de la reserva")
    updated_at: datetime = Field(
        description="Fecha y hora de última actualización de la reserva"
    )

    model_config = ConfigDict(from_attributes=True)


# Esquemas para la actualización de una reserva, permitiendo actualizar solo ciertos campos
class ReservationUpdate(BaseModel):
    title: str | None = Field(default=None, description="Nombre del recurso")
    description: str | None = Field(default=None, description="Descripción del recurso")
    resource_id: int | None = Field(
        default=None, description="Identificador del recurso a reservar"
    )
    start_time: datetime | None = Field(
        default=None, description="Fecha y hora de inicio de la reserva"
    )
    end_time: datetime | None = Field(
        default=None, description="Fecha y hora de finalización de la reserva"
    )
