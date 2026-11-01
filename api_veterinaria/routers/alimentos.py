import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import AlimentoEntrada, AlimentoRespuesta
from modelos.alimento import Alimento
from repositorios.alimentos import RepositorioAlimentos

router = APIRouter(prefix="/alimentos", tags=["Nutrición"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioAlimentos, None, None]:
    yield RepositorioAlimentos(connection)


@router.get("/", response_model=list[AlimentoRespuesta])
def listar_alimentos(
    repositorio: RepositorioAlimentos = Depends(obtener_repositorio),
) -> list[Alimento]:
    return repositorio.listar()


@router.get("/{alimento_id}", response_model=AlimentoRespuesta)
def obtener_alimento(
    alimento_id: int,
    repositorio: RepositorioAlimentos = Depends(obtener_repositorio),
) -> Alimento:
    alimento = repositorio.obtener_por_id(alimento_id)
    if alimento is None:
        raise HTTPException(status_code=404, detail="No se encontró el alimento.")
    return alimento


@router.post(
    "/",
    response_model=AlimentoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_alimento(
    datos: AlimentoEntrada,
    repositorio: RepositorioAlimentos = Depends(obtener_repositorio),
) -> Alimento:
    return repositorio.crear(Alimento(id=None, **datos.model_dump()))


@router.put("/{alimento_id}", response_model=AlimentoRespuesta)
def actualizar_alimento(
    alimento_id: int,
    datos: AlimentoEntrada,
    repositorio: RepositorioAlimentos = Depends(obtener_repositorio),
) -> Alimento:
    alimento = repositorio.actualizar(
        alimento_id,
        Alimento(id=alimento_id, **datos.model_dump()),
    )
    if alimento is None:
        raise HTTPException(status_code=404, detail="No se encontró el alimento.")
    return alimento


@router.delete("/{alimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_alimento(
    alimento_id: int,
    repositorio: RepositorioAlimentos = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(alimento_id):
        raise HTTPException(status_code=404, detail="No se encontró el alimento.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
