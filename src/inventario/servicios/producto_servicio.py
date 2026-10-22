"""Operaciones de negocio sobre los productos."""

from __future__ import annotations

from typing import Any, Mapping

from inventario.comun.errores import (
    ErrorNoEncontrado,
    ErrorValidacion,
    ProductoEnUsoError,
)
from inventario.comun.registro import obtener_logger
from inventario.dominio.categoria import Categoria
from inventario.dominio.producto import Producto
from inventario.repositorios.interfaces import CategoriaRepositorio, ProductoRepositorio

log = obtener_logger(__name__)


class ProductoServicio:
    def __init__(self, productos: ProductoRepositorio, categorias: CategoriaRepositorio) -> None:
        self._productos = productos
        self._categorias = categorias

    # ── Consultas ────────────────────────────────────────────────────────────
    def listar(self) -> list[Producto]:
        return self._productos.listar()

    def listar_categorias(self) -> list[Categoria]:
        return self._categorias.listar()

    def obtener(self, id_producto: int) -> Producto:
        producto = self._productos.obtener(id_producto)
        if producto is None:
            raise ErrorNoEncontrado()
        return producto

    # ── Comandos ─────────────────────────────────────────────────────────────
    def crear(self, datos: Mapping[str, Any]) -> Producto:
        producto = Producto.desde_datos(datos)
        self._verificar_categoria(producto.id_categoria)
        creado = self._productos.agregar(producto)
        log.info("Producto creado id=%s nombre=%r", creado.id, creado.nombre)
        return creado

    def actualizar(self, id_producto: int, datos: Mapping[str, Any]) -> Producto:
        self.obtener(id_producto)  # lanza ErrorNoEncontrado si no existe
        producto = Producto.desde_datos(datos, id=id_producto)
        self._verificar_categoria(producto.id_categoria)
        self._productos.actualizar(producto)
        log.info("Producto actualizado id=%s", id_producto)
        return producto

    def eliminar(self, id_producto: int) -> None:
        self.obtener(id_producto)
        if self._productos.esta_en_pedidos(id_producto):
            error = ProductoEnUsoError(id_producto)
            log.warning("Eliminación bloqueada: producto id=%s está en pedidos", id_producto)
            raise error
        self._productos.eliminar(id_producto)
        log.info("Producto eliminado id=%s", id_producto)

    # ── Reglas internas ──────────────────────────────────────────────────────
    def _verificar_categoria(self, id_categoria: int) -> None:
        if not self._categorias.existe(id_categoria):
            raise ErrorValidacion({"id_categoria": "La categoría seleccionada no existe."})
