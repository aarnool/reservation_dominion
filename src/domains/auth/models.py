from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import settings
from src.database import Base


# Tabla de Roles donde se almacenan los diferentes roles que pueden tener los usuarios del sistema
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relación uno a muchos con la tabla de usuarios
    users: Mapped[list["User"]] = relationship("User", back_populates="role")  # type: ignore  # noqa: UP037


# Tabla de Usuarios donde se almacenan los datos de los usuarios del sistema
class User(Base):
    __tablename__ = "users"

    # Columnas de la tabla de usuarios
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False, index=True, default=1
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Combinar el uuid del avatar con la URL base para obtener la URL completa del avatar
    @hybrid_property
    def avatar_full_url(self):  # type: ignore
        if self.avatar_url:
            return f"{settings.R2_PUBLIC_DOMAIN}/{self.avatar_url}"
        return None

    @avatar_full_url.expression
    def avatar_full_url(cls):
        return func.concat(settings.R2_PUBLIC_DOMAIN, "/", cls.avatar_url)

    # Relación muchos a uno con la tabla de roles
    role: Mapped["Role"] = relationship("Role", back_populates="users")  # type: ignore  # noqa: UP037

    # Relación uno a muchos con la tabla de notificaciones
    notifications: Mapped[list["Notification"]] = relationship(  # type: ignore  # noqa: F821, UP037
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Relación uno a muchos con la tabla de reservas
    reservations: Mapped[list["Reservation"]] = relationship(  # type: ignore  # noqa: F821, UP037
        "Reservation",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
