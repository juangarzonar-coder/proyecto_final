"""Configuración de la base de datos a partir de variables de entorno.

Variables: INVENTARIO_REPO (sqlserver o memoria), INVENTARIO_DB_DRIVER,
INVENTARIO_DB_SERVER, INVENTARIO_DB_NAME, INVENTARIO_DB_USER,
INVENTARIO_DB_PASSWORD e INVENTARIO_DB_TIMEOUT."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfiguracionBD:
    driver: str = "ODBC Driver 17 for SQL Server"
    servidor: str = "localhost"
    base_datos: str = "EmpresaLimpiezaDB"
    usuario: str | None = None
    clave: str | None = None
    timeout: int = 5

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionBD":
        return cls(
            driver=os.getenv("INVENTARIO_DB_DRIVER", cls.driver),
            servidor=os.getenv("INVENTARIO_DB_SERVER", cls.servidor),
            base_datos=os.getenv("INVENTARIO_DB_NAME", cls.base_datos),
            usuario=os.getenv("INVENTARIO_DB_USER") or None,
            clave=os.getenv("INVENTARIO_DB_PASSWORD") or None,
            timeout=int(os.getenv("INVENTARIO_DB_TIMEOUT", cls.timeout)),
        )

    def cadena_conexion(self) -> str:
        partes = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.servidor}",
            f"DATABASE={self.base_datos}",
        ]
        if self.usuario:
            partes += [f"UID={self.usuario}", f"PWD={self.clave or ''}"]
        else:
            partes.append("Trusted_Connection=yes")
        return ";".join(partes) + ";"


def modo_repositorio() -> str:
    return os.getenv("INVENTARIO_REPO", "sqlserver").strip().lower()
