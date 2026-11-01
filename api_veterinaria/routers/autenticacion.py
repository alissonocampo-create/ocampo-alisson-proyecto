import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from database import get_db
from esquemas import (
    CambioPasswordEntrada,
    CredencialesEntrada,
    UsuarioActualizarEntrada,
    UsuarioEntrada,
)

router = APIRouter(prefix="/auth", tags=["Acceso"])
SESSION_COOKIE = "zeus_session"
SESSION_HOURS = 8
PASSWORD_ITERATIONS = 310_000


def _encoded(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def crear_hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256:{PASSWORD_ITERATIONS}:{_encoded(salt)}:{_encoded(digest)}"


def verificar_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, rounds, salt, digest = stored_hash.split(":")
        iterations = int(rounds)
        if algorithm != "pbkdf2_sha256" or not 100_000 <= iterations <= 600_000:
            return False
        salt_bytes = base64.urlsafe_b64decode(salt + "=" * (-len(salt) % 4))
        expected = base64.urlsafe_b64decode(digest + "=" * (-len(digest) % 4))
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt_bytes, iterations
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def obtener_usuario_actual(request: Request) -> dict[str, object]:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inicia sesión para continuar.",
        )
    return user


def _guardar_sesion(
    connection: sqlite3.Connection,
    user_id: int,
    response: Response,
    request: Request,
) -> None:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=SESSION_HOURS)
    connection.execute(
        "INSERT INTO sesiones (token_hash, usuario_id, creada_en, expira_en) "
        "VALUES (?, ?, ?, ?)",
        (
            hashlib.sha256(token.encode("ascii")).hexdigest(),
            user_id,
            now.isoformat(),
            expires.isoformat(),
        ),
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_HOURS * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/",
    )


@router.post("/login")
def iniciar_sesion(
    datos: CredencialesEntrada,
    request: Request,
    response: Response,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    address = request.client.host if request.client else "desconocido"
    attempt = connection.execute(
        "SELECT intentos, ultimo_intento FROM intentos_acceso WHERE direccion_ip = ?",
        (address,),
    ).fetchone()
    now = datetime.now(timezone.utc)
    if attempt is not None:
        last_attempt = datetime.fromisoformat(attempt["ultimo_intento"])
        if now - last_attempt < timedelta(minutes=15) and attempt["intentos"] >= 5:
            raise HTTPException(
                status_code=429,
                detail="Demasiados intentos. Espera 15 minutos antes de volver a probar.",
            )

    user = connection.execute(
        """
        SELECT id, nombre_usuario, nombre_completo, password_hash, rol, activo
        FROM usuarios WHERE nombre_usuario = ?
        """,
        (datos.nombre_usuario.strip(),),
    ).fetchone()
    valid = user is not None and bool(user["activo"]) and verificar_password(
        datos.password, user["password_hash"]
    )
    if not valid:
        if attempt is None:
            connection.execute(
                "INSERT INTO intentos_acceso (direccion_ip, intentos, ultimo_intento) "
                "VALUES (?, 1, ?)",
                (address, now.isoformat()),
            )
        elif now - datetime.fromisoformat(attempt["ultimo_intento"]) >= timedelta(
            minutes=15
        ):
            connection.execute(
                "UPDATE intentos_acceso SET intentos = 1, ultimo_intento = ? "
                "WHERE direccion_ip = ?",
                (now.isoformat(), address),
            )
        else:
            connection.execute(
                "UPDATE intentos_acceso SET intentos = intentos + 1, ultimo_intento = ? "
                "WHERE direccion_ip = ?",
                (now.isoformat(), address),
            )
        connection.commit()
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    connection.execute(
        "DELETE FROM intentos_acceso WHERE direccion_ip = ?", (address,)
    )
    _guardar_sesion(connection, user["id"], response, request)
    connection.commit()
    return {
        "id": user["id"],
        "nombre_usuario": user["nombre_usuario"],
        "nombre_completo": user["nombre_completo"],
        "rol": user["rol"],
    }


@router.get("/me")
def consultar_sesion(
    user: dict[str, object] = Depends(obtener_usuario_actual),
) -> dict[str, object]:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(
    request: Request,
    response: Response,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
        connection.execute("DELETE FROM sesiones WHERE token_hash = ?", (token_hash,))
        connection.commit()
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    datos: CambioPasswordEntrada,
    request: Request,
    response: Response,
    user: dict[str, object] = Depends(obtener_usuario_actual),
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    account = connection.execute(
        "SELECT password_hash FROM usuarios WHERE id = ?", (user["id"],)
    ).fetchone()
    if account is None or not verificar_password(
        datos.password_actual, account["password_hash"]
    ):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta.")
    connection.execute(
        "UPDATE usuarios SET password_hash = ? WHERE id = ?",
        (crear_hash_password(datos.password_nueva), user["id"]),
    )
    connection.execute("DELETE FROM sesiones WHERE usuario_id = ?", (user["id"],))
    connection.commit()
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/usuarios")
def listar_usuarios(
    connection: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, nombre_usuario, correo, nombre_completo, rol, activo, creado_en
        FROM usuarios ORDER BY nombre_completo COLLATE NOCASE
        """
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioEntrada,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    cursor = connection.execute(
        """
        INSERT INTO usuarios (
            nombre_usuario, correo, nombre_completo, password_hash, rol
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            datos.nombre_usuario,
            datos.correo,
            datos.nombre_completo,
            crear_hash_password(datos.password),
            datos.rol,
        ),
    )
    connection.commit()
    return {
        "id": cursor.lastrowid,
        "nombre_usuario": datos.nombre_usuario,
        "correo": datos.correo,
        "nombre_completo": datos.nombre_completo,
        "rol": datos.rol,
        "activo": True,
    }


@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioActualizarEntrada,
    user: dict[str, object] = Depends(obtener_usuario_actual),
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, object]:
    existing = connection.execute(
        "SELECT id, rol, activo FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    if existing is None:
        raise HTTPException(status_code=404, detail="No se encontró la cuenta.")
    if user["id"] == usuario_id and (
        datos.rol != existing["rol"] or datos.activo != bool(existing["activo"])
    ):
        raise HTTPException(
            status_code=409,
            detail="No puedes cambiar tu propio perfil o desactivar tu cuenta.",
        )
    if existing["rol"] == "administrador" and (
        datos.rol != "administrador" or not datos.activo
    ):
        other_admins = connection.execute(
            """
            SELECT COUNT(*) FROM usuarios
            WHERE rol = 'administrador' AND activo = 1 AND id != ?
            """,
            (usuario_id,),
        ).fetchone()[0]
        if other_admins == 0:
            raise HTTPException(
                status_code=409,
                detail="Debe quedar al menos una cuenta de administración activa.",
            )
    connection.execute(
        "UPDATE usuarios SET rol = ?, activo = ? WHERE id = ?",
        (datos.rol, int(datos.activo), usuario_id),
    )
    connection.commit()
    row = connection.execute(
        """
        SELECT id, nombre_usuario, correo, nombre_completo, rol, activo, creado_en
        FROM usuarios WHERE id = ?
        """,
        (usuario_id,),
    ).fetchone()
    return dict(row)
