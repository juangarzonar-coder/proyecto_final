"""Interfaces que deben cumplir los repositorios."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from inventario.dominio.categoria import Categoria
from inventario.dominio.producto import Producto


@runtime_checkable
class ProductoRepositorio(Protocol):
    def listar(self) -> list[Producto]: ...

    def obtener(self, id_producto: int) -> Producto | None: ...

    def agregar(self, producto: Producto) -> Producto:
        """Devuelve el producto con el id asignado."""
        ...

    def actualizar(self, producto: Producto) -> None: ...

    def eliminar(self, id_producto: int) -> None: ...

    def esta_en_pedidos(self, id_producto: int) -> bool: ...


@runtime_checkable
class CategoriaRepositorio(Protocol):
    def listar(self) -> list[Categoria]: ...

    def existe(self, id_categoria: int) -> bool: ...
