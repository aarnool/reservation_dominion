from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.database import Base

# Tabla de Usuarios donde se almacenan los datos de los usuarios del sistema
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación muchos a uno con la tabla de roles
    role: Mapped["Role"] = relationship("Role", back_populates="users") #type: ignore

    # Relación uno a muchos con la tabla de notificaciones
    notifications: Mapped[list["Notification"]] = relationship( #type: ignore
        "Notification", back_populates="user", cascade="all, delete-orphan", passive_deletes=True) 

    # Relación uno a muchos con la tabla de reservas
    reservations: Mapped[list["Reservation"]] = relationship( #type: ignore
        "Reservation", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)