"""Objetos falsos y datos de prueba."""

from __future__ import annotations

from decimal import Decimal

from inventario.dominio.categoria import Categoria
from inventario.dominio.producto import Producto
from inventario.repositorios.memoria import CategoriaRepositorioMemoria, ProductoRepositorioMemoria
from inventario.servicios.producto_servicio import ProductoServicio

DATOS_VALIDOS = {
    "nombre": "Jabón industrial",
    "descripcion": "Galón",
    "precio": "15000",
    "stock": "10",
    "id_categoria": 1,
}


def crear_servicio(en_pedidos=(1,)):
    cats = CategoriaRepositorioMemoria([Categoria(1, "Hogar"), Categoria(2, "Vehículos")])
    repo = ProductoRepositorioMemoria(
        cats,
        [
            Producto("Limpiavidrios", Decimal("8000"), 30, 1),
            Producto("Cera para carro", Decimal("22000"), 5, 2),
        ],
        productos_en_pedidos=en_pedidos,
    )
    return ProductoServicio(repo, cats), repo


class ErrorPyodbcFalso(Exception):
    """Imita pyodbc.Error: args[0] es el SQLSTATE."""


class IntegrityError(ErrorPyodbcFalso):
    pass


class CursorFalso:
    def __init__(self, resultados=(), error=None, rowcount=1):
        self._resultados = list(resultados)
        self._error = error
        self.rowcount = rowcount
        self.ejecutados = []
        self.cerrado = False

    def execute(self, sql, params=()):
        self.ejecutados.append((sql, params))
        if self._error:
            raise self._error

    def fetchall(self):
        return list(self._resultados)

    def fetchone(self):
        return self._resultados[0] if self._resultados else None

    def close(self):
        self.cerrado = True


class ConexionFalsa:
    def __init__(self, cursor: CursorFalso):
        self._cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.cerrada = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.cerrada = True
