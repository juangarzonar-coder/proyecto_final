"""Repositorios en memoria, usados en las pruebas y en el modo demo."""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from inventario.comun.errores import ErrorNoEncontrado, ProductoEnUsoError
from inventario.dominio.categoria import Categoria
from inventario.dominio.producto import Producto


class CategoriaRepositorioMemoria:
    def __init__(self, categorias: Iterable[Categoria] = ()) -> None:
        self._datos = {c.id: c for c in categorias}

    def listar(self) -> list[Categoria]:
        return sorted(self._datos.values(), key=lambda c: c.nombre)

    def existe(self, id_categoria: int) -> bool:
        return id_categoria in self._datos

    def nombre_de(self, id_categoria: int) -> str | None:
        cat = self._datos.get(id_categoria)
        return cat.nombre if cat else None


class ProductoRepositorioMemoria:
    def __init__(
        self,
        categorias: CategoriaRepositorioMemoria | None = None,
        productos: Iterable[Producto] = (),
        productos_en_pedidos: Iterable[int] = (),
    ) -> None:
        self._categorias = categorias or CategoriaRepositorioMemoria()
        self._datos: dict[int, Producto] = {}
        self._siguiente_id = 1
        # ids de productos que están en algún pedido
        self.productos_en_pedidos: set[int] = set(productos_en_pedidos)
        for p in productos:
            self.agregar(p)

    def _con_nombre_categoria(self, p: Producto) -> Producto:
        return p.con_categoria(self._categorias.nombre_de(p.id_categoria))

    def listar(self) -> list[Producto]:
        return [self._con_nombre_categoria(p) for p in sorted(self._datos.values(), key=lambda p: p.id)]

    def obtener(self, id_producto: int) -> Producto | None:
        p = self._datos.get(id_producto)
        return self._con_nombre_categoria(p) if p else None

    def agregar(self, producto: Producto) -> Producto:
        nuevo = producto.con_id(self._siguiente_id)
        self._datos[nuevo.id] = nuevo
        self._siguiente_id += 1
        return self._con_nombre_categoria(nuevo)

    def actualizar(self, producto: Producto) -> None:
        if producto.id not in self._datos:
            raise ErrorNoEncontrado()
        self._datos[producto.id] = producto

    def eliminar(self, id_producto: int) -> None:
        if id_producto in self.productos_en_pedidos:
            raise ProductoEnUsoError(id_producto)
        if self._datos.pop(id_producto, None) is None:
            raise ErrorNoEncontrado()

    def esta_en_pedidos(self, id_producto: int) -> bool:
        return id_producto in self.productos_en_pedidos


def datos_demo() -> tuple[ProductoRepositorioMemoria, CategoriaRepositorioMemoria]:
    """Datos de ejemplo para el modo demo."""
    cats = CategoriaRepositorioMemoria(
        [Categoria(1, "Hogar"), Categoria(2, "Vehículos"), Categoria(3, "Industrial")]
    )
    productos = ProductoRepositorioMemoria(
        cats,
        [
            Producto("Jabón líquido multiusos", Decimal("12500"), 40, 1, "Envase 1 L"),
            Producto("Shampoo para carro", Decimal("18900"), 25, 2, "Con cera"),
            Producto("Desengrasante industrial", Decimal("32000"), 12, 3, "Galón"),
        ],
        productos_en_pedidos=[1],
    )
    return productos, cats
