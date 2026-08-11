from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from src.database import Base


class TypeNotification(str, Enum):
    INFO = "info"
    RESERVATION = "reservation"
    ACCOUNT = "account"
    PAYMENT = "payment"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type_notification: Mapped[TypeNotification] = mapped_column(
        SQLEnum(TypeNotification), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    reservation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reservations.id"), nullable=True, index=True
    )

    # Relación muchos a uno con la tabla de usuarios
    user: Mapped["User"] = relationship("User", back_populates="notifications")  # type: ignore  # noqa: F821, UP037

    # Relación muchos a uno con la tabla de reservas
    reservation: Mapped["Reservation"] = relationship(  # type: ignore  # noqa: F821, UP037
        "Reservation", back_populates="notifications"
    )
