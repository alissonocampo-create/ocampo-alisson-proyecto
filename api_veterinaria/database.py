import sqlite3
from collections.abc import Generator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "clinica_veterinaria.db"
SCHEMA_PATH = PROJECT_ROOT / "crear_bd.sql"
MIGRATION_PATH = Path(__file__).resolve().parent / "migraciones" / (
    "001_accesorios_productos_tratamientos.sql"
)
NUTRITION_MIGRATION_PATH = Path(__file__).resolve().parent / "migraciones" / (
    "002_alimentos.sql"
)
CATALOG_DETAILS_MIGRATION_PATH = Path(__file__).resolve().parent / "migraciones" / (
    "003_catalogo_detalles.sql"
)
CATALOG_ORTHOGRAPHY_MIGRATION_PATH = (
    Path(__file__).resolve().parent
    / "migraciones"
    / "004_correccion_catalogo_ortografia.sql"
)
CLINIC_MANAGEMENT_MIGRATION_PATH = (
    Path(__file__).resolve().parent
    / "migraciones"
    / "005_gestion_clinica.sql"
)
TREATMENT_DEMO_MIGRATION_PATH = (
    Path(__file__).resolve().parent
    / "migraciones"
    / "006_tratamientos_demo.sql"
)
FARM_ANIMAL_MIGRATION_PATH = (
    Path(__file__).resolve().parent
    / "migraciones"
    / "007_mascotas_granja.sql"
)
CATALOG_TABLES = ("accesorios", "productos_veterinarios", "alimentos")
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
    else:
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

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for migration_path in (MIGRATION_PATH, NUTRITION_MIGRATION_PATH):
            connection.executescript(
                "BEGIN;\n"
                + migration_path.read_text(encoding="utf-8")
                + "\nCOMMIT;"
            )
        user_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(usuarios)")
        }
        if "rol" not in user_columns:
            connection.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN rol TEXT NOT NULL DEFAULT 'recepcion'
                CHECK (rol IN ('administrador', 'veterinario', 'recepcion'))
                """
            )
        for table_name in CATALOG_TABLES:
            columns = {
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table_name})")
            }
            if "uso" not in columns:
                connection.execute(f"ALTER TABLE {table_name} ADD COLUMN uso TEXT")
        for table_name in ("mascotas", *CATALOG_TABLES):
            columns = {
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table_name})")
            }
            if "imagen_url" not in columns:
                connection.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN imagen_url TEXT"
                )
        connection.executescript(
            "BEGIN;\n"
            + CATALOG_DETAILS_MIGRATION_PATH.read_text(encoding="utf-8")
            + "\n"
            + CATALOG_ORTHOGRAPHY_MIGRATION_PATH.read_text(encoding="utf-8")
            + "\nCOMMIT;"
        )
        connection.executescript(
            "BEGIN;\n"
            + CLINIC_MANAGEMENT_MIGRATION_PATH.read_text(encoding="utf-8")
            + "\nUPDATE usuarios SET rol = 'administrador' "
            "WHERE nombre_usuario = 'admin';\n"
            + "DELETE FROM sesiones WHERE julianday(expira_en) <= julianday('now');\n"
            + "COMMIT;"
        )
        connection.executescript(
            "BEGIN;\n"
            + TREATMENT_DEMO_MIGRATION_PATH.read_text(encoding="utf-8")
            + "\nCOMMIT;"
        )
        schema_migrations_exist = connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'migraciones_esquema'"
        ).fetchone()
        farm_animals_migration_applied = (
            schema_migrations_exist is not None
            and connection.execute(
                "SELECT 1 FROM migraciones_esquema "
                "WHERE version = '007_mascotas_granja'"
            ).fetchone()
            is not None
        )
        if not farm_animals_migration_applied:
            connection.executescript(
                FARM_ANIMAL_MIGRATION_PATH.read_text(encoding="utf-8")
            )


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
