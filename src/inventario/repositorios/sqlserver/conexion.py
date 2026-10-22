"""Conexión a SQL Server y conversión de sus errores a excepciones propias."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterator

from inventario.comun.errores import (
    ErrorAplicacion,
    ErrorConexion,
    ErrorPersistencia,
    ErrorReglaNegocio,
)
from inventario.comun.registro import obtener_logger
from inventario.config import ConfiguracionBD

log = obtener_logger(__name__)

# Códigos SQLSTATE de pyodbc
SQLSTATE_INTEGRIDAD = "23000"
PREFIJOS_CONEXION = ("08", "HYT")


class ErrorIntegridad(ErrorReglaNegocio):
    """Error por llave foránea, UNIQUE o NOT NULL."""


def _sqlstate(exc: BaseException) -> str:
    args = getattr(exc, "args", ())
    return str(args[0]) if args else ""


def traducir_error_bd(exc: BaseException, operacion: str) -> ErrorAplicacion:
    estado = _sqlstate(exc)
    if estado.startswith(PREFIJOS_CONEXION) or type(exc).__name__ == "InterfaceError":
        return ErrorConexion(f"Fallo de conexión durante '{operacion}' ({estado})", causa=exc)
    if estado == SQLSTATE_INTEGRIDAD or type(exc).__name__ == "IntegrityError":
        return ErrorIntegridad(
            f"Violación de integridad durante '{operacion}' ({estado})", causa=exc
        )
    return ErrorPersistencia(f"Error de base de datos durante '{operacion}' ({estado})", causa=exc)


def _conectar_pyodbc(config: ConfiguracionBD) -> Any:
    import pyodbc  # se importa aquí para que las pruebas no lo necesiten

    return pyodbc.connect(config.cadena_conexion(), timeout=config.timeout)


class GestorConexion:
    def __init__(
        self,
        config: ConfiguracionBD | None = None,
        conectar: Callable[[ConfiguracionBD], Any] | None = None,
    ) -> None:
        self.config = config or ConfiguracionBD.desde_entorno()
        self._conectar = conectar or _conectar_pyodbc

    @contextmanager
    def cursor(self, operacion: str = "consulta") -> Iterator[Any]:
        try:
            con = self._conectar(self.config)
        except ErrorAplicacion:
            raise
        except Exception as exc:  # pyodbc no tiene una jerarquía de errores fiable
            error = traducir_error_bd(exc, operacion)
            if not isinstance(error, ErrorConexion):
                error = ErrorConexion(f"No se pudo abrir la conexión ({_sqlstate(exc)})", causa=exc)
            log.error("%s | %r", error.mensaje, exc)
            raise error from exc

        cur = con.cursor()
        try:
            yield cur
            con.commit()
        except ErrorAplicacion:
            con.rollback()
            raise
        except Exception as exc:
            con.rollback()
            error = traducir_error_bd(exc, operacion)
            log.error("%s | %r", error.mensaje, exc)
            raise error from exc
        finally:
            cur.close()
            con.close()
