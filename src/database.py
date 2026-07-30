from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase
from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


#Creación de la URL de conexión a la base de datos utilizando los valores de configuración
DATABASE_URL = URL.create(
    drivername="mysql+aiomysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD.get_secret_value(),
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME)


# Creación del motor de base de datos asíncrono y la sesión de base de datos
engine = create_async_engine(
    DATABASE_URL
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False, #No se realiza un commit automáticamente después de cada operación de la sesión
    expire_on_commit=False) #No se expiren los objetos de la session después de un commit


# Definición de la clase base para los modelos de SQLAlchemy
class Base(DeclarativeBase):
    pass