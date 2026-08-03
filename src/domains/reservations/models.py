from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.database import Base
from enum import Enum
from sqlalchemy.types import Enum as SQLEnum


class StatusReservation(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Reservation(Base):
    __tablename__ = "reservations"

    # Definición de las columnas de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(124), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_reservation: Mapped[StatusReservation] = mapped_column(SQLEnum(StatusReservation), nullable=False, default=StatusReservation.PENDING)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación muchos a uno con la tabla de usuarios
    user: Mapped["User"] = relationship("User", back_populates="reservations") # type: ignore
    
    # Relación muchos a uno con la tabla de recursos
    resource: Mapped["Resources"] = relationship("Resources", back_populates="reservations") #type: ignore