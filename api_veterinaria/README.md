# API de Clínica Veterinaria

Proyecto académico de Alisson Daniela Ocampo Maldonado para Programación III.

## Avance actual

Sistema web con FastAPI, SQLite y arquitectura por capas. Incluye gestión de
dueños, mascotas, una tienda veterinaria, una farmacia, un catálogo de nutrición
y tratamientos asociados a mascotas.

## Preparación y ejecución

Desde esta carpeta (`api_veterinaria`), crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Inicia el sistema web y su API:

```powershell
python -m uvicorn main:app --reload --port 8001
```

Abre el sistema visual en <http://127.0.0.1:8001/> o la documentación de la API
en <http://127.0.0.1:8001/docs>. Se usa el puerto 8001 para mantenerlo separado
de otros proyectos que puedan estar ejecutándose en el puerto 8000.

La API utiliza la base `clinica_veterinaria.db` y el esquema `crear_bd.sql` que
están en la carpeta principal del repositorio, fuera de esta subcarpeta. Si la
base no existe, la API la crea con ese esquema. Al iniciar, aplica de forma
idempotente las migraciones de inventarios, alimentos, fichas, correcciones
ortográficas del catálogo y gestión clínica;
si la base ya existe, conserva sus datos y agrega las nuevas tablas y columnas
sin borrar ni recrear las tablas existentes.

## Documentación y pruebas

- Sistema visual: <http://127.0.0.1:8001/>
- Documentación interactiva: <http://127.0.0.1:8001/docs>
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
| GET, POST | `/accesorios/` | Listar y registrar artículos de la tienda |
| GET, PUT, DELETE | `/accesorios/{id}` | Consultar, actualizar o eliminar un artículo de la tienda |
| GET, POST | `/productos-veterinarios/` | Listar y registrar medicamentos y productos de farmacia |
| GET, PUT, DELETE | `/productos-veterinarios/{id}` | Consultar, actualizar o eliminar un producto de farmacia |
| GET, POST | `/alimentos/` | Listar y registrar alimentos para mascotas |
| GET, PUT, DELETE | `/alimentos/{id}` | Consultar, actualizar o eliminar un alimento |
| GET, POST | `/tratamientos/` | Consultar y registrar tratamientos por mascota |
| GET, PUT, DELETE | `/tratamientos/{id}` | Consultar, actualizar o eliminar un tratamiento |
| POST | `/asistente/preguntar` | Consultar inventario y registros mediante el asistente local |
| POST | `/imagenes/` | Cargar una foto JPG, PNG o WebP de hasta 5 MB |
| POST | `/auth/login`, `/auth/logout` | Iniciar y cerrar una sesión protegida |
| GET | `/auth/me` | Consultar el usuario y el perfil de la sesión |
| POST | `/auth/password` | Cambiar la contraseña de la cuenta actual |
| GET, POST, PUT | `/auth/usuarios` | Consultar, crear, activar y asignar perfiles (solo administración) |
| GET, POST, PUT, DELETE | `/citas/` | Gestionar citas, con filtros por fecha |
| GET, POST, PUT, DELETE | `/vacunas/` | Consultar el historial y registrar aplicaciones |
| GET | `/vacunas/proximas?dias=30` | Consultar próximas dosis |
| GET, POST, PUT, DELETE | `/lotes-farmacia/` | Controlar lotes, proveedores, existencias y vencimientos |
| GET | `/lotes-farmacia/alertas?dias=90` | Consultar lotes vencidos o próximos a vencer |
| GET | `/reportes/resumen` | Consultar indicadores de citas, vacunas e inventario |
| GET | `/reportes/descargar?tipo=citas\|vacunas\|inventario` | Descargar reportes CSV |
| POST | `/respaldos/` | Descargar una copia SQLite consistente (solo administración) |

La primera cuenta de la base de demostración es `admin` con contraseña
`VetDemo2026!`. Cambia esta contraseña desde **Informes y seguridad** después
del primer acceso. Las contraseñas nuevas se guardan con PBKDF2-HMAC-SHA256;
las sesiones usan una cookie `HttpOnly`, `SameSite=Strict` y vencen a las ocho
horas. Tras cinco intentos fallidos desde una misma dirección se limita el
acceso durante 15 minutos.

La base de demostración incluye tres tratamientos de ejemplo identificados
como **DEMO**. No son recetas ni historiales clínicos reales; reemplázalos por
indicaciones confirmadas por un médico veterinario.

Perfiles disponibles: **administración** (acceso completo y gestión de cuentas
y respaldos), **veterinario** (historial clínico, citas, vacunas y tratamientos)
y **recepción** (dueños, mascotas y agenda; consulta de catálogos e informes).
El registro de mascotas permite perros, gatos, aves, gallinas, caballos y vacas.
La migración agrega ejemplos llamados Pepita, Relámpago, Gangster y Bandida;
son registros de demostración que puedes editar o borrar. El directorio muestra
ilustraciones diferentes para cada especie y conserva las fotos propias que se
carguen en cada mascota.
En desarrollo local la cookie funciona por HTTP; al publicar el sistema, usa
HTTPS para que la cookie quede protegida también con el atributo `Secure`.
Los respaldos se generan con la API de copia de SQLite y se descargan; no se
almacenan en la carpeta pública del servidor.

Nutrición permite clasificar alimentos por tipo, especie recomendada y etapa
de vida. Farmacia muestra alertas visuales para existencias de tres unidades
o menos, además de filtros por categoría y stock bajo. Los inventarios permiten
gestionar descripción, uso, precio, existencias y estado; las fichas muestran
fotografías locales representativas por categoría e incluyen sus créditos y
licencias. No se descargan imágenes externas al abrir el sistema.
Las fichas de Tienda, Farmacia y Nutrición se agrupan por categoría en un orden
estable, y los artículos de cada grupo se ordenan alfabéticamente. Cada catálogo
permite filtrar una categoría específica, además de buscar entre sus artículos.
Al registrar o editar una mascota, artículo, producto o alimento se puede cargar
una foto propia. Se guarda localmente y reemplaza la imagen representativa en su
ficha; se aceptan JPG, PNG y WebP de hasta 5 MB.
Las fotografías se obtuvieron de Wikimedia Commons y se distribuyen con estas
licencias:

| Fotografía | Autoría | Licencia | Fuente |
|---|---|---|---|
| Alimento para perros | chrismetcalfTV | CC BY 2.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dog_Food_(208810939).jpg) |
| Premios para perros | Megan Marrs | CC BY 2.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dog_Treats_(51049057473).jpg) |
| Alimento seco para gatos | Anne Jea. | CC BY-SA 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dry_cat_food_mix_08.jpg) |
| Latas de alimento húmedo para gatos | Jonn Leffmann | CC BY 3.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Kattmat-Cat_food-Katzenfutter-Nourriture_pour_chats_-_2022.jpg) |
| Collar de perro | Trougnouf (Benoit Brummer), Les cuirs d'Agathe | CC BY 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Leather_dog_collar_made_by_Les_cuirs_d%27Agathe_(DSC07529).jpg) |
| Correa para perro | Schizek | Dominio público | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:PPD-Leash-PinkGreenStripes.jpg) |
| Gato jugando con un juguete | Nancy Wong | CC BY-SA 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Cat_playing_with_toy_mouse.jpg) |
| Perro en su cama | Tomwsulcer | CC0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dog_sleeping_in_a_dog_bed.JPG) |
| Frasco de shampoo antipulgas para perro | Shingoli | CC BY-SA 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Shingoli_shampoo_Tick_n_flea_front.jpg) |
| Frasco de gotas para los oídos | 3df | CC BY-SA 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Ear_drops_bottle.jpg) |
| Cápsulas y tabletas en blíster | BuhaM | CC BY-SA 4.0 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Pills_and_medicines_01.jpg) |

Las imágenes son fotografías representativas, no fotos del modelo o marca exactos
de cada artículo registrado.
Los productos de farmacia describen su uso según la etiqueta y no sustituyen
la prescripción veterinaria. Registrar un
tratamiento documenta sus indicaciones, fechas, estado y producto opcional, pero
no descuenta automáticamente las existencias. La interfaz permite buscar,
crear, editar y eliminar registros. La agenda, vacunas, veterinarios activos,
lotes y vencimientos, autenticación por perfil, informes descargables y
respaldos se administran desde sus secciones del sistema visual y la API.

El asistente de ZEUS VET responde preguntas sobre la información que ya está
registrada en la base local. No requiere una API externa y no brinda
diagnósticos ni recomendaciones de dosis.
