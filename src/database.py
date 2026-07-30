from sqlalchemy.engine import URL
from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


DATABASE_URL = URL.create(
    drivername="mysql+aiomysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD.get_secret_value(),
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME)

engine = create_async_engine(
    DATABASE_URL
)

Session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    expire_on_commit=False)
