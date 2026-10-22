"""Lógica de la pantalla de productos, separada de los widgets."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Any, Mapping, Sequence

from inventario.comun.registro import obtener_logger
from inventario.dominio.producto import Producto
from inventario.presentacion.controladores.manejo_errores import ejecutar_accion
from inventario.presentacion.controladores.resultado import Resultado
from inventario.servicios.producto_servicio import ProductoServicio

log = obtener_logger("presentacion.productos")

SIN_CATEGORIAS = "Sin categorías"


CAMPOS_TABLA = ("id", "nombre", "descripcion", "precio", "stock", "nombre_categoria")
NO_EDITABLES = ("id", "id_categoria", "nombre_categoria")


def formatear(valor: Any) -> Any:
    if valor is None:
        return "—"
    if isinstance(valor, Decimal):
        return f"{valor:,.2f}"
    return valor


def fila_tabla(p: Producto, campos: Sequence[str] = CAMPOS_TABLA) -> tuple:
    return tuple(formatear(getattr(p, campo)) for campo in campos)


class ProductosControlador:
    def __init__(self, servicio: ProductoServicio) -> None:
        self._servicio = servicio
        self._categorias: dict[str, int] = {}
        self.id_editando: int | None = None

    # ── Estado ───────────────────────────────────────────────────────────────
    @property
    def editando(self) -> bool:
        return self.id_editando is not None

    @property
    def texto_boton_guardar(self) -> str:
        return "Actualizar" if self.editando else "Guardar Producto"

    @property
    def titulo_formulario(self) -> str:
        return f"Editando producto #{self.id_editando}" if self.editando else "Nuevo Producto"

    def cancelar_edicion(self) -> None:
        self.id_editando = None

    # ── Consultas ────────────────────────────────────────────────────────────
    def cargar_categorias(self) -> Resultado:
        def accion() -> Resultado:
            cats = self._servicio.listar_categorias()
            self._categorias = {c.nombre: c.id for c in cats}
            nombres = list(self._categorias) or [SIN_CATEGORIAS]
            return Resultado.ok(datos=nombres)

        resultado = ejecutar_accion("cargar categorías", accion, log)
        if not resultado.exito:
            return Resultado(False, resultado.mensaje, {}, ["(no disponible)"])
        return resultado

    def listar(self, campos: Sequence[str] = CAMPOS_TABLA) -> Resultado:
        return ejecutar_accion(
            "listar productos",
            lambda: Resultado.ok(datos=[fila_tabla(p, campos) for p in self._servicio.listar()]),
            log,
        )

    def iniciar_edicion(self, id_producto: int) -> Resultado:
        def accion() -> Resultado:
            p = self._servicio.obtener(int(id_producto))
            self.id_editando = p.id
            valores = {
                campo: "" if valor is None else str(valor)
                for campo, valor in asdict(p).items()
                if campo not in NO_EDITABLES
            }
            valores["categoria"] = p.nombre_categoria or ""
            return Resultado.ok(datos=valores)

        return ejecutar_accion("cargar producto para edición", accion, log)

    # ── Comandos ─────────────────────────────────────────────────────────────
    def guardar(self, valores: Mapping[str, str]) -> Resultado:
        # La categoría llega por nombre y se guarda por id
        datos = {clave: valor for clave, valor in valores.items() if clave != "categoria"}
        datos["id_categoria"] = self._categorias.get(valores.get("categoria", ""))

        def accion() -> Resultado:
            if self.editando:
                self._servicio.actualizar(self.id_editando, datos)
                self.id_editando = None
                return Resultado.ok("Producto actualizado correctamente.")
            self._servicio.crear(datos)
            return Resultado.ok("Producto agregado correctamente.")

        resultado = ejecutar_accion("guardar producto", accion, log)
        if "id_categoria" in resultado.errores:
            errores = dict(resultado.errores)
            errores["categoria"] = errores.pop("id_categoria")
            return Resultado.fallo(resultado.mensaje, errores)
        return resultado

    def eliminar(self, id_producto: int | None) -> Resultado:
        if id_producto is None:
            return Resultado.fallo("Selecciona un producto de la tabla.")

        def accion() -> Resultado:
            self._servicio.eliminar(int(id_producto))
            if self.id_editando == int(id_producto):
                self.id_editando = None
            return Resultado.ok("Producto eliminado.")

        return ejecutar_accion("eliminar producto", accion, log)
