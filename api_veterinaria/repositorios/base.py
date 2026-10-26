import sqlite3
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Entity = TypeVar("Entity")


class RepositorioBase(ABC, Generic[Entity]):
    """Shared parameterized CRUD operations for a single database table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def columns(self) -> tuple[str, ...]:
        raise NotImplementedError

    @abstractmethod
    def to_values(self, entity: Entity) -> tuple[object, ...]:
        raise NotImplementedError

    @abstractmethod
    def from_row(self, row: sqlite3.Row) -> Entity:
        raise NotImplementedError

    def listar(self) -> list[Entity]:
        rows = self.connection.execute(
            f"SELECT * FROM {self.table_name} ORDER BY id"
        ).fetchall()
        return [self.from_row(row) for row in rows]

    def obtener_por_id(self, entity_id: int) -> Entity | None:
        row = self.connection.execute(
            f"SELECT * FROM {self.table_name} WHERE id = ?",
            (entity_id,),
        ).fetchone()
        return self.from_row(row) if row is not None else None

    def crear(self, entity: Entity) -> Entity:
        placeholders = ", ".join("?" for _ in self.columns)
        columns = ", ".join(self.columns)
        cursor = self.connection.execute(
            f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
            self.to_values(entity),
        )
        self.connection.commit()
        entity_id = cursor.lastrowid
        if entity_id is None:
            raise RuntimeError("La base de datos no devolvió el identificador creado.")
        created = self.obtener_por_id(entity_id)
        if created is None:
            raise RuntimeError("No se pudo recuperar el registro recién creado.")
        return created

    def actualizar(self, entity_id: int, entity: Entity) -> Entity | None:
        assignments = ", ".join(f"{column} = ?" for column in self.columns)
        cursor = self.connection.execute(
            f"UPDATE {self.table_name} SET {assignments} WHERE id = ?",
            (*self.to_values(entity), entity_id),
        )
        if cursor.rowcount == 0:
            return None
        self.connection.commit()
        return self.obtener_por_id(entity_id)

    def eliminar(self, entity_id: int) -> bool:
        cursor = self.connection.execute(
            f"DELETE FROM {self.table_name} WHERE id = ?",
            (entity_id,),
        )
        if cursor.rowcount == 0:
            return False
        self.connection.commit()
        return True
