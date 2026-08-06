from sqlalchemy import MetaData
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# Creación de la URL de conexión a la base de datos utilizando los valores de configuración
DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD.get_secret_value(),
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)


# Creación del motor de base de datos asíncrono y la sesión de base de datos
engine = create_async_engine(DATABASE_URL)


# Creación de la sesión de base de datos asíncrona utilizando el motor de base de datos
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,  # No se realiza un commit automáticamente después de cada operación de la sesión
    expire_on_commit=False,
)  # No se expiren los objetos de la session después de un commit


# Definición de la convención de nombres para las restricciones y claves en la base de datos
convention = {
    "ix": "ix_%(column_0_label)s",  # ix es para índices
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # uq es para claves únicas
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # ck es para restricciones de comprobación
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # fk es para claves foráneas
    "pk": "pk_%(table_name)s",  # pk es para claves primarias
}

metadata_custom = MetaData(naming_convention=convention)


# Definición de la clase base para los modelos de SQLAlchemy
class Base(DeclarativeBase):
    metadata = metadata_custom
