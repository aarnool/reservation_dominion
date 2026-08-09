from fastapi import UploadFile, HTTPException, status
import magic


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
