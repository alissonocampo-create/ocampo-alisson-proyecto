import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import MascotaEntrada, MascotaRespuesta
from modelos.mascota import Mascota
from repositorios.mascotas import RepositorioMascotas

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioMascotas, None, None]:
    yield RepositorioMascotas(connection)


@router.get("/", response_model=list[MascotaRespuesta])
def listar_mascotas(
    repositorio: RepositorioMascotas = Depends(obtener_repositorio),
) -> list[Mascota]:
    return repositorio.listar()


@router.get("/{mascota_id}", response_model=MascotaRespuesta)
def obtener_mascota(
    mascota_id: int,
    repositorio: RepositorioMascotas = Depends(obtener_repositorio),
) -> Mascota:
    mascota = repositorio.obtener_por_id(mascota_id)
    if mascota is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    return mascota


@router.post(
    "/",
    response_model=MascotaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_mascota(
    datos: MascotaEntrada,
    repositorio: RepositorioMascotas = Depends(obtener_repositorio),
) -> Mascota:
    if not repositorio.existe_dueno(datos.dueno_id):
        raise HTTPException(status_code=404, detail="No se encontró el dueño.")
    return repositorio.crear(
        Mascota(id=None, **datos.model_dump()),
    )


@router.put("/{mascota_id}", response_model=MascotaRespuesta)
def actualizar_mascota(
    mascota_id: int,
    datos: MascotaEntrada,
    repositorio: RepositorioMascotas = Depends(obtener_repositorio),
) -> Mascota:
    if not repositorio.existe_dueno(datos.dueno_id):
        raise HTTPException(status_code=404, detail="No se encontró el dueño.")
    mascota = repositorio.actualizar(
        mascota_id,
        Mascota(id=mascota_id, **datos.model_dump()),
    )
    if mascota is None:
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    return mascota


@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mascota(
    mascota_id: int,
    repositorio: RepositorioMascotas = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(mascota_id):
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
