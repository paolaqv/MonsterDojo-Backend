import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.supabase import get_supabase_client
from app.db.session import get_db
from app.logs.application.service import registrar_aplicacion
from app.modules.auth.permissions import require_any_permission
from app.modules.users.model import Usuario


router = APIRouter(prefix="/uploads", tags=["Uploads"])


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

MAX_BYTES = 5 * 1024 * 1024  # 5 MB

ALLOWED_SUBFOLDERS: dict[str, str] = {
    "producto": "productos",
    "juego": "juegos",
}


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    tipo: Literal["producto", "juego"] = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_any_permission("gestionar_productos", "gestionar_juegos")
    ),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Usa JPG, PNG o WEBP.",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo esta vacio.",
        )
    if len(contents) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo supera el limite de 5 MB.",
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    subfolder = ALLOWED_SUBFOLDERS[tipo]
    object_path = f"{subfolder}/{uuid.uuid4().hex}.{extension}"

    settings = get_settings()
    bucket = settings.supabase_bucket
    supabase = get_supabase_client()

    try:
        supabase.storage.from_(bucket).upload(
            path=object_path,
            file=contents,
            file_options={"content-type": file.content_type, "upsert": "false"},
        )
        public_url = supabase.storage.from_(bucket).get_public_url(object_path)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo subir la imagen al almacenamiento.",
        )

    if isinstance(public_url, str):
        public_url = public_url.rstrip("?")

    registrar_aplicacion(
        db,
        modulo="uploads",
        evento="ARCHIVO_SUBIDO",
        descripcion=(
            f"Usuario {current_user.id_usuario} subio imagen para {tipo} "
            f"({len(contents)} bytes). Ruta: {object_path}"
        ),
        severidad="INFO",
        estado="OK",
        usuario_id=current_user.id_usuario,
        entidad_afectada=f"imagen_{tipo}",
        # entidad_id es INTEGER ahora; el path va en la descripción.
    )

    return {"url": public_url, "path": object_path}
