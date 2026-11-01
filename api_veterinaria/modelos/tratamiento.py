from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Tratamiento:
    id: int | None
    mascota_id: int
    producto_id: int | None
    nombre: str
    indicaciones: str
    dosis: str | None
    fecha_inicio: date
    fecha_fin: date | None
    estado: str
