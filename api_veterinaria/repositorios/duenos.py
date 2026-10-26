import sqlite3

from modelos.dueno import Dueno
from repositorios.base import RepositorioBase


class RepositorioDuenos(RepositorioBase[Dueno]):
    @property
    def table_name(self) -> str:
        return "duenos"

    @property
    def columns(self) -> tuple[str, ...]:
        return ("nombre", "telefono", "direccion")

    def to_values(self, entity: Dueno) -> tuple[object, ...]:
        return (entity.nombre, entity.telefono, entity.direccion)

    def from_row(self, row: sqlite3.Row) -> Dueno:
        return Dueno(
            id=row["id"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            direccion=row["direccion"],
        )
