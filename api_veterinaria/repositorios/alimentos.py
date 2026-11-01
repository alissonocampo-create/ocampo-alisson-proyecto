import sqlite3

from modelos.alimento import Alimento
from repositorios.base import RepositorioBase


class RepositorioAlimentos(RepositorioBase[Alimento]):
    @property
    def table_name(self) -> str:
        return "alimentos"

    @property
    def columns(self) -> tuple[str, ...]:
        return (
            "nombre",
            "categoria",
            "especie",
            "etapa",
            "descripcion",
            "uso",
            "precio",
            "stock",
            "activo",
            "imagen_url",
        )

    def to_values(self, entity: Alimento) -> tuple[object, ...]:
        return (
            entity.nombre,
            entity.categoria,
            entity.especie,
            entity.etapa,
            entity.descripcion,
            entity.uso,
            entity.precio,
            entity.stock,
            int(entity.activo),
            entity.imagen_url,
        )

    def from_row(self, row: sqlite3.Row) -> Alimento:
        return Alimento(
            id=row["id"],
            nombre=row["nombre"],
            categoria=row["categoria"],
            especie=row["especie"],
            etapa=row["etapa"],
            descripcion=row["descripcion"],
            uso=row["uso"],
            precio=row["precio"],
            stock=row["stock"],
            activo=bool(row["activo"]),
            imagen_url=row["imagen_url"],
        )
