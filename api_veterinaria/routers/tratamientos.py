import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import TratamientoEntrada, TratamientoRespuesta
from modelos.tratamiento import Tratamiento
from repositorios.tratamientos import RepositorioTratamientos

router = APIRouter(prefix="/tratamientos", tags=["Tratamientos"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioTratamientos, None, None]:
    yield RepositorioTratamientos(connection)


def validar_referencias(
    datos: TratamientoEntrada,
    repositorio: RepositorioTratamientos,
) -> None:
    if not repositorio.existe_mascota(datos.mascota_id):
        raise HTTPException(status_code=404, detail="No se encontró la mascota.")
    if datos.producto_id is not None and not repositorio.existe_producto(
        datos.producto_id
    ):
        raise HTTPException(status_code=404, detail="No se encontró el producto.")


@router.get("/", response_model=list[TratamientoRespuesta])
def listar_tratamientos(
    repositorio: RepositorioTratamientos = Depends(obtener_repositorio),
) -> list[Tratamiento]:
    return repositorio.listar()


@router.get("/{tratamiento_id}", response_model=TratamientoRespuesta)
def obtener_tratamiento(
    tratamiento_id: int,
    repositorio: RepositorioTratamientos = Depends(obtener_repositorio),
) -> Tratamiento:
    tratamiento = repositorio.obtener_por_id(tratamiento_id)
    if tratamiento is None:
        raise HTTPException(status_code=404, detail="No se encontró el tratamiento.")
    return tratamiento


@router.post(
    "/",
    response_model=TratamientoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_tratamiento(
    datos: TratamientoEntrada,
    repositorio: RepositorioTratamientos = Depends(obtener_repositorio),
) -> Tratamiento:
    validar_referencias(datos, repositorio)
    return repositorio.crear(Tratamiento(id=None, **datos.model_dump()))


@router.put("/{tratamiento_id}", response_model=TratamientoRespuesta)
def actualizar_tratamiento(
    tratamiento_id: int,
    datos: TratamientoEntrada,
    repositorio: RepositorioTratamientos = Depends(obtener_repositorio),
) -> Tratamiento:
    validar_referencias(datos, repositorio)
    tratamiento = repositorio.actualizar(
        tratamiento_id,
        Tratamiento(id=tratamiento_id, **datos.model_dump()),
    )
    if tratamiento is None:
        raise HTTPException(status_code=404, detail="No se encontró el tratamiento.")
    return tratamiento


@router.delete("/{tratamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tratamiento(
    tratamiento_id: int,
    repositorio: RepositorioTratamientos = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(tratamiento_id):
        raise HTTPException(status_code=404, detail="No se encontró el tratamiento.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
