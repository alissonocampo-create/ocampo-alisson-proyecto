import sqlite3

from modelos.accesorio import Accesorio
from repositorios.base import RepositorioBase


class RepositorioAccesorios(RepositorioBase[Accesorio]):
    @property
    def table_name(self) -> str:
        return "accesorios"

    @property
    def columns(self) -> tuple[str, ...]:
        return (
            "nombre",
            "categoria",
            "descripcion",
            "uso",
            "precio",
            "stock",
            "activo",
            "imagen_url",
        )

    def to_values(self, entity: Accesorio) -> tuple[object, ...]:
        return (
            entity.nombre,
            entity.categoria,
            entity.descripcion,
            entity.uso,
            entity.precio,
            entity.stock,
            int(entity.activo),
            entity.imagen_url,
        )

    def from_row(self, row: sqlite3.Row) -> Accesorio:
        return Accesorio(
            id=row["id"],
            nombre=row["nombre"],
            categoria=row["categoria"],
            descripcion=row["descripcion"],
            uso=row["uso"],
            precio=row["precio"],
            stock=row["stock"],
            activo=bool(row["activo"]),
            imagen_url=row["imagen_url"],
        )
