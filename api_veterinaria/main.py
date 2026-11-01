from contextlib import asynccontextmanager
import hashlib
import sqlite3
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

import database
from database import initialize_database
from routers import (
    agenda,
    accesorios,
    alimentos,
    asistente,
    autenticacion,
    duenos,
    mascotas,
    productos_veterinarios,
    reportes,
    respaldos,
    tratamientos,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
IMAGE_FORMATS = {
    "image/jpeg": (".jpg", lambda content: content.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda content: content.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (
        ".webp",
        lambda content: content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    ),
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="API de Clínica Veterinaria",
    description="Gestión de dueños y mascotas de una clínica veterinaria.",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AutenticacionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if (
            path == "/"
            or path.startswith("/static/")
            or path in {"/docs", "/openapi.json", "/redoc", "/docs/oauth2-redirect"}
            or path == "/auth/login"
            or request.method == "OPTIONS"
        ):
            return await call_next(request)

        token = request.cookies.get(autenticacion.SESSION_COOKIE)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Inicia sesión para continuar."},
            )

        token_hash = hashlib.sha256(token.encode("ascii", errors="ignore")).hexdigest()
        connection = sqlite3.connect(database.DATABASE_PATH, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            user = connection.execute(
                """
                SELECT u.id, u.nombre_usuario, u.nombre_completo, u.rol
                FROM sesiones s
                JOIN usuarios u ON u.id = s.usuario_id
                WHERE s.token_hash = ? AND s.expira_en > ? AND u.activo = 1
                """,
                (token_hash, datetime.now(timezone.utc).isoformat()),
            ).fetchone()
        finally:
            connection.close()

        if user is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "La sesión venció. Inicia sesión nuevamente."},
            )
        current_user = dict(user)
        request.state.user = current_user
        method = request.method
        role = current_user["rol"]
        if role != "administrador":
            if path.startswith(("/auth/usuarios", "/respaldos")):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Esta acción requiere permisos de administración."},
                )
            if method not in {"GET", "HEAD"}:
                allowed = path.startswith(("/auth/password", "/auth/logout"))
                if role == "recepcion":
                    allowed = allowed or (
                        method in {"POST", "PUT"}
                        and path.startswith(
                            ("/duenos/", "/mascotas/", "/citas/", "/imagenes/")
                        )
                    )
                elif role == "veterinario":
                    allowed = allowed or path.startswith(
                        (
                            "/duenos/",
                            "/mascotas/",
                            "/citas/",
                            "/vacunas/",
                            "/tratamientos/",
                            "/imagenes/",
                        )
                    )
                if not allowed:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Tu perfil no tiene permiso para esta acción."},
                    )
        return await call_next(request)


app.add_middleware(AutenticacionMiddleware)


@app.exception_handler(sqlite3.IntegrityError)
async def manejar_conflicto_de_integridad(
    _: Request,
    exception: sqlite3.IntegrityError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "La operación no se pudo completar porque viola una regla "
                "de integridad de la base de datos."
            )
        },
    )


@app.get("/", tags=["Inicio"])
def inicio() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/imagenes/", tags=["Imágenes"])
async def subir_imagen(request: Request) -> dict[str, str]:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip()
    image_format = IMAGE_FORMATS.get(content_type)
    if image_format is None:
        return JSONResponse(
            status_code=415,
            content={"detail": "Usa una imagen JPG, PNG o WebP."},
        )

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_size = int(content_length)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail="La longitud del archivo no es válida.",
            ) from error
        if declared_size < 0:
            raise HTTPException(
                status_code=400,
                detail="La longitud del archivo no es válida.",
            )
        if declared_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="La imagen no puede superar los 5 MB.",
            )

    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="La imagen no puede superar los 5 MB.",
            )
        content.extend(chunk)

    extension, matches_signature = image_format
    if not matches_signature(content):
        raise HTTPException(
            status_code=415,
            detail="El archivo no coincide con el formato de imagen.",
        )

    filename = f"{uuid.uuid4().hex}{extension}"
    upload_directory = STATIC_DIR / "images" / "uploads"
    upload_directory.mkdir(parents=True, exist_ok=True)
    (upload_directory / filename).write_bytes(content)
    return {"imagen_url": f"/static/images/uploads/{filename}"}


app.include_router(duenos.router)
app.include_router(mascotas.router)
app.include_router(accesorios.router)
app.include_router(alimentos.router)
app.include_router(productos_veterinarios.router)
app.include_router(tratamientos.router)
app.include_router(asistente.router)
app.include_router(agenda.router)
app.include_router(autenticacion.router)
app.include_router(reportes.router)
app.include_router(respaldos.router)
