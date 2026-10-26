from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Mascota:
    id: int | None
    nombre: str
    especie: str
    raza: str | None
    fecha_nacimiento: date | None
    dueno_id: int
