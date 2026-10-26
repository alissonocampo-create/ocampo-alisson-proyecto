import sqlite3
from datetime import date

from modelos.mascota import Mascota
from repositorios.base import RepositorioBase


class RepositorioMascotas(RepositorioBase[Mascota]):
    @property
    def table_name(self) -> str:
        return "mascotas"

    @property
    def columns(self) -> tuple[str, ...]:
        return (
            "nombre",
            "especie",
            "raza",
            "fecha_nacimiento",
            "dueno_id",
        )

    def to_values(self, entity: Mascota) -> tuple[object, ...]:
        fecha_nacimiento = (
            entity.fecha_nacimiento.isoformat()
            if entity.fecha_nacimiento is not None
            else None
        )
        return (
            entity.nombre,
            entity.especie,
            entity.raza,
            fecha_nacimiento,
            entity.dueno_id,
        )

    def from_row(self, row: sqlite3.Row) -> Mascota:
        fecha_nacimiento = row["fecha_nacimiento"]
        return Mascota(
            id=row["id"],
            nombre=row["nombre"],
            especie=row["especie"],
            raza=row["raza"],
            fecha_nacimiento=(
                date.fromisoformat(fecha_nacimiento)
                if fecha_nacimiento is not None
                else None
            ),
            dueno_id=row["dueno_id"],
        )

    def existe_dueno(self, dueno_id: int) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM duenos WHERE id = ?",
            (dueno_id,),
        ).fetchone()
        return row is not None
