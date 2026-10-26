from contextlib import asynccontextmanager
import sqlite3
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database import initialize_database
from routers import duenos, mascotas


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
def inicio() -> dict[str, str]:
    return {"mensaje": "API de Clínica Veterinaria", "documentacion": "/docs"}


app.include_router(duenos.router)
app.include_router(mascotas.router)
