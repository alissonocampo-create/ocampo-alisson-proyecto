# API de Clínica Veterinaria

Proyecto académico de Alisson Daniela Ocampo Maldonado para Programación III.

## Avance actual

API con FastAPI, SQLite y arquitectura por capas. Este avance implementa CRUD de
dueños y mascotas; las demás tablas ya están definidas en `crear_bd.sql`.

## Preparación y ejecución

Desde esta carpeta (`api_veterinaria`), crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Inicia la API:

```powershell
uvicorn main:app --reload
```

La API utiliza la base `clinica_veterinaria.db` y el esquema `crear_bd.sql` que
están en la carpeta principal del repositorio, fuera de esta subcarpeta. Si la
base no existe, la API la crea con ese esquema; si ya existe, la conserva y
comprueba que tenga las seis tablas esperadas.

## Documentación y pruebas

- Documentación interactiva: <http://127.0.0.1:8000/docs>
- Pruebas: `pytest`
- Diagrama entidad-relación y diagrama UML: [`../docs/diagramas.md`](../docs/diagramas.md)

## Endpoints implementados

| Método | Ruta | Acción |
|---|---|---|
| GET | `/duenos/` | Listar dueños |
| GET | `/duenos/{id}` | Consultar un dueño |
| POST | `/duenos/` | Crear un dueño |
| PUT | `/duenos/{id}` | Actualizar un dueño |
| DELETE | `/duenos/{id}` | Eliminar un dueño |
| GET | `/mascotas/` | Listar mascotas |
| GET | `/mascotas/{id}` | Consultar una mascota |
| POST | `/mascotas/` | Crear una mascota |
| PUT | `/mascotas/{id}` | Actualizar una mascota |
| DELETE | `/mascotas/{id}` | Eliminar una mascota |
