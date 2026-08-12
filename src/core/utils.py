import secrets
import string
from datetime import UTC

import boto3
from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from src.config import settings


class TZDateTime(TypeDecorator):
    """
    DateTime que siempre devuelve datetimes con timezone UTC.

    SQLite no soporta timezone nativo, por lo que al leer un datetime
    puede llegar sin tzinfo (naïve). Este TypeDecorator re-inyecta UTC
    automáticamente para que sea compatible con AwareDatetime de Pydantic.

    En bases de datos que sí soportan timezone,
    el valor ya viene con tzinfo y este decorator no hace nada extra.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


# Configuracion de boto3 para usar R2 de Cloudflare
def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY.get_secret_value(),
        region_name="auto",  # R2 no requiere una región específica, pero boto3 necesita un valor
    )


def generate_random_reservation_code():
    """
    Genera un código de reserva aleatorio de 10 caracteres que incluye letras mayúsculas,
    minúsculas, dígitos y caracteres especiales.

    Returns:
        str: Cadena aleatoria generada.
    """
    # Define el conjunto de caracteres que se pueden usar para generar el código alfabeto ASCII y dígitos 0-9
    characters = string.ascii_letters + string.digits
    reservation_code = ""
    # Genera un código de 10 caracteres aleatorios
    for _ in range(10):
        reservation_code += secrets.choice(characters)
    return reservation_code
