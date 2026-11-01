import sqlite3
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Response, status

from database import get_db
from esquemas import ProductoVeterinarioEntrada, ProductoVeterinarioRespuesta
from modelos.producto_veterinario import ProductoVeterinario
from repositorios.productos_veterinarios import RepositorioProductosVeterinarios

router = APIRouter(prefix="/productos-veterinarios", tags=["Farmacia"])


def obtener_repositorio(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[RepositorioProductosVeterinarios, None, None]:
    yield RepositorioProductosVeterinarios(connection)


@router.get("/", response_model=list[ProductoVeterinarioRespuesta])
def listar_productos(
    repositorio: RepositorioProductosVeterinarios = Depends(obtener_repositorio),
) -> list[ProductoVeterinario]:
    return repositorio.listar()


@router.get("/{producto_id}", response_model=ProductoVeterinarioRespuesta)
def obtener_producto(
    producto_id: int,
    repositorio: RepositorioProductosVeterinarios = Depends(obtener_repositorio),
) -> ProductoVeterinario:
    producto = repositorio.obtener_por_id(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    return producto


@router.post(
    "/",
    response_model=ProductoVeterinarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    datos: ProductoVeterinarioEntrada,
    repositorio: RepositorioProductosVeterinarios = Depends(obtener_repositorio),
) -> ProductoVeterinario:
    return repositorio.crear(ProductoVeterinario(id=None, **datos.model_dump()))


@router.put("/{producto_id}", response_model=ProductoVeterinarioRespuesta)
def actualizar_producto(
    producto_id: int,
    datos: ProductoVeterinarioEntrada,
    repositorio: RepositorioProductosVeterinarios = Depends(obtener_repositorio),
) -> ProductoVeterinario:
    producto = repositorio.actualizar(
        producto_id,
        ProductoVeterinario(id=producto_id, **datos.model_dump()),
    )
    if producto is None:
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    repositorio: RepositorioProductosVeterinarios = Depends(obtener_repositorio),
) -> Response:
    if not repositorio.eliminar(producto_id):
        raise HTTPException(status_code=404, detail="No se encontró el producto.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
