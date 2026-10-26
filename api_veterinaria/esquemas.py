from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    especie: Literal["perro", "gato", "ave", "otro"]
    raza: str | None = Field(default=None, max_length=100)
    fecha_nacimiento: date | None = None
    dueno_id: int = Field(gt=0)

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


class MascotaRespuesta(MascotaEntrada):
    model_config = ConfigDict(from_attributes=True)

    id: int
