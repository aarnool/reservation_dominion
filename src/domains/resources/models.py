from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


# Definición del modelo de datos para la tabla de recursos
class Resources(Base):
    __tablename__ = "resources"

    # Definición de las columnas de la tabla
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Texto largo para la descripción del recurso
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relación uno a muchos con la tabla de reservas
    reservations: Mapped[list["Reservation"]] = relationship(  # type: ignore  # noqa: F821, UP037
        "Reservation", back_populates="resource"
    )
