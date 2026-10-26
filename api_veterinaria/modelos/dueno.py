from dataclasses import dataclass


@dataclass(slots=True)
class Dueno:
    id: int | None
    nombre: str
    telefono: str
    direccion: str | None = None
