from pwdlib import PasswordHash
import jwt
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
    to_encode = data.copy()
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt