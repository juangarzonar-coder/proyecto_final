"""Pruebas del controlador de la pantalla de productos."""

import unittest
from unittest import mock

from inventario.comun.errores import ErrorConexion
from inventario.presentacion.controladores.manejo_errores import MENSAJE_INESPERADO
from inventario.presentacion.controladores.productos_controlador import (
    ProductosControlador,
    SIN_CATEGORIAS,
)
from tests.fakes import crear_servicio

FORM = {"nombre": "Ambientador", "descripcion": "", "precio": "9500", "stock": "4", "categoria": "Hogar"}


class TestProductosControlador(unittest.TestCase):
    def setUp(self):
        self.servicio, self.repo = crear_servicio(en_pedidos=(1,))
        self.ctrl = ProductosControlador(self.servicio)
        self.ctrl.cargar_categorias()

    def test_categorias_y_filas_de_tabla(self):
        self.assertEqual(self.ctrl.cargar_categorias().datos, ["Hogar", "Vehículos"])
        filas = self.ctrl.listar().datos
        self.assertEqual(filas[0], (1, "Limpiavidrios", "", "8,000.00", 30, "Hogar"))

    def test_sin_categorias_muestra_marcador(self):
        self.repo._categorias._datos.clear()
        self.assertEqual(self.ctrl.cargar_categorias().datos, [SIN_CATEGORIAS])

    def test_guardar_nuevo(self):
        r = self.ctrl.guardar(FORM)
        self.assertTrue(r.exito)
        self.assertEqual(len(self.servicio.listar()), 3)

    def test_guardar_invalido_devuelve_errores_por_campo(self):
        r = self.ctrl.guardar(dict(FORM, nombre="", precio="abc", categoria="(no existe)"))
        self.assertFalse(r.exito)
        self.assertEqual(set(r.errores), {"nombre", "precio", "categoria"})

    def test_flujo_de_edicion(self):
        r = self.ctrl.iniciar_edicion(2)
        self.assertTrue(r.exito)
        self.assertEqual(r.datos["categoria"], "Vehículos")
        self.assertEqual(self.ctrl.texto_boton_guardar, "Actualizar")
        r = self.ctrl.guardar(dict(r.datos, stock="99"))
        self.assertTrue(r.exito)
        self.assertFalse(self.ctrl.editando)
        self.assertEqual(self.servicio.obtener(2).stock, 99)

    def test_cancelar_edicion(self):
        self.ctrl.iniciar_edicion(2)
        self.ctrl.cancelar_edicion()
        self.assertEqual(self.ctrl.titulo_formulario, "Nuevo Producto")

    def test_eliminar_sin_seleccion(self):
        self.assertFalse(self.ctrl.eliminar(None).exito)

    def test_eliminar_producto_libre_sale_del_modo_edicion(self):
        self.ctrl.iniciar_edicion(2)
        self.assertTrue(self.ctrl.eliminar(2).exito)
        self.assertFalse(self.ctrl.editando)

    def test_borrar_producto_en_pedido_se_bloquea(self):
        with self.assertLogs("inventario", level="WARNING") as registro:
            r = self.ctrl.eliminar(1)
        self.assertFalse(r.exito)
        self.assertIn("pedidos", r.mensaje)
        self.assertTrue(any("ProductoEnUsoError" in linea for linea in registro.output))
        self.assertIsNotNone(self.servicio.obtener(1))

    def test_falla_de_conexion_se_registra_y_no_muestra_texto_tecnico(self):
        detalle_tecnico = "[08001] [Microsoft][ODBC Driver 17] TCP Provider: timeout"
        with mock.patch.object(
            self.servicio, "listar", side_effect=ErrorConexion(detalle_tecnico)
        ), self.assertLogs("inventario", level="ERROR") as registro:
            r = self.ctrl.listar()
        self.assertFalse(r.exito)
        self.assertNotIn("ODBC", r.mensaje)
        self.assertTrue(any("08001" in linea for linea in registro.output))

    def test_error_de_programacion_no_tumba_la_app(self):
        with mock.patch.object(
            self.servicio, "eliminar", side_effect=AttributeError("bug")
        ), self.assertLogs("inventario", level="ERROR") as registro:
            r = self.ctrl.eliminar(2)
        self.assertEqual(r.mensaje, MENSAJE_INESPERADO)
        self.assertIn("Traceback", "\n".join(registro.output))

    def test_categorias_no_disponibles_no_finge_lista_vacia(self):
        with mock.patch.object(
            self.servicio, "listar_categorias", side_effect=ErrorConexion("sin red")
        ), self.assertLogs("inventario", level="ERROR"):
            r = self.ctrl.cargar_categorias()
        self.assertFalse(r.exito)
        self.assertEqual(r.datos, ["(no disponible)"])


if __name__ == "__main__":
    unittest.main()
