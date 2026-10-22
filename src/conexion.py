"""Conexión usada por los módulos que todavía usan crud/."""
import pyodbc

from inventario.config import ConfiguracionBD


def conectar():
    config = ConfiguracionBD.desde_entorno()
    return pyodbc.connect(config.cadena_conexion(), timeout=config.timeout)
