from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.database import Base

# Tabla de Roles donde se almacenan los diferentes roles que pueden tener los usuarios del sistema
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación uno a muchos con la tabla de usuarios
    users: Mapped[list["User"]] = relationship("User", back_populates="role") #type: ignore

    # Relación muchos a muchos con la tabla de permisos a través de la tabla intermedia role_permissions
    permissions_association: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan", passive_deletes=True)

   

# Tabla de Permisos donde se almacenan los diferentes permisos que pueden tener los roles del sistema
class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación muchos a muchos con la tabla de roles a través de la tabla intermedia role_permissions
    roles_association: Mapped[list["RolePermission"]] = relationship(
        "RolePermission" ,back_populates="permission", cascade="all, delete-orphan", passive_deletes=True)
  


# Tabla intermedia para la relación muchos a muchos entre roles y permisos
class RolePermission(Base):
    __tablename__ = "role_permissions"


    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

    # Relación muchos a uno con la tabla de roles
    role: Mapped["Role"] = relationship("Role", back_populates="permissions_association")
    # Relación muchos a uno con la tabla de permisos
    permission: Mapped["Permission"] = relationship("Permission", back_populates="roles_association")








