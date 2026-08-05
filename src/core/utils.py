from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator
from datetime import timezone


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
            return value.replace(tzinfo=timezone.utc)
        return value
