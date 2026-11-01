from dataclasses import dataclass


@dataclass(slots=True)
class Accesorio:
    id: int | None
    nombre: str
    categoria: str
    descripcion: str
    uso: str
    precio: float
    stock: int
    activo: bool
    imagen_url: str | None = None
