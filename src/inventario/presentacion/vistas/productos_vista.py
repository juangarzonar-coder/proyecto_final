"""Pantalla de gestión de productos."""

from __future__ import annotations

import customtkinter as ctk

from interfaces.estilos import (
    btn_back,
    btn_danger,
    btn_primary,
    confirm_delete,
    section_title,
    show_error,
    show_success,
)
from inventario.arranque import crear_controlador_productos
from inventario.presentacion.componentes.formulario import Campo, FormularioCRUD
from inventario.presentacion.componentes.tabla import TablaCRUD
from inventario.presentacion.controladores.productos_controlador import ProductosControlador

CAMPOS = [
    Campo("nombre", "Nombre", "Ej: Jabón industrial"),
    Campo("descripcion", "Descripción", "Descripción breve"),
    Campo("precio", "Precio", "0.00"),
    Campo("stock", "Stock", "0"),
    Campo("categoria", "Categoría", tipo="opciones"),
]

# "campo" es el atributo de Producto que va en cada columna
COLUMNAS = [
    {"id": "id", "campo": "id", "text": "ID", "width": 50, "anchor": "center"},
    {"id": "nom", "campo": "nombre", "text": "Nombre", "width": 180},
    {"id": "desc", "campo": "descripcion", "text": "Descripción", "width": 200},
    {"id": "prec", "campo": "precio", "text": "Precio", "width": 90, "anchor": "e"},
    {"id": "stk", "campo": "stock", "text": "Stock", "width": 70, "anchor": "center"},
    {"id": "cat", "campo": "nombre_categoria", "text": "Categoría", "width": 130},
]
CAMPOS_TABLA = [c["campo"] for c in COLUMNAS]


def abrir_productos(contenedor_principal, controlador: ProductosControlador | None = None):
    for w in contenedor_principal.winfo_children():
        w.destroy()
    VistaProductos(contenedor_principal, controlador or crear_controlador_productos())


class VistaProductos:
    def __init__(self, contenedor, controlador: ProductosControlador) -> None:
        self.contenedor = contenedor
        self.ctrl = controlador
        self._construir()
        self._cargar_categorias()
        self.refrescar()

    # ── Construcción ─────────────────────────────────────────────────────────
    def _construir(self) -> None:
        header = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        btn_back(header, self._volver).pack(side="left")
        section_title(header, "Gestión de Productos", "📦").pack(side="left", padx=20)

        body = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.form = FormularioCRUD(body, self.ctrl.titulo_formulario, CAMPOS)
        self.form.marco.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        self.btn_guardar = btn_primary(
            self.form.marco, self.ctrl.texto_boton_guardar, self.guardar, width=240, icon="💾"
        )
        self.btn_guardar.pack(padx=20, pady=(14, 6))
        btn_danger(self.form.marco, "Cancelar edición", self.cancelar, width=240, icon="✖").pack(
            padx=20, pady=(0, 6)
        )
        btn_danger(self.form.marco, "Eliminar", self.eliminar, width=240, icon="🗑").pack(
            padx=20, pady=(0, 20)
        )

        derecha = ctk.CTkFrame(body, fg_color="transparent")
        derecha.grid(row=0, column=1, sticky="nsew")
        derecha.grid_rowconfigure(1, weight=1)
        derecha.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(derecha, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        btn_primary(barra, "Actualizar Lista", self.refrescar, width=180, icon="🔄").pack(side="left")

        self.tabla = TablaCRUD(derecha, COLUMNAS, al_seleccionar=self.seleccionar)
        self.tabla.marco.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

    # ── Acciones ─────────────────────────────────────────────────────────────
    def _cargar_categorias(self) -> None:
        r = self.ctrl.cargar_categorias()
        self.form.set_opciones("categoria", r.datos)
        if not r.exito:
            show_error(r.mensaje)

    def refrescar(self) -> None:
        r = self.ctrl.listar(CAMPOS_TABLA)
        if r.exito:
            self.tabla.cargar(r.datos)
        else:
            self.tabla.cargar([])
            show_error(r.mensaje)

    def guardar(self) -> None:
        r = self.ctrl.guardar(self.form.valores())
        if r.exito:
            show_success(r.mensaje)
            self.form.limpiar()
            self._sincronizar_modo()
            self.refrescar()
        else:
            self.form.mostrar_errores(r.errores)
            show_error(r.mensaje)

    def seleccionar(self, id_producto: int) -> None:
        r = self.ctrl.iniciar_edicion(id_producto)
        if r.exito:
            self.form.llenar(r.datos)
            self._sincronizar_modo()
        else:
            show_error(r.mensaje)

    def cancelar(self) -> None:
        self.ctrl.cancelar_edicion()
        self.form.limpiar()
        self._sincronizar_modo()

    def eliminar(self) -> None:
        id_producto = self.tabla.id_seleccionado()
        if id_producto is not None and not confirm_delete(f'"{self.tabla.valor_seleccionado(1)}"'):
            return
        r = self.ctrl.eliminar(id_producto)
        if r.exito:
            show_success(r.mensaje)
            self.form.limpiar()
            self._sincronizar_modo()
            self.refrescar()
        else:
            show_error(r.mensaje)

    def _sincronizar_modo(self) -> None:
        self.btn_guardar.configure(text=f"💾 {self.ctrl.texto_boton_guardar}")
        self.form.set_titulo(self.ctrl.titulo_formulario)

    def _volver(self) -> None:
        from interfaces.menu_principal import construir_menu

        construir_menu(self.contenedor)
