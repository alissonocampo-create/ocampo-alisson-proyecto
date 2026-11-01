import sqlite3
from datetime import date

from modelos.tratamiento import Tratamiento
from repositorios.base import RepositorioBase


class RepositorioTratamientos(RepositorioBase[Tratamiento]):
    @property
    def table_name(self) -> str:
        return "tratamientos"

    @property
    def columns(self) -> tuple[str, ...]:
        return (
            "mascota_id",
            "producto_id",
            "nombre",
            "indicaciones",
            "dosis",
            "fecha_inicio",
            "fecha_fin",
            "estado",
        )

    def to_values(self, entity: Tratamiento) -> tuple[object, ...]:
        return (
            entity.mascota_id,
            entity.producto_id,
            entity.nombre,
            entity.indicaciones,
            entity.dosis,
            entity.fecha_inicio.isoformat(),
            entity.fecha_fin.isoformat() if entity.fecha_fin else None,
            entity.estado,
        )

    def from_row(self, row: sqlite3.Row) -> Tratamiento:
        return Tratamiento(
            id=row["id"],
            mascota_id=row["mascota_id"],
            producto_id=row["producto_id"],
            nombre=row["nombre"],
            indicaciones=row["indicaciones"],
            dosis=row["dosis"],
            fecha_inicio=date.fromisoformat(row["fecha_inicio"]),
            fecha_fin=date.fromisoformat(row["fecha_fin"]) if row["fecha_fin"] else None,
            estado=row["estado"],
        )

    def existe_mascota(self, mascota_id: int) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM mascotas WHERE id = ?",
            (mascota_id,),
        ).fetchone()
        return row is not None

    def existe_producto(self, producto_id: int) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM productos_veterinarios WHERE id = ?",
            (producto_id,),
        ).fetchone()
        return row is not None
