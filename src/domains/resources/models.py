from sqlalchemy import Column, Integer, String, DateTime, func, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.database import Base

# Definición del modelo de datos para la tabla de recursos
class Resources(Base):
    __tablename__ = "resources"

    # Definición de las columnas de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True) # Texto largo para la descripción del recurso
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación uno a muchos con la tabla de reservas
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="resource") # type: ignore