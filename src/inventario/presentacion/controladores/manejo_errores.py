"""Convierte las excepciones en mensajes para el usuario y las registra en el log."""

from __future__ import annotations

import logging
from typing import Callable, TypeVar

from inventario.comun.errores import (
    ErrorAplicacion,
    ErrorNoEncontrado,
    ErrorPersistencia,
    ErrorReglaNegocio,
    ErrorValidacion,
)
from inventario.comun.registro import obtener_logger
from inventario.presentacion.controladores.resultado import Resultado

T = TypeVar("T")

MENSAJE_INESPERADO = "Ocurrió un error inesperado. El detalle quedó registrado para soporte."


def ejecutar_accion(
    operacion: str,
    accion: Callable[[], Resultado],
    log: logging.Logger | None = None,
) -> Resultado:
    log = log or obtener_logger("presentacion")
    try:
        return accion()
    except ErrorValidacion as exc:
        log.info("[%s] validación rechazada: %s", operacion, exc.errores)
        return Resultado.fallo(exc.mensaje_usuario, exc.errores)
    except (ErrorReglaNegocio, ErrorNoEncontrado) as exc:
        log.warning("[%s] %s: %s", operacion, type(exc).__name__, exc.mensaje)
        return Resultado.fallo(exc.mensaje_usuario)
    except ErrorPersistencia as exc:
        log.error("[%s] %s: %s | causa=%r", operacion, type(exc).__name__, exc.mensaje, exc.causa)
        return Resultado.fallo(exc.mensaje_usuario)
    except ErrorAplicacion as exc:
        log.error("[%s] %s: %s", operacion, type(exc).__name__, exc.mensaje)
        return Resultado.fallo(exc.mensaje_usuario)
    except Exception:  # cualquier otro error se registra y la app sigue abierta
        log.exception("[%s] error inesperado", operacion)
        return Resultado.fallo(MENSAJE_INESPERADO)
