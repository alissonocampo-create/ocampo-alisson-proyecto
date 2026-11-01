from dataclasses import dataclass


@dataclass(slots=True)
class ProductoVeterinario:
    id: int | None
    nombre: str
    categoria: str
    descripcion: str
    uso: str
    precio: float
    stock: int
    activo: bool
    imagen_url: str | None = None
