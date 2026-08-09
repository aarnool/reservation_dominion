from collections.abc import AsyncGenerator

import jwt
from fastapi import File, HTTPException, Request, UploadFile, status
from fastapi.security import SecurityScopes
import magic
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import ALGORITHM, SECRET_KEY
from src.database import SessionLocal


# Dependencia para obtener la sesión de base de datos de manera segura y asincrónica se cierra despues de usarla
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


# Dependencia para obtener el usuario actual a partir del token de acceso JWT y verificar los scopes de seguridad
async def get_current_user(request: Request, security_scopes: SecurityScopes) -> dict:
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


# Dependecia para obtener el MIME type del archivo subido, si no es un archivo valido lanza una excepcion
class FileTypeValidator:
    def __init__(self, allowed_types: list[str]):
        self.allowed_types = allowed_types

    async def __call__(self, file: UploadFile = File()) -> UploadFile:
        # Leer cabecera para chequear el Magic Number
        header_bytes = await file.read(2048)
        await file.seek(0)  # Resetear cursor

        # Detectar tipo real
        detected_mime = magic.from_buffer(header_bytes, mime=True)

        if detected_mime not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo no válido. Tipo detectado: {detected_mime}",
            )

        return file


valiate_image_file = FileTypeValidator(
    allowed_types=["image/jpeg", "image/png", "image/webp", "image/jpg"]
)
