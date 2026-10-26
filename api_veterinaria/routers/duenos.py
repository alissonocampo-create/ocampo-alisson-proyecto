import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import DuenoEntrada, DuenoRespuesta
from modelos.dueno import Dueno
from repositorios.duenos import RepositorioDuenos

router = APIRouter(prefix="/duenos", tags=["Dueños"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioDuenos, None, None]:
    yield RepositorioDuenos(connection)


@router.get("/", response_model=list[DuenoRespuesta])
def listar_duenos(
    repositorio: RepositorioDuenos = Depends(obtener_repositorio),
) -> list[Dueno]:
    return repositorio.listar()


@router.get("/{dueno_id}", response_model=DuenoRespuesta)
def obtener_dueno(
    dueno_id: int,
    repositorio: RepositorioDuenos = Depends(obtener_repositorio),
) -> Dueno:
    dueno = repositorio.obtener_por_id(dueno_id)
    if dueno is None:
        raise HTTPException(status_code=404, detail="No se encontró el dueño.")
    return dueno


@router.post(
    "/",
    response_model=DuenoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_dueno(
    datos: DuenoEntrada,
    repositorio: RepositorioDuenos = Depends(obtener_repositorio),
) -> Dueno:
    return repositorio.crear(Dueno(id=None, **datos.model_dump()))


@router.put("/{dueno_id}", response_model=DuenoRespuesta)
def actualizar_dueno(
    dueno_id: int,
    datos: DuenoEntrada,
    repositorio: RepositorioDuenos = Depends(obtener_repositorio),
) -> Dueno:
    dueno = repositorio.actualizar(
        dueno_id,
        Dueno(id=dueno_id, **datos.model_dump()),
    )
    if dueno is None:
        raise HTTPException(status_code=404, detail="No se encontró el dueño.")
    return dueno


@router.delete("/{dueno_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_dueno(
    dueno_id: int,
    repositorio: RepositorioDuenos = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(dueno_id):
        raise HTTPException(status_code=404, detail="No se encontró el dueño.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
