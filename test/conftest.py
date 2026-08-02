from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from src.models import *
from src.database import Base
from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
from src.core.security import create_access_token
from src.domains.auth.service import ROLES_SCOOPES



DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    autocommit=False, 
    expire_on_commit=False)



@pytest.fixture()
async def reset_rate_limiter():
    """
    Fixture para reiniciar el limitador de velocidad antes de cada prueba.
    """
    pass

@pytest_asyncio.fixture()
async def db_session():
    """
    Fixture para proporcionar una sesión de base de datos para las pruebas.
    """
    # 1. Crear las tablas en la base de datos en memoria
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 1.1 Insertar roles por defecto
    from src.domains.auth.models import Role
    async with TestingSessionLocal() as session:
        session.add(Role(id=1, name="user", description="Usuario regular"))
        session.add(Role(id=2, name="admin", description="Administrador del sistema"))
        await session.commit()

    # 2. Levantar la sesión asíncrona para el test
    async with TestingSessionLocal() as session:
        yield session

    # 3. Limpiar las tablas después de que el test termine
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession):
    """
    Fixture para proporcionar un cliente de prueba de FastAPI con la sesión de base de datos inyectada.
    """
    from src.main import app
    from src.dependencies import get_db

    # Inyectar la sesión de base de datos en la aplicación FastAPI
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://test"
    ) as test_client:

        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def admin_client(client: AsyncClient):
    """Fixture que proporciona un cliente con sesión de Administrador."""
    token = create_access_token(data={
        "sub": "admin_test",
        "id": 1,
        "role": "admin",
        "scopes": ROLES_SCOOPES["admin"]
    })
    client.cookies.set("auth_token", token)
    return client

@pytest_asyncio.fixture()
async def user_client(client: AsyncClient):
    """Fixture que proporciona un cliente con sesión de Usuario normal."""
    token = create_access_token(data={
        "sub": "user_test",
        "id": 2,
        "role": "user",
        "scopes": ROLES_SCOOPES["user"]
    })
    client.cookies.set("auth_token", token)
    return client