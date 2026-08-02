from src.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from fastapi import HTTPException, Request, status
from fastapi.security import SecurityScopes
import jwt
from src.core.security import SECRET_KEY, ALGORITHM


# Dependencia para obtener la sesión de base de datos de manera segura y asincrónica se cierra despues de usarla
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# Dependencia para obtener el usuario actual a partir del token de acceso JWT y verificar los scopes de seguridad
async def get_current_user(
    request: Request, 
    security_scopes: SecurityScopes
) -> dict:
    
    """

    Obtiene el usuario actual a partir del token de acceso JWT y verifica los scopes de seguridad
    Args:
        request (Request): La solicitud HTTP entrante.
        security_scopes (SecurityScopes): Los scopes de seguridad requeridos para acceder a la ruta
    Returns:
        dict: Un diccionario que contiene la información del usuario actual.
    Raises:
        HTTPException: Si el token de acceso es inválido, ha expirado o no tiene los scopes requeridos.

    """

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": authenticate_value},
    )


    try:
        token = request.cookies.get("auth_token")
        if not token:
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        list_scopes = payload.get("scopes", [])

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    
    except jwt.InvalidTokenError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in list_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para realizar esta acción",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return payload