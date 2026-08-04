from fastapi import APIRouter, Depends, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_db
from src.domains.auth.service import login_user, create_user
from src.domains.auth.schemas import UserCreate, UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Inicia sesión en el sistema"
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """

    Inicia sesión en el sistema autenticando al usuario y generando un token de acceso.
    ### Detalles:
    - **username**: Nombre de usuario del usuario que intenta iniciar sesión.
    - **password**: Contraseña del usuario que intenta iniciar sesión.

    """
    await login_user(response, db, form_data)
    return {
        "message": "Inicio de sesión exitoso"
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un nuevo usuario en el sistema"
)
async def register(
    response: Response,
    user: UserCreate = Body(),
    db: AsyncSession = Depends(get_db)
):
    """

    Registra un nuevo usuario en el sistema.
    ### Detalles:
    - **username**: Nombre de usuario único para el sistema.
    - **email**: Correo electrónico único del usuario.
    - **first_name**: Primer nombre del usuario.
    - **last_name**: Apellido del usuario.
    - **password**: Contraseña del usuario.

    """

    return await create_user(user, db)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cierra sesión en el sistema"
)
async def logout(response: Response):
    """

    Cierra sesión en el sistema eliminando el token de acceso del usuario.
    ### Detalles:
    - Elimina la cookie de autenticación del usuario.

    """
    response.delete_cookie(key="auth_token")

