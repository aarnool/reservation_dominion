from datetime import UTC, datetime, timedelta

import jwt
import magic
from fastapi import HTTPException, UploadFile, status
from pwdlib import PasswordHash

from src.config import settings

SECRET_KEY = settings.SECRET_KEY.get_secret_value()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
password_hasher = PasswordHash.recommended()
DUMMY_HASH = password_hasher.hash("dummy_password")


# Crear un hash de contraseña
def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


# Verificar la contraseña ingresada con el hash almacenado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


# Crear un token de acceso JWT
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):

    # Crear variable con una copia de los datos
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        minutes=expires_delta
    )  # Establecer la fecha de expiración del token
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependecia para obtener el MIME type del archivo subido, si no es un archivo valido lanza una excepcion
class FileTypeValidator:
    def __init__(self, allowed_types: list[str]):
        self.allowed_types = allowed_types

    async def __call__(self, file: UploadFile | None = None) -> UploadFile | None:
        if file is None:
            return None

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
