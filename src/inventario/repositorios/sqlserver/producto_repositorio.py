"""Acceso a la tabla Producto en SQL Server."""

from __future__ import annotations

from decimal import Decimal

from inventario.comun.errores import ErrorNoEncontrado, ProductoEnUsoError
from inventario.dominio.producto import Producto
from inventario.repositorios.sqlserver.conexion import ErrorIntegridad, GestorConexion

_SELECT_BASE = """
    SELECT p.id_producto, p.Nombre_producto, p.Descripcion, p.Precio, p.Stock,
           p.id_categoria, c.Nombre_categoria
    FROM Producto p
    LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
"""


def _a_producto(fila) -> Producto:
    id_, nombre, descripcion, precio, stock, id_categoria, nombre_categoria = fila
    return Producto(
        id=int(id_),
        nombre=nombre,
        descripcion=descripcion or "",
        precio=Decimal(str(precio)),
        stock=int(stock),
        id_categoria=int(id_categoria),
        nombre_categoria=nombre_categoria,
    )


class ProductoRepositorioSQL:
    def __init__(self, gestor: GestorConexion) -> None:
        self._gestor = gestor

    def listar(self) -> list[Producto]:
        with self._gestor.cursor("listar productos") as cur:
            cur.execute(_SELECT_BASE + " ORDER BY p.id_producto")
            return [_a_producto(f) for f in cur.fetchall()]

    def obtener(self, id_producto: int) -> Producto | None:
        with self._gestor.cursor("obtener producto") as cur:
            cur.execute(_SELECT_BASE + " WHERE p.id_producto = ?", (id_producto,))
            fila = cur.fetchone()
            return _a_producto(fila) if fila else None

    def agregar(self, producto: Producto) -> Producto:
        with self._gestor.cursor("insertar producto") as cur:
            cur.execute(
                "INSERT INTO Producto (Nombre_producto, Descripcion, Precio, Stock, id_categoria) "
                "OUTPUT INSERTED.id_producto VALUES (?, ?, ?, ?, ?)",
                (
                    producto.nombre,
                    producto.descripcion,
                    producto.precio,
                    producto.stock,
                    producto.id_categoria,
                ),
            )
            nuevo_id = int(cur.fetchone()[0])
        return producto.con_id(nuevo_id)

    def actualizar(self, producto: Producto) -> None:
        with self._gestor.cursor("actualizar producto") as cur:
            cur.execute(
                "UPDATE Producto SET Nombre_producto=?, Descripcion=?, Precio=?, Stock=?, "
                "id_categoria=? WHERE id_producto=?",
                (
                    producto.nombre,
                    producto.descripcion,
                    producto.precio,
                    producto.stock,
                    producto.id_categoria,
                    producto.id,
                ),
            )
            if cur.rowcount == 0:
                raise ErrorNoEncontrado()

    def eliminar(self, id_producto: int) -> None:
        try:
            with self._gestor.cursor("eliminar producto") as cur:
                cur.execute("DELETE FROM Producto WHERE id_producto = ?", (id_producto,))
                if cur.rowcount == 0:
                    raise ErrorNoEncontrado()
        except ErrorIntegridad as exc:
            # El producto tiene registros en DetallePedido
            raise ProductoEnUsoError(id_producto, causa=exc) from exc

    def esta_en_pedidos(self, id_producto: int) -> bool:
        with self._gestor.cursor("verificar uso en pedidos") as cur:
            cur.execute(
                "SELECT COUNT(*) FROM DetallePedido WHERE id_producto = ?", (id_producto,)
            )
            return int(cur.fetchone()[0]) > 0
