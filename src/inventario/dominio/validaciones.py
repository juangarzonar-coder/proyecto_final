"""Funciones de validación para los datos de los formularios.

Cada función recibe el valor tal como llega, lo devuelve convertido y lanza
ValueError si no es válido."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Callable, TypeVar

from inventario.comun.errores import ErrorValidacion

T = TypeVar("T")


def texto_requerido(valor: Any, *, maximo: int | None = None) -> str:
    texto = "" if valor is None else str(valor).strip()
    if not texto:
        raise ValueError("Es obligatorio.")
    return texto_opcional(texto, maximo=maximo)


def texto_opcional(valor: Any, *, maximo: int | None = None) -> str:
    texto = "" if valor is None else str(valor).strip()
    if maximo is not None and len(texto) > maximo:
        raise ValueError(f"Máximo {maximo} caracteres.")
    return texto


def decimal_positivo(valor: Any) -> Decimal:
    """Número mayor que cero; acepta coma o punto como separador decimal."""
    texto = "" if valor is None else str(valor).strip().replace(",", ".")
    if not texto:
        raise ValueError("Es obligatorio.")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        raise ValueError("Debe ser un número válido.") from None
    if not numero.is_finite():
        raise ValueError("Debe ser un número válido.")
    if numero <= 0:
        raise ValueError("Debe ser mayor que cero.")
    return numero.quantize(Decimal("0.01"))


def entero_no_negativo(valor: Any) -> int:
    """Número entero mayor o igual a cero."""
    if isinstance(valor, bool):
        raise ValueError("Debe ser un número entero.")
    if isinstance(valor, int):
        numero = valor
    else:
        texto = "" if valor is None else str(valor).strip()
        if not texto:
            raise ValueError("Es obligatorio.")
        try:
            numero = int(texto)
        except ValueError:
            raise ValueError("Debe ser un número entero.") from None
    if numero < 0:
        raise ValueError("No puede ser negativo.")
    return numero


def id_requerido(valor: Any) -> int:
    if valor in (None, ""):
        raise ValueError("Seleccione una opción.")
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError("Selección inválida.") from None
    if numero <= 0:
        raise ValueError("Selección inválida.")
    return numero


class ColectorErrores:
    """Junta los errores de varios campos para mostrarlos todos juntos."""

    def __init__(self) -> None:
        self.errores: dict[str, str] = {}

    def validar(self, campo: str, regla: Callable[..., T], valor: Any, **kwargs: Any) -> T | None:
        try:
            return regla(valor, **kwargs)
        except ValueError as exc:
            self.errores[campo] = str(exc)
            return None

    def lanzar_si_hay_errores(self) -> None:
        if self.errores:
            raise ErrorValidacion(self.errores)
