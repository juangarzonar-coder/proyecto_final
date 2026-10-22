"""Configuración del log de la aplicación (logs/app.log)."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

RAIZ_LOGGER = "inventario"
FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_registro(
    ruta_archivo: str | os.PathLike | None = None,
    nivel: int = logging.INFO,
) -> logging.Logger:
    """Agrega el archivo de log al logger principal (solo una vez)."""
    ruta = Path(ruta_archivo or os.getenv("INVENTARIO_LOG", "logs/app.log"))
    ruta.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(RAIZ_LOGGER)
    logger.setLevel(nivel)

    ya_configurado = any(
        isinstance(h, RotatingFileHandler) and Path(h.baseFilename) == ruta.resolve()
        for h in logger.handlers
    )
    if not ya_configurado:
        manejador = RotatingFileHandler(
            ruta, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        manejador.setFormatter(logging.Formatter(FORMATO))
        logger.addHandler(manejador)
    return logger


def obtener_logger(nombre: str) -> logging.Logger:
    if nombre == RAIZ_LOGGER or nombre.startswith(RAIZ_LOGGER + "."):
        return logging.getLogger(nombre)
    return logging.getLogger(f"{RAIZ_LOGGER}.{nombre}")
