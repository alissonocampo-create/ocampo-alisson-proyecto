import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import AccesorioEntrada, AccesorioRespuesta
from modelos.accesorio import Accesorio
from repositorios.accesorios import RepositorioAccesorios

router = APIRouter(prefix="/accesorios", tags=["Accesorios"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioAccesorios, None, None]:
    yield RepositorioAccesorios(connection)


@router.get("/", response_model=list[AccesorioRespuesta])
def listar_accesorios(
    repositorio: RepositorioAccesorios = Depends(obtener_repositorio),
) -> list[Accesorio]:
    return repositorio.listar()


@router.get("/{accesorio_id}", response_model=AccesorioRespuesta)
def obtener_accesorio(
    accesorio_id: int,
    repositorio: RepositorioAccesorios = Depends(obtener_repositorio),
) -> Accesorio:
    accesorio = repositorio.obtener_por_id(accesorio_id)
    if accesorio is None:
        raise HTTPException(status_code=404, detail="No se encontró el accesorio.")
    return accesorio


@router.post(
    "/",
    response_model=AccesorioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_accesorio(
    datos: AccesorioEntrada,
    repositorio: RepositorioAccesorios = Depends(obtener_repositorio),
) -> Accesorio:
    return repositorio.crear(Accesorio(id=None, **datos.model_dump()))


@router.put("/{accesorio_id}", response_model=AccesorioRespuesta)
def actualizar_accesorio(
    accesorio_id: int,
    datos: AccesorioEntrada,
    repositorio: RepositorioAccesorios = Depends(obtener_repositorio),
) -> Accesorio:
    accesorio = repositorio.actualizar(
        accesorio_id,
        Accesorio(id=accesorio_id, **datos.model_dump()),
    )
    if accesorio is None:
        raise HTTPException(status_code=404, detail="No se encontró el accesorio.")
    return accesorio


@router.delete("/{accesorio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_accesorio(
    accesorio_id: int,
    repositorio: RepositorioAccesorios = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(accesorio_id):
        raise HTTPException(status_code=404, detail="No se encontró el accesorio.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
