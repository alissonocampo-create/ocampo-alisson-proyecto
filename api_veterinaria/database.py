import sqlite3
from collections.abc import Generator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "clinica_veterinaria.db"
SCHEMA_PATH = PROJECT_ROOT / "crear_bd.sql"
REQUIRED_TABLES = {
    "duenos",
    "mascotas",
    "veterinarios",
    "citas",
    "vacunas_aplicadas",
    "usuarios",
}


def initialize_database() -> None:
    """Create a new database from the SQL script, or verify an existing one."""
    if not DATABASE_PATH.exists():
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        return

    with sqlite3.connect(DATABASE_PATH) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    missing_tables = REQUIRED_TABLES - tables
    if missing_tables:
        missing = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            f"La base de datos no contiene las tablas requeridas: {missing}. "
            "Revise la ruta de la base de datos antes de iniciar la API."
        )


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
