
from fastapi import Request, Depends, Response, HTTPException, status
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.database import SessionLocal
from src.dependencies import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from src.models import User
from src.core.security import verify_password, create_access_token, DUMMY_HASH, get_password_hash
from src.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from src.domains.auth.schemas import UserCreate, UserResponse
from src.domains.auth.models import User, Role
from src.core.permissions import ROLES_SCOOPES

# Autentificador de usuario (Ver si existe en la base de datos y si la contraseña es correcta)
async def authenticate_user(
    db: AsyncSession,
    username: str, 
    password: str
):
    """
    
    Autentica a un usuario verificando su nombre de usuario y contraseña.
    Args:
        db (AsyncSession): Sesión de base de datos asincrónica.
        username (str): Nombre de usuario del usuario a autenticar.
        password (str): Contraseña del usuario a autenticar.
    Raises:
        HTTPException: Si el usuario no se encuentra o la contraseña es incorrecta.
    Returns:
        User: Objeto de usuario autenticado.
    
    """

    smtm = (
        select(User)
        .options(selectinload(User.role))  # Cargar la relación de rol del usuario para usarse en la generación del token
        .where(User.username == username)
    )
    
    user = await db.scalar(smtm)
    if not user:
        verify_password(password, DUMMY_HASH) # Verifica la contraseña para evitar ataques de temporización
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
    

# Inicia sesión de usuario y genera un token de acceso JWT, luego lo establece como una cookie de Response
async def login_user(
    response: Response,
    db: AsyncSession,
    form_data: OAuth2PasswordRequestForm,
):
    """

    Inicia sesión de usuario y genera un token de acceso JWT, luego lo establece como una cookie de Response.
    Args:
        response (Response): Objeto de respuesta de FastAPI.
        db (AsyncSession): Sesión de base de datos asincrónica.
        form_data (OAuth2PasswordRequestForm): Datos del formulario de inicio de sesión.
    Raises:
        HTTPException: Si el usuario no se encuentra o la contraseña es incorrecta.
    Returns:
   
        None: No retorna ningún valor, pero establece una cookie de autenticación en la respuesta.

    """

    user = await authenticate_user(db, form_data.username, form_data.password)

    user_scopes = ROLES_SCOOPES.get(user.role.name, [])

    auth_token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "role": user.role.name,
            "scopes": user_scopes}
    )

    response.set_cookie(
        key="auth_token",
        value=auth_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )



# Crea un nuevo usuario en la base de datos 
async def create_user(
  user_create: UserCreate,
  db: AsyncSession  
):
    """

    Crea un nuevo usuario en la base de datos.
    Args:
        user_create (UserCreate): Objeto que contiene los datos del usuario a crear.
        db (AsyncSession): Sesión de base de datos asincrónica.
    Raises:
        HTTPException: Si el nombre de usuario o correo electrónico ya está en uso.
    Returns:
        User: Objeto del usuario recién creado.
        
    """

    smtm_user = select(User).where(User.username == user_create.username)
    existing_user = await db.scalar(smtm_user)
    smtm_email = select(User).where(User.email == user_create.email)
    existing_user_email = await db.scalar(smtm_email)

    if existing_user or existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario/cooreo ya está en uso"
        )
    password_hash = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        password=password_hash,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user