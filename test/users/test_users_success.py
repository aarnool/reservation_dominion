from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.domains.auth.models import User


# Prueba obtener la lista de usuarios como administrador con paginación
async def test_get_all_users_success(
    admin_client: AsyncClient, db_session: AsyncSession
):
    user1 = User(
        username="userone",
        email="userone@example.com",
        first_name="User",
        last_name="One",
        password=get_password_hash("password123"),
    )
    user2 = User(
        username="usertwo",
        email="usertwo@example.com",
        first_name="User",
        last_name="Two",
        password=get_password_hash("password123"),
    )
    db_session.add_all([user1, user2])
    await db_session.commit()

    response = await admin_client.get("/users/?start=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert "X-Total-Count" in response.headers


# Prueba obtener un usuario específico por ID como administrador
async def test_get_user_by_id_success(
    admin_client: AsyncClient, db_session: AsyncSession
):
    user = User(
        username="userbyid",
        email="userbyid@example.com",
        first_name="User",
        last_name="ByID",
        password=get_password_hash("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await admin_client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "userbyid"
    assert data["email"] == "userbyid@example.com"
