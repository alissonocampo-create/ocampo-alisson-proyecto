import re
import sqlite3
import unicodedata
from collections.abc import Generator

from fastapi import APIRouter, Depends

from database import get_db
from esquemas import PreguntaAsistente, RespuestaAsistente

router = APIRouter(prefix="/asistente", tags=["Asistente ZEUS VET"])

STOP_WORDS = {
    "a", "al", "cuanto", "cuantos", "cuantas", "de", "del", "el", "en", "es",
    "hay", "la", "las", "lo", "los", "me", "mi", "mis", "para", "por", "que",
    "se", "tiene", "un", "una", "y",
}
MEDICAL_ADVICE_TERMS = (
    "que dosis",
    "cuanto le doy",
    "cuanta dosis",
    "que medicamento le doy",
    "que le puedo dar",
    "puedo darle",
    "como tratar",
    "diagnostica",
    "diagnosticar",
)


def normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto.casefold())
    sin_acentos = "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"\s+", " ", sin_acentos).strip()


def formatear_inventario(productos: list[sqlite3.Row]) -> str:
    if not productos:
        return "No encontré artículos activos que coincidan en el inventario."
    filas = []
    for producto in productos:
        detalles = f"({producto['categoria']})"
        if "especie" in producto.keys() and producto["especie"] != "universal":
            detalles += f", para {producto['especie']}"
        if "etapa" in producto.keys() and producto["etapa"] != "todas":
            detalles += f", etapa {producto['etapa']}"
        filas.append(
            f"• {producto['nombre']} {detalles}: "
            f"{producto['stock']} en existencias, L {producto['precio']:.2f}."
        )
    return "Esto es lo que aparece en el inventario:\n" + "\n".join(filas)


def responder(pregunta: str, connection: sqlite3.Connection) -> str:
    texto = normalizar(pregunta)
    if any(normalizar(term) in texto for term in MEDICAL_ADVICE_TERMS):
        return (
            "Puedo consultar los productos y tratamientos registrados, pero no "
            "puedo indicar dosis, diagnosticar ni recomendar medicamentos. "
            "Consulta a un profesional veterinario."
        )

    if any(
        word in texto
        for word in (
            "alimento",
            "alimentos",
            "comida",
            "comidas",
            "concentrado",
            "premio",
            "premios",
            "suplemento",
            "dieta",
            "nutricion",
            "nutrición",
        )
    ):
        condiciones = ["activo = 1"]
        parametros: list[object] = []
        if "stock bajo" in texto or "poco stock" in texto:
            condiciones.append("stock <= 3")
        if "perro" in texto or "perros" in texto:
            condiciones.append("especie IN (?, ?)")
            parametros.extend(("perro", "universal"))
        elif "gato" in texto or "gatos" in texto:
            condiciones.append("especie IN (?, ?)")
            parametros.extend(("gato", "universal"))
        elif "ave" in texto or "aves" in texto:
            condiciones.append("especie IN (?, ?)")
            parametros.extend(("ave", "universal"))
        categoria = next(
            (
                category
                for phrase, category in (
                    ("concentrado", "concentrado"),
                    ("humedo", "humedo"),
                    ("premio", "premio"),
                    ("suplemento", "suplemento"),
                    ("dieta especial", "dieta_especial"),
                )
                if normalizar(phrase) in texto
            ),
            None,
        )
        if categoria:
            condiciones.append("categoria = ?")
            parametros.append(categoria)
        productos = connection.execute(
            "SELECT nombre, categoria, especie, etapa, stock, precio "
            "FROM alimentos WHERE "
            + " AND ".join(condiciones)
            + " ORDER BY nombre",
            parametros,
        ).fetchall()
        return formatear_inventario(productos)

    if any(word in texto for word in ("farmacia", "medicamento", "medicamentos", "pastilla", "pastillas", "shampoo", "champu", "higiene")):
        condiciones = ["activo = 1"]
        parametros: list[object] = []
        if "stock bajo" in texto or "poco stock" in texto:
            condiciones.append("stock <= 3")
        if "shampoo" in texto or "champu" in texto:
            condiciones.append("categoria = ?")
            parametros.append("shampoo")
        elif "pastilla" in texto:
            condiciones.append("categoria = ?")
            parametros.append("pastilla")
        elif "higiene" in texto:
            condiciones.append("categoria = ?")
            parametros.append("higiene")
        elif "medicamento" in texto:
            condiciones.append("categoria IN (?, ?)")
            parametros.extend(("medicamento", "pastilla"))
        productos = connection.execute(
            "SELECT nombre, categoria, stock, precio "
            "FROM productos_veterinarios WHERE "
            + " AND ".join(condiciones)
            + " ORDER BY nombre",
            parametros,
        ).fetchall()
        return formatear_inventario(productos)

    if any(word in texto for word in ("tienda", "accesorio", "accesorios", "correa", "collar", "juguete")):
        productos = connection.execute(
            "SELECT nombre, categoria, stock, precio FROM accesorios "
            "WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        return formatear_inventario(productos)

    if any(word in texto for word in ("tratamiento", "tratamientos", "historial")):
        tratamientos = connection.execute(
            """
            SELECT t.nombre, t.estado, t.fecha_inicio, m.nombre AS mascota
            FROM tratamientos AS t
            JOIN mascotas AS m ON m.id = t.mascota_id
            ORDER BY t.fecha_inicio DESC, t.id DESC
            LIMIT 10
            """
        ).fetchall()
        if not tratamientos:
            return "Todavía no hay tratamientos registrados."
        filas = [
            f"• {item['nombre']} — {item['mascota']}, {item['estado']} "
            f"(desde {item['fecha_inicio']})."
            for item in tratamientos
        ]
        return "Tratamientos registrados:\n" + "\n".join(filas)

    mascotas = connection.execute(
        """
        SELECT m.nombre, m.especie, m.raza, d.nombre AS dueno
        FROM mascotas AS m
        JOIN duenos AS d ON d.id = m.dueno_id
        ORDER BY m.nombre
        """
    ).fetchall()
    mascotas_mencionadas = [
        pet for pet in mascotas if normalizar(pet["nombre"]) in texto
    ]
    if mascotas_mencionadas:
        return "\n".join(
            f"• {pet['nombre']}: {pet['especie']}"
            + (f", raza {pet['raza']}" if pet["raza"] else "")
            + f". Dueño: {pet['dueno']}."
            for pet in mascotas_mencionadas
        )

    if any(word in texto for word in ("mascota", "mascotas", "paciente", "pacientes")):
        if any(word in texto for word in ("cuantas", "cuantos", "total")):
            return f"Hay {len(mascotas)} mascotas registradas en ZEUS VET."
        return (
            f"Hay {len(mascotas)} mascotas registradas. Puedes preguntarme por "
            "una mascota usando su nombre."
        )

    if any(word in texto for word in ("dueno", "duenos", "cliente", "clientes")):
        cantidad = connection.execute("SELECT COUNT(*) FROM duenos").fetchone()[0]
        return f"Hay {cantidad} dueños registrados en ZEUS VET."

    tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", texto)
        if token not in STOP_WORDS and len(token) > 2
    }
    if tokens:
        coincidencias = connection.execute(
            "SELECT nombre, categoria, stock, precio FROM productos_veterinarios "
            "WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        coincidencias += connection.execute(
            "SELECT nombre, categoria, stock, precio FROM accesorios "
            "WHERE activo = 1 ORDER BY nombre"
        ).fetchall()
        por_nombre = [
            producto
            for producto in coincidencias
            if tokens.intersection(normalizar(producto["nombre"]).split())
        ]
        if por_nombre:
            return formatear_inventario(por_nombre)

    return (
        "Puedo ayudarte a consultar la farmacia, la tienda, los tratamientos, "
        "las mascotas y los dueños registrados. Por ejemplo: "
        "«¿Qué medicamentos hay?» o «¿Cuántas mascotas hay?»"
    )


def obtener_conexion(
    connection: sqlite3.Connection = Depends(get_db),
) -> Generator[sqlite3.Connection, None, None]:
    yield connection


@router.post("/preguntar", response_model=RespuestaAsistente)
def preguntar(
    datos: PreguntaAsistente,
    connection: sqlite3.Connection = Depends(obtener_conexion),
) -> RespuestaAsistente:
    return RespuestaAsistente(respuesta=responder(datos.pregunta, connection))
