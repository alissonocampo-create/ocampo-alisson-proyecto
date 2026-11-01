import sqlite3
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import database
import main
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
        assert {
            "accesorios",
            "productos_veterinarios",
            "tratamientos",
            "alimentos",
            "sesiones",
            "lotes_farmacia",
            "intentos_acceso",
        } <= tables
        user_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(usuarios)")
        }
        assert "rol" in user_columns
        assert connection.execute(
            "SELECT rol FROM usuarios WHERE nombre_usuario = 'admin'"
        ).fetchone()[0] == "administrador"
        for table_name in ("accesorios", "productos_veterinarios", "alimentos"):
            columns = {
                row[1]
                for row in connection.execute(f"PRAGMA table_info({table_name})")
            }
            assert {"descripcion", "uso"} <= columns
            assert "imagen_url" in columns
        pet_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(mascotas)")
        }
        assert "imagen_url" in pet_columns
        assert connection.execute("SELECT COUNT(*) FROM duenos").fetchone()[0] == 10
        assert connection.execute("SELECT COUNT(*) FROM accesorios").fetchone()[0] > 0
        assert connection.execute(
            "SELECT COUNT(*) FROM productos_veterinarios"
        ).fetchone()[0] > 0
        assert connection.execute("SELECT COUNT(*) FROM alimentos").fetchone()[0] > 0
        for table_name in ("accesorios", "productos_veterinarios", "alimentos"):
            assert connection.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE descripcion IS NULL OR uso IS NULL"
            ).fetchone()[0] == 0


def test_inicializar_agrega_tratamientos_demo_una_sola_vez(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "tratamientos_demo.db"
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)

    database.initialize_database()
    with sqlite3.connect(database_path) as connection:
        treatments = connection.execute(
            "SELECT nombre, indicaciones, dosis FROM tratamientos ORDER BY id"
        ).fetchall()
    assert len(treatments) == 3
    assert all("(DEMO)" in name for name, _, _ in treatments)
    assert all("no es una receta real" in instructions for _, instructions, _ in treatments)
    assert all(dose is None for _, _, dose in treatments)

    with sqlite3.connect(database_path) as connection:
        connection.execute("DELETE FROM tratamientos")
    database.initialize_database()

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM tratamientos").fetchone()[0] == 0


def test_migrar_especies_de_granja_conserva_referencias(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "clinica_legacy.db"
    legacy_schema = SCHEMA_PATH.read_text(encoding="utf-8").replace(
        "'perro', 'gato', 'ave', 'gallina', 'caballo', 'vaca', 'otro'",
        "'perro', 'gato', 'ave', 'otro'",
    )
    with sqlite3.connect(database_path) as connection:
        connection.executescript(legacy_schema)
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)

    database.initialize_database()
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        pets = connection.execute(
            "SELECT nombre, especie, raza, dueno_id FROM mascotas "
            "WHERE especie IN ('gallina', 'caballo', 'vaca') ORDER BY id"
        ).fetchall()
    assert pets == [
        ("Pepita", "gallina", "Criolla", 1),
        ("Relámpago", "caballo", "Cuarto de milla", 2),
        ("Gangster", "vaca", "Holstein", 3),
        ("Bandida", "vaca", "Brahman", 4),
    ]

    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE INDEX idx_prueba_migracion_una_vez ON mascotas(nombre)")
    database.initialize_database()
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM mascotas WHERE especie IN ('gallina', 'caballo', 'vaca')"
        ).fetchone()[0] == 4
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'index' AND name = 'idx_prueba_migracion_una_vez'"
        ).fetchone() is not None


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    test_database = tmp_path / "test_clinica.db"
    with sqlite3.connect(test_database) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    with TestClient(app) as test_client:
        login = test_client.post(
            "/auth/login",
            json={"nombre_usuario": "admin", "password": "VetDemo2026!"},
        )
        assert login.status_code == 200
        yield test_client


def test_sistema_requiere_sesion_para_datos_clinicos(client: TestClient) -> None:
    client.cookies.clear()
    response = client.get("/duenos/")
    assert response.status_code == 401


def test_autenticacion_expone_rol_sin_publicar_password_hash(
    client: TestClient,
) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["nombre_usuario"] == "admin"
    assert response.json()["rol"] == "administrador"
    assert "password_hash" not in response.json()


def test_cambio_de_password_revoca_y_reinicia_la_sesion(
    client: TestClient,
) -> None:
    changed = client.post(
        "/auth/password",
        json={
            "password_actual": "VetDemo2026!",
            "password_nueva": "NuevaClaveSegura2026!",
        },
    )
    assert changed.status_code == 204
    assert client.get("/auth/me").status_code == 401
    assert client.post(
        "/auth/login",
        json={
            "nombre_usuario": "admin",
            "password": "NuevaClaveSegura2026!",
        },
    ).status_code == 200


def test_citas_vacunas_y_alertas_de_lotes(client: TestClient) -> None:
    appointment = client.post(
        "/citas/",
        json={
            "mascota_id": 1,
            "veterinario_id": 1,
            "fecha_hora": "2099-05-01T10:30",
            "motivo": "Control preventivo",
            "estado": "programada",
        },
    )
    assert appointment.status_code == 201
    assert appointment.json()["mascota"] == "Luna"
    assert client.get("/citas/?desde=2099-05-01").json()[0]["motivo"] == (
        "Control preventivo"
    )

    next_dose = (date.today() + timedelta(days=10)).isoformat()
    vaccine = client.post(
        "/vacunas/",
        json={
            "mascota_id": 1,
            "vacuna": "Vacuna de prueba",
            "fecha": date.today().isoformat(),
            "proxima_dosis": next_dose,
        },
    )
    assert vaccine.status_code == 201
    assert vaccine.json()["mascota"] == "Luna"
    assert any(
        record["vacuna"] == "Vacuna de prueba"
        for record in client.get("/vacunas/proximas?dias=30").json()
    )

    product = client.get("/productos-veterinarios/").json()[0]
    lot = client.post(
        "/lotes-farmacia/",
        json={
            "producto_id": product["id"],
            "numero_lote": "TEST-2026",
            "proveedor": "Proveedor de prueba",
            "vencimiento": "2000-01-01",
            "stock": 7,
        },
    )
    assert lot.status_code == 201
    assert lot.json()["producto"] == product["nombre"]
    assert any(
        record["numero_lote"] == "TEST-2026"
        for record in client.get("/lotes-farmacia/alertas").json()
    )


def test_reportes_csv_y_respaldo_sqlite(client: TestClient, tmp_path: Path) -> None:
    summary = client.get("/reportes/resumen")
    assert summary.status_code == 200
    assert {"citas_programadas", "vacunas_proximas", "lotes_por_vencer"} <= (
        summary.json().keys()
    )
    report = client.get("/reportes/descargar?tipo=vacunas")
    assert report.status_code == 200
    assert "text/csv" in report.headers["content-type"]
    assert "Mascota" in report.text

    backup = client.post("/respaldos/")
    assert backup.status_code == 200
    backup_file = tmp_path / "clinic-backup.db"
    backup_file.write_bytes(backup.content)
    with sqlite3.connect(backup_file) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert {"citas", "vacunas_aplicadas", "lotes_farmacia", "sesiones"} <= tables


def test_recepcion_no_puede_administrar_usuarios_ni_modificar_farmacia(
    client: TestClient,
) -> None:
    created = client.post(
        "/auth/usuarios",
        json={
            "nombre_usuario": "recepcion1",
            "correo": "recepcion@example.test",
            "nombre_completo": "Recepción de prueba",
            "password": "ClaveSegura2026!",
            "rol": "recepcion",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert client.put(
        f"/auth/usuarios/{user_id}",
        json={"rol": "veterinario", "activo": True},
    ).json()["rol"] == "veterinario"
    assert client.put(
        f"/auth/usuarios/{user_id}",
        json={"rol": "recepcion", "activo": False},
    ).json()["activo"] == 0
    assert client.post(
        "/auth/login",
        json={"nombre_usuario": "recepcion1", "password": "ClaveSegura2026!"},
    ).status_code == 401
    assert client.put(
        f"/auth/usuarios/{user_id}",
        json={"rol": "recepcion", "activo": True},
    ).json()["activo"] == 1
    assert client.put(
        "/auth/usuarios/1",
        json={"rol": "recepcion", "activo": True},
    ).status_code == 409
    client.post("/auth/logout")
    login = client.post(
        "/auth/login",
        json={"nombre_usuario": "recepcion1", "password": "ClaveSegura2026!"},
    )
    assert login.status_code == 200
    assert client.get("/productos-veterinarios/").status_code == 200
    assert client.get("/auth/usuarios").status_code == 403
    assert client.post(
        "/productos-veterinarios/",
        json={
            "nombre": "Producto no permitido",
            "categoria": "higiene",
            "descripcion": "Prueba",
            "uso": "Prueba",
            "precio": 10,
            "stock": 1,
        },
    ).status_code == 403


def test_inicio_muestra_sistema_visual(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ZEUS VET" in response.text


def test_interfaz_estatica_se_sirve_correctamente(client: TestClient) -> None:
    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "loadData" in response.text


def test_catalogos_muestran_tarjetas_con_imagen_y_uso(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    for catalog_id in ("accessories-body", "products-body", "foods-body"):
        assert f'id="{catalog_id}" class="catalog-grid-content"' in response.text


def test_fotografias_del_catalogo_se_sirven_localmente(client: TestClient) -> None:
    for photo in (
        "dog-food.jpg",
        "dog-treats.jpg",
        "cat-food.jpg",
        "cat-wet-food.jpg",
        "medicine-pills.jpg",
        "dog-collar.jpg",
        "dog-leash.jpg",
        "cat-toy.jpg",
        "dog-bed.jpg",
        "pet-shampoo.jpg",
        "ear-drops.jpg",
    ):
        response = client.get(f"/static/images/catalog/{photo}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content.startswith(b"\xff\xd8\xff")


def test_cargar_foto_de_producto_y_guardarla_en_su_ficha(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main, "STATIC_DIR", tmp_path / "static")
    image_data = b"\xff\xd8\xff\xe0foto-de-prueba"
    uploaded = client.post(
        "/imagenes/",
        content=image_data,
        headers={"content-type": "image/jpeg"},
    )
    assert uploaded.status_code == 200
    imagen_url = uploaded.json()["imagen_url"]
    stored_image = tmp_path / "static" / imagen_url.removeprefix("/static/")
    assert stored_image.read_bytes() == image_data

    created = client.post(
        "/productos-veterinarios/",
        json={
            "nombre": "Producto con foto",
            "categoria": "higiene",
            "descripcion": "Producto de prueba.",
            "uso": "Uso según la etiqueta.",
            "precio": 99,
            "stock": 2,
            "imagen_url": imagen_url,
        },
    )
    assert created.status_code == 201
    assert created.json()["imagen_url"] == imagen_url

    fetched = client.get(f"/productos-veterinarios/{created.json()['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["imagen_url"] == imagen_url

    pet = client.post(
        "/mascotas/",
        json={
            "nombre": "Mascota con foto",
            "especie": "perro",
            "dueno_id": 1,
            "imagen_url": imagen_url,
        },
    )
    assert pet.status_code == 201
    assert pet.json()["imagen_url"] == imagen_url


def test_actualizar_foto_de_accesorio_persiste_la_nueva_url(
    client: TestClient,
) -> None:
    created = client.post(
        "/accesorios/",
        json={
            "nombre": "Accesorio con foto",
            "categoria": "collar",
            "descripcion": "Collar de prueba.",
            "uso": "Uso de prueba.",
            "precio": 99,
            "stock": 2,
            "imagen_url": "/static/images/uploads/11111111111111111111111111111111.jpg",
        },
    )
    assert created.status_code == 201
    accessory_id = created.json()["id"]

    updated = client.put(
        f"/accesorios/{accessory_id}",
        json={
            **created.json(),
            "imagen_url": "/static/images/uploads/22222222222222222222222222222222.jpg",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["imagen_url"] == (
        "/static/images/uploads/22222222222222222222222222222222.jpg"
    )

    fetched = client.get(f"/accesorios/{accessory_id}")
    assert fetched.status_code == 200
    assert fetched.json()["imagen_url"] == updated.json()["imagen_url"]


def test_cargar_imagen_rechaza_formato_invalido(client: TestClient) -> None:
    response = client.post(
        "/imagenes/",
        content=b"not an image",
        headers={"content-type": "image/jpeg"},
    )
    assert response.status_code == 415


def test_registros_rechazan_rutas_de_imagen_externas(client: TestClient) -> None:
    response = client.post(
        "/mascotas/",
        json={
            "nombre": "Nube",
            "especie": "gato",
            "dueno_id": 1,
            "imagen_url": "https://example.com/foto.jpg",
        },
    )
    assert response.status_code == 422


def test_interfaz_clasifica_tratamientos_por_especie(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="treatment-species-filter"' in response.text
    assert '<option value="perro">Perros</option>' in response.text
    assert '<option value="gato">Gatos</option>' in response.text
    assert '<option value="ave">Aves</option>' in response.text
    assert '<option value="gallina">Gallinas</option>' in response.text
    assert '<option value="caballo">Caballos</option>' in response.text
    assert '<option value="vaca">Vacas</option>' in response.text
    assert '<option value="otro">Otros</option>' in response.text
    script = client.get("/static/app.js")
    assert script.status_code == 200
    for species, label in (
        ("gallina", "Gallina"),
        ("caballo", "Caballo"),
        ("vaca", "Vaca"),
    ):
        assert f'["{species}", "{label}"]' in script.text


def test_crear_mascotas_de_granja(client: TestClient) -> None:
    animals = (
        ("Pepita de prueba", "gallina", "Criolla"),
        ("Relámpago de prueba", "caballo", "Cuarto de milla"),
        ("Gangster de prueba", "vaca", "Holstein"),
    )
    for name, species, breed in animals:
        response = client.post(
            "/mascotas/",
            json={
                "nombre": name,
                "especie": species,
                "raza": breed,
                "fecha_nacimiento": "2024-01-15",
                "dueno_id": 1,
            },
        )
        assert response.status_code == 201
        assert response.json()["especie"] == species
        assert response.json()["raza"] == breed


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
    assert len(response.json()) == 14


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


def test_asistente_consulta_productos_de_farmacia(client: TestClient) -> None:
    response = client.post(
        "/asistente/preguntar",
        json={"pregunta": "¿Qué medicamentos hay en la farmacia?"},
    )
    assert response.status_code == 200
    assert "Antiparasitario oral" in response.json()["respuesta"]
    assert "existencias" in response.json()["respuesta"]
    assert "Shampoo hipoalergénico" not in response.json()["respuesta"]


def test_asistente_consulta_alimentos_por_especie(client: TestClient) -> None:
    response = client.post(
        "/asistente/preguntar",
        json={"pregunta": "¿Qué alimentos hay para perros?"},
    )
    assert response.status_code == 200
    assert "Concentrado completo para perro" in response.json()["respuesta"]
    assert "Alimento húmedo para gato" not in response.json()["respuesta"]


def test_asistente_busca_articulo_y_consulta_mascotas(client: TestClient) -> None:
    product = client.post(
        "/asistente/preguntar",
        json={"pregunta": "¿Cuánto shampoo hipoalergénico queda?"},
    )
    assert product.status_code == 200
    assert "Shampoo hipoalergénico" in product.json()["respuesta"]

    pet = client.post(
        "/asistente/preguntar",
        json={"pregunta": "¿Quién es el dueño de Luna?"},
    )
    assert pet.status_code == 200
    assert "Luna" in pet.json()["respuesta"]


def test_asistente_no_indica_dosis_ni_diagnostica(client: TestClient) -> None:
    response = client.post(
        "/asistente/preguntar",
        json={"pregunta": "¿Qué dosis le doy a mi perro?"},
    )
    assert response.status_code == 200
    assert "no puedo indicar dosis" in response.json()["respuesta"]


def test_asistente_rechaza_pregunta_vacia(client: TestClient) -> None:
    assert client.post("/asistente/preguntar", json={"pregunta": "   "}).status_code == 422


def test_crear_actualizar_y_eliminar_accesorio(client: TestClient) -> None:
    created = client.post(
        "/accesorios/",
        json={
            "nombre": "Arnés azul",
            "categoria": "ropa",
            "descripcion": "Arnés ajustable",
            "uso": "Ayuda a sujetar a la mascota durante los paseos.",
            "precio": 275.5,
            "stock": 4,
            "activo": True,
        },
    )
    assert created.status_code == 201
    accessory_id = created.json()["id"]
    assert created.json()["stock"] == 4
    updated = client.put(
        f"/accesorios/{accessory_id}",
        json={
            "nombre": "Arnés azul mediano",
            "categoria": "ropa",
            "descripcion": "Arnés ajustable para perros medianos.",
            "uso": "Ayuda a sujetar a la mascota durante los paseos.",
            "precio": 300,
            "stock": 2,
            "activo": False,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["activo"] is False
    assert client.delete(f"/accesorios/{accessory_id}").status_code == 204
    assert client.get(f"/accesorios/{accessory_id}").status_code == 404


def test_rechazar_stock_negativo_y_categoria_invalida(client: TestClient) -> None:
    payload = {
        "nombre": "Producto inválido",
        "categoria": "otra",
        "descripcion": "Producto de prueba.",
        "uso": "Uso descrito en la etiqueta.",
        "precio": 10,
        "stock": -1,
    }
    assert client.post("/productos-veterinarios/", json=payload).status_code == 422
    payload["categoria"] = "pastilla"
    payload["stock"] = 1
    payload["precio"] = -1
    assert client.post("/productos-veterinarios/", json=payload).status_code == 422


def test_crear_actualizar_y_eliminar_producto_veterinario(
    client: TestClient,
) -> None:
    created = client.post(
        "/productos-veterinarios/",
        json={
            "nombre": "Producto de prueba",
            "categoria": "higiene",
            "descripcion": "Artículo de higiene para mascotas.",
            "uso": "Uso externo según las indicaciones del fabricante.",
            "precio": 99,
            "stock": 5,
        },
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    updated = client.put(
        f"/productos-veterinarios/{product_id}",
        json={
            "nombre": "Producto actualizado",
            "categoria": "shampoo",
            "descripcion": "Shampoo para higiene del pelaje.",
            "uso": "Usar según las instrucciones de la etiqueta.",
            "precio": 125,
            "stock": 3,
            "activo": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["stock"] == 3
    assert client.delete(f"/productos-veterinarios/{product_id}").status_code == 204
    assert client.get(f"/productos-veterinarios/{product_id}").status_code == 404


def test_crear_actualizar_y_eliminar_alimento(client: TestClient) -> None:
    created = client.post(
        "/alimentos/",
        json={
            "nombre": "Croquetas para gato",
            "categoria": "concentrado",
            "especie": "gato",
            "etapa": "adulto",
            "descripcion": "Croquetas completas para gatos adultos.",
            "uso": "Alimentación diaria según la ración del envase.",
            "precio": 420,
            "stock": 6,
        },
    )
    assert created.status_code == 201
    assert created.json()["especie"] == "gato"
    alimento_id = created.json()["id"]

    updated = client.put(
        f"/alimentos/{alimento_id}",
        json={**created.json(), "categoria": "humedo", "stock": 4},
    )
    assert updated.status_code == 200
    assert updated.json()["categoria"] == "humedo"
    assert updated.json()["stock"] == 4
    assert client.delete(f"/alimentos/{alimento_id}").status_code == 204
    assert client.get(f"/alimentos/{alimento_id}").status_code == 404


def test_alimento_rechaza_categoria_especie_y_stock_invalidos(
    client: TestClient,
) -> None:
    payload = {
        "nombre": "Alimento inválido",
        "categoria": "otra",
        "especie": "gato",
        "descripcion": "Alimento de prueba.",
        "uso": "Alimentación según las instrucciones del envase.",
        "precio": 10,
        "stock": 1,
    }
    assert client.post("/alimentos/", json=payload).status_code == 422
    payload.update(categoria="concentrado", especie="reptil")
    assert client.post("/alimentos/", json=payload).status_code == 422
    payload.update(especie="gato", stock=-1)
    assert client.post("/alimentos/", json=payload).status_code == 422


def test_registrar_tratamiento_asociado_sin_descontar_existencias(
    client: TestClient,
) -> None:
    product = client.get("/productos-veterinarios/").json()[0]
    initial_stock = product["stock"]
    created = client.post(
        "/tratamientos/",
        json={
            "mascota_id": 1,
            "producto_id": product["id"],
            "nombre": "Control veterinario",
            "indicaciones": "Seguir la indicación del profesional.",
            "dosis": "Según evaluación",
            "fecha_inicio": "2025-02-01",
            "fecha_fin": "2025-02-08",
            "estado": "en_curso",
        },
    )
    assert created.status_code == 201
    assert created.json()["mascota_id"] == 1
    assert created.json()["producto_id"] == product["id"]
    assert client.get(f"/productos-veterinarios/{product['id']}").json()["stock"] == initial_stock
    treatment_id = created.json()["id"]
    updated = client.put(
        f"/tratamientos/{treatment_id}",
        json={
            **created.json(),
            "estado": "completado",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["estado"] == "completado"
    assert client.delete(f"/tratamientos/{treatment_id}").status_code == 204
    assert client.get(f"/tratamientos/{treatment_id}").status_code == 404


def test_tratamiento_valida_mascota_producto_y_fechas(client: TestClient) -> None:
    payload = {
        "mascota_id": 9999,
        "nombre": "Tratamiento",
        "indicaciones": "Indicaciones",
        "fecha_inicio": "2025-03-10",
        "fecha_fin": "2025-03-01",
    }
    assert client.post("/tratamientos/", json=payload).status_code == 422
    payload["fecha_fin"] = None
    assert client.post("/tratamientos/", json=payload).status_code == 404
    payload["mascota_id"] = 1
    payload["producto_id"] = 9999
    assert client.post("/tratamientos/", json=payload).status_code == 404


def test_catalogo_normaliza_y_exige_descripcion_y_uso(client: TestClient) -> None:
    payload = {
        "nombre": "Juguete de prueba",
        "categoria": "juguete",
        "descripcion": "  Juguete resistente. ",
        "uso": "  Para juego supervisado. ",
        "precio": 50,
        "stock": 2,
    }
    created = client.post("/accesorios/", json=payload)
    assert created.status_code == 201
    assert created.json()["descripcion"] == "Juguete resistente."
    assert created.json()["uso"] == "Para juego supervisado."

    payload.pop("uso")
    assert client.post("/accesorios/", json=payload).status_code == 422
    payload["uso"] = "   "
    assert client.post("/accesorios/", json=payload).status_code == 422


def test_migracion_repetida_no_duplica_datos_ni_borra_registros(
    client: TestClient,
) -> None:
    before = {
        table: client.get(f"/{endpoint}/").json()
        for table, endpoint in (
            ("mascotas", "mascotas"),
            ("accesorios", "accesorios"),
            ("productos", "productos-veterinarios"),
            ("alimentos", "alimentos"),
            ("tratamientos", "tratamientos"),
        )
    }
    database.initialize_database()
    after = {
        table: client.get(f"/{endpoint}/").json()
        for table, endpoint in (
            ("mascotas", "mascotas"),
            ("accesorios", "accesorios"),
            ("productos", "productos-veterinarios"),
            ("alimentos", "alimentos"),
            ("tratamientos", "tratamientos"),
        )
    }
    assert {table: len(rows) for table, rows in after.items()} == {
        table: len(rows) for table, rows in before.items()
    }


def test_migracion_corrige_acentos_danados_en_los_catalogos(
    client: TestClient,
) -> None:
    with sqlite3.connect(database.DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO alimentos (
                id, nombre, categoria, especie, etapa, descripcion, uso,
                precio, stock, activo
            )
            VALUES (
                9001, 'Hueso de fÃ©mur de cerdo', 'premio', 'perro',
                'todas', 'Premio masticable de fÃ©mur de cerdo, segÃºn el empaque.',
                'Ofrecer según las indicaciones.', 300, 10, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO productos_veterinarios (
                id, nombre, categoria, descripcion, uso, precio, stock, activo
            )
            VALUES (
                9002, 'BÃÂ¡lsamo para nariz', 'higiene',
                'BÃÂ¡lsamo cosmÃÂ©tico para nariz seca.',
                'Aplicar ÃÂºnicamente conforme a las indicaciones.',
                100, 5, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO alimentos (
                id, nombre, categoria, especie, etapa, descripcion, uso,
                precio, stock, activo
            )
            VALUES (
                9003, 'Cesar Classics pollo y pavo', 'humedo', 'perro',
                'todas',
                'Alimento hÃºmedo para perro Cesar Classics, presentaciÃ³n de 150 g.',
                'Instrucción personalizada válida.', 80, 5, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO alimentos (
                id, nombre, categoria, especie, etapa, descripcion, uso,
                precio, stock, activo
            )
            VALUES (
                9004, 'Tropifit Premium Hamster', 'concentrado', 'universal',
                'todas',
                'Alimento Tropifit Premium para hamster con mezcla de semillas y vegetales.',
                'Servir como alimento para hamster segun las instrucciones del empaque.',
                200, 5, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO accesorios (
                id, nombre, categoria, descripcion, uso, precio, stock, activo
            )
            VALUES (
                9005, 'Arnes y correa para gato', 'correa',
                'Conjunto de arnes y correa para gato, mostrado en la fotografia.',
                'Para paseos supervisados con ajuste seguro.',
                150, 5, 1
            )
            """
        )
        connection.execute(
            """
            INSERT INTO productos_veterinarios (
                id, nombre, categoria, descripcion, uso, precio, stock, activo
            )
            VALUES (
                9006, 'Balsamo hidratante para patas Rozino', 'higiene',
                'Balsamo cosmetico para hidratacion de las almohadillas, segun el envase.',
                'Aplicar solo conforme a las indicaciones del fabricante.',
                150, 5, 1
            )
            """
        )

    database.initialize_database()

    foods = {record["id"]: record for record in client.get("/alimentos/").json()}
    products = {
        record["id"]: record
        for record in client.get("/productos-veterinarios/").json()
    }
    accessories = {
        record["id"]: record for record in client.get("/accesorios/").json()
    }
    assert foods[9001]["nombre"] == "Hueso de fémur de cerdo"
    assert foods[9001]["descripcion"] == (
        "Premio masticable de fémur de cerdo, según el empaque de la fotografía."
    )
    assert products[9002]["nombre"] == "Bálsamo para nariz"
    assert products[9002]["descripcion"] == (
        "Bálsamo cosmético para nariz seca, conforme a la etiqueta del fabricante."
    )
    assert products[9002]["uso"] == (
        "Aplicar únicamente conforme a las indicaciones del fabricante."
    )
    assert foods[9003]["descripcion"] == (
        "Alimento húmedo para perro Cesar Classics con pollo y pavo, "
        "presentación mostrada de 150 g."
    )
    assert foods[9003]["uso"] == "Instrucción personalizada válida."
    assert foods[9004]["descripcion"] == (
        "Alimento Tropifit Premium para hámster con mezcla de semillas y vegetales."
    )
    assert foods[9004]["uso"] == (
        "Servir como alimento para hámster según las instrucciones del empaque."
    )
    assert accessories[9005]["nombre"] == "Arnés y correa para gato"
    assert accessories[9005]["descripcion"] == (
        "Conjunto de arnés y correa para gato, mostrado en la fotografía."
    )
    assert products[9006]["nombre"] == "Bálsamo hidratante para patas Rozino"
    assert products[9006]["descripcion"] == (
        "Bálsamo cosmético para hidratación de las almohadillas, según el envase."
    )
