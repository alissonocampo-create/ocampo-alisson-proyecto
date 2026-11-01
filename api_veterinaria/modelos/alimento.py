from dataclasses import dataclass


@dataclass(slots=True)
class Alimento:
    id: int | None
    nombre: str
    categoria: str
    especie: str
    etapa: str
    descripcion: str
    uso: str
    precio: float
    stock: int
    activo: bool
    imagen_url: str | None = None
