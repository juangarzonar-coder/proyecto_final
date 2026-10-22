"""Resultado que el controlador le devuelve a la vista."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Resultado:
    exito: bool
    mensaje: str = ""
    errores: dict[str, str] = field(default_factory=dict)
    datos: Any = None

    @classmethod
    def ok(cls, mensaje: str = "", datos: Any = None) -> "Resultado":
        return cls(True, mensaje, {}, datos)

    @classmethod
    def fallo(cls, mensaje: str, errores: dict[str, str] | None = None) -> "Resultado":
        return cls(False, mensaje, dict(errores or {}))
