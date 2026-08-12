from enum import Enum

from sqlalchemy import CHAR, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from src.core.utils import TZDateTime
from src.database import Base


class StatusReservation(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Reservation(Base):
    __tablename__ = "reservations"

    # Definición de las columnas de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    resource_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resources.id"), nullable=False
    )
    code_reservation: Mapped[str] = mapped_column(CHAR(10), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(124), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(TZDateTime, nullable=False)
    end_time: Mapped[DateTime] = mapped_column(TZDateTime, nullable=False)
    status_reservation: Mapped[StatusReservation] = mapped_column(
        SQLEnum(StatusReservation), nullable=False, default=StatusReservation.PENDING
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    # --------------------------------------------------------------------------------------#

    # Relación muchos a uno con la tabla de usuarios
    user: Mapped["User"] = relationship("User", back_populates="reservations")  # type: ignore  # noqa: F821, UP037

    # Relación muchos a uno con la tabla de recursos
    resource: Mapped["Resources"] = relationship(  # type: ignore  # noqa: F821, UP037
        "Resources", back_populates="reservations"
    )

    # Relacion muchos a uno con la tabla de notificaciones
    notifications: Mapped[list["Notification"]] = relationship(  # type: ignore  # noqa: F821, UP037
        "Notification",
        back_populates="reservation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
