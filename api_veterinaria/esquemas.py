from datetime import date, datetime
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

IMAGE_URL_PATTERN = re.compile(
    r"^/static/images/uploads/[a-f0-9]{32}\.(?:jpg|png|webp)$"
)


class DuenoEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    telefono: str = Field(min_length=8, max_length=30)
    direccion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre", "telefono")
    @classmethod
    def quitar_espacios(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("direccion")
    @classmethod
    def normalizar_direccion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class DuenoRespuesta(DuenoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MascotaEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    especie: Literal[
        "perro", "gato", "ave", "gallina", "caballo", "vaca", "otro"
    ]
    raza: str | None = Field(default=None, max_length=100)
    fecha_nacimiento: date | None = None
    dueno_id: int = Field(gt=0)
    imagen_url: str | None = Field(default=None, max_length=255)

    @field_validator("nombre")
    @classmethod
    def normalizar_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío.")
        return value

    @field_validator("raza")
    @classmethod
    def normalizar_raza(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("imagen_url")
    @classmethod
    def validar_imagen_url(cls, value: str | None) -> str | None:
        if value is not None and not IMAGE_URL_PATTERN.fullmatch(value):
            raise ValueError("La imagen debe ser una foto cargada en el sistema.")
        return value


class MascotaRespuesta(MascotaEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InventarioEntrada(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str
    descripcion: str = Field(min_length=1, max_length=500)
    uso: str = Field(min_length=1, max_length=500)
    precio: float = Field(ge=0)
    stock: int = Field(ge=0)
    activo: bool = True
    imagen_url: str | None = Field(default=None, max_length=255)

    @field_validator("nombre", "categoria")
    @classmethod
    def normalizar_texto_requerido(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("descripcion", "uso")
    @classmethod
    def normalizar_descripcion(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("imagen_url")
    @classmethod
    def validar_imagen_url(cls, value: str | None) -> str | None:
        if value is not None and not IMAGE_URL_PATTERN.fullmatch(value):
            raise ValueError("La imagen debe ser una foto cargada en el sistema.")
        return value


class AccesorioEntrada(InventarioEntrada):
    categoria: Literal["collar", "correa", "juguete", "ropa", "cama", "transporte", "otro"]


class AccesorioRespuesta(AccesorioEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ProductoVeterinarioEntrada(InventarioEntrada):
    categoria: Literal["medicamento", "pastilla", "shampoo", "higiene", "otro"]


class ProductoVeterinarioRespuesta(ProductoVeterinarioEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AlimentoEntrada(InventarioEntrada):
    categoria: Literal[
        "concentrado", "humedo", "premio", "suplemento", "dieta_especial"
    ]
    especie: Literal["perro", "gato", "ave", "universal"] = "universal"
    etapa: Literal["cachorro", "adulto", "senior", "todas"] = "todas"


class AlimentoRespuesta(AlimentoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TratamientoEntrada(BaseModel):
    mascota_id: int = Field(gt=0)
    producto_id: int | None = Field(default=None, gt=0)
    nombre: str = Field(min_length=1, max_length=120)
    indicaciones: str = Field(min_length=1, max_length=1000)
    dosis: str | None = Field(default=None, max_length=200)
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: Literal["recetado", "en_curso", "completado", "suspendido"] = "recetado"

    @field_validator("nombre", "indicaciones")
    @classmethod
    def normalizar_texto_tratamiento(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("dosis")
    @classmethod
    def normalizar_dosis(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def validar_periodo(self) -> "TratamientoEntrada":
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial.")
        return self


class TratamientoRespuesta(TratamientoEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PreguntaAsistente(BaseModel):
    pregunta: str = Field(min_length=1, max_length=500)

    @field_validator("pregunta")
    @classmethod
    def normalizar_pregunta(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Escribe una pregunta.")
        return value


class RespuestaAsistente(BaseModel):
    respuesta: str


class CitaEntrada(BaseModel):
    mascota_id: int = Field(gt=0)
    veterinario_id: int = Field(gt=0)
    fecha_hora: datetime
    motivo: str = Field(min_length=1, max_length=500)
    estado: Literal["programada", "atendida", "cancelada"] = "programada"

    @field_validator("motivo")
    @classmethod
    def normalizar_motivo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El motivo no puede estar vacío.")
        return value


class VacunaEntrada(BaseModel):
    mascota_id: int = Field(gt=0)
    vacuna: str = Field(min_length=1, max_length=120)
    fecha: date
    proxima_dosis: date | None = None

    @field_validator("vacuna")
    @classmethod
    def normalizar_vacuna(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre de la vacuna no puede estar vacío.")
        return value

    @model_validator(mode="after")
    def validar_proxima_dosis(self) -> "VacunaEntrada":
        if self.proxima_dosis is not None and self.proxima_dosis <= self.fecha:
            raise ValueError("La próxima dosis debe ser posterior a la fecha aplicada.")
        return self


class LoteFarmaciaEntrada(BaseModel):
    producto_id: int = Field(gt=0)
    numero_lote: str = Field(min_length=1, max_length=80)
    proveedor: str | None = Field(default=None, max_length=160)
    vencimiento: date
    stock: int = Field(ge=0)

    @field_validator("numero_lote")
    @classmethod
    def normalizar_numero_lote(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El número de lote no puede estar vacío.")
        return value

    @field_validator("proveedor")
    @classmethod
    def normalizar_proveedor(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class UsuarioEntrada(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9._-]+$")
    correo: str = Field(min_length=5, max_length=254)
    nombre_completo: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=128)
    rol: Literal["administrador", "veterinario", "recepcion"] = "recepcion"

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Escribe un correo electrónico válido.")
        return value

    @field_validator("nombre_completo")
    @classmethod
    def normalizar_nombre_completo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío.")
        return value


class UsuarioActualizarEntrada(BaseModel):
    rol: Literal["administrador", "veterinario", "recepcion"]
    activo: bool


class CambioPasswordEntrada(BaseModel):
    password_actual: str = Field(min_length=1, max_length=128)
    password_nueva: str = Field(min_length=12, max_length=128)


class CredencialesEntrada(BaseModel):
    nombre_usuario: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=128)
