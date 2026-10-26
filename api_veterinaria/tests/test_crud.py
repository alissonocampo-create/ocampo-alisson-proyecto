import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import database
from main import app

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "crear_bd.sql"


def test_inicializar_crea_base_nueva_desde_sql(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "nueva_clinica.db"
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)
    database.initialize_database()

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert database.REQUIRED_TABLES <= tables
        assert connection.execute("SELECT COUNT(*) FROM duenos").fetchone()[0] == 10


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    test_database = tmp_path / "test_clinica.db"
    with sqlite3.connect(test_database) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    with TestClient(app) as test_client:
        yield test_client


def test_inicio_muestra_documentacion(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["documentacion"] == "/docs"


def test_listar_duenos_incluye_datos_de_prueba(client: TestClient) -> None:
    response = client.get("/duenos/")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_crear_y_consultar_dueno(client: TestClient) -> None:
    created = client.post(
        "/duenos/",
        json={
            "nombre": "  María López ",
            "telefono": "  +504 9999-1234 ",
            "direccion": " Barrio Centro ",
        },
    )
    assert created.status_code == 201
    assert created.json()["nombre"] == "María López"
    assert created.json()["direccion"] == "Barrio Centro"
    fetched = client.get(f"/duenos/{created.json()['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["telefono"] == "+504 9999-1234"


def test_actualizar_dueno(client: TestClient) -> None:
    response = client.put(
        "/duenos/1",
        json={
            "nombre": "Ana Rivera Actualizada",
            "telefono": "+504 9999-1111",
            "direccion": None,
        },
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Ana Rivera Actualizada"


def test_rechazar_telefono_de_dueno_duplicado(client: TestClient) -> None:
    response = client.post(
        "/duenos/",
        json={"nombre": "Otro dueño", "telefono": "+504 9876-1001"},
    )
    assert response.status_code == 409


def test_eliminar_dueno_con_mascotas_se_rechaza(client: TestClient) -> None:
    response = client.delete("/duenos/1")
    assert response.status_code == 409


def test_listar_mascotas_incluye_datos_de_prueba(client: TestClient) -> None:
    response = client.get("/mascotas/")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_crear_mascota(client: TestClient) -> None:
    response = client.post(
        "/mascotas/",
        json={
            "nombre": "Nube",
            "especie": "gato",
            "raza": "Criollo",
            "fecha_nacimiento": "2025-02-10",
            "dueno_id": 1,
        },
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "Nube"
    assert response.json()["fecha_nacimiento"] == "2025-02-10"


def test_rechazar_mascota_con_especie_invalida(client: TestClient) -> None:
    response = client.post(
        "/mascotas/",
        json={"nombre": "Nube", "especie": "reptil", "dueno_id": 1},
    )
    assert response.status_code == 422


def test_rechazar_mascota_con_dueno_inexistente(client: TestClient) -> None:
    response = client.post(
        "/mascotas/",
        json={"nombre": "Nube", "especie": "gato", "dueno_id": 9999},
    )
    assert response.status_code == 404


def test_actualizar_y_eliminar_mascota(client: TestClient) -> None:
    created = client.post(
        "/mascotas/",
        json={"nombre": "Nube", "especie": "gato", "dueno_id": 1},
    )
    assert created.status_code == 201
    mascota_id = created.json()["id"]
    updated = client.put(
        f"/mascotas/{mascota_id}",
        json={
            "nombre": "Nube Actualizada",
            "especie": "gato",
            "raza": "Criollo",
            "fecha_nacimiento": None,
            "dueno_id": 1,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["nombre"] == "Nube Actualizada"
    deleted = client.delete(f"/mascotas/{mascota_id}")
    assert deleted.status_code == 204
    assert client.get(f"/mascotas/{mascota_id}").status_code == 404


def test_consulta_de_registro_inexistente_devuelve_404(client: TestClient) -> None:
    assert client.get("/duenos/9999").status_code == 404
    assert client.get("/mascotas/9999").status_code == 404
