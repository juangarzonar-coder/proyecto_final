"""Pruebas de las validaciones y de la entidad Producto."""

import unittest
from decimal import Decimal

from inventario.comun.errores import ErrorValidacion
from inventario.dominio import validaciones as v
from inventario.dominio.producto import NOMBRE_MAX, Producto
from tests.fakes import DATOS_VALIDOS


class TestValidaciones(unittest.TestCase):
    def test_texto_requerido_recorta_espacios(self):
        self.assertEqual(v.texto_requerido("  Jabón  "), "Jabón")

    def test_texto_requerido_rechaza_vacio(self):
        for valor in ("", "   ", None):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                v.texto_requerido(valor)

    def test_texto_respeta_longitud_maxima(self):
        with self.assertRaisesRegex(ValueError, "Máximo 5"):
            v.texto_opcional("abcdef", maximo=5)

    def test_decimal_positivo_acepta_coma_y_redondea(self):
        self.assertEqual(v.decimal_positivo("12,5"), Decimal("12.50"))

    def test_decimal_positivo_rechaza_cero_negativo_y_texto(self):
        for valor in ("0", "-3", "abc", "", "nan", "inf"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                v.decimal_positivo(valor)

    def test_entero_no_negativo(self):
        self.assertEqual(v.entero_no_negativo("0"), 0)
        self.assertEqual(v.entero_no_negativo(7), 7)
        for valor in ("-1", "2.5", "", True, None):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                v.entero_no_negativo(valor)

    def test_id_requerido(self):
        self.assertEqual(v.id_requerido("3"), 3)
        for valor in (None, "", "x", 0, -2):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                v.id_requerido(valor)


class TestProducto(unittest.TestCase):
    def test_crea_producto_valido_desde_textos(self):
        p = Producto.desde_datos(DATOS_VALIDOS)
        self.assertEqual(p.nombre, "Jabón industrial")
        self.assertEqual(p.precio, Decimal("15000.00"))
        self.assertEqual(p.stock, 10)
        self.assertIsNone(p.id)

    def test_reporta_todos_los_campos_invalidos_a_la_vez(self):
        datos = {"nombre": "", "precio": "0", "stock": "-1", "id_categoria": None}
        with self.assertRaises(ErrorValidacion) as ctx:
            Producto.desde_datos(datos)
        self.assertEqual(set(ctx.exception.errores), {"nombre", "precio", "stock", "id_categoria"})

    def test_nombre_demasiado_largo(self):
        datos = dict(DATOS_VALIDOS, nombre="x" * (NOMBRE_MAX + 1))
        with self.assertRaises(ErrorValidacion) as ctx:
            Producto.desde_datos(datos)
        self.assertIn("nombre", ctx.exception.errores)

    def test_no_se_puede_construir_invalido_directamente(self):
        with self.assertRaises(ErrorValidacion):
            Producto(nombre="Jabón", precio=Decimal("-5"), stock=1, id_categoria=1)

    def test_es_inmutable_y_con_id_devuelve_copia(self):
        p = Producto.desde_datos(DATOS_VALIDOS)
        p2 = p.con_id(9)
        self.assertIsNone(p.id)
        self.assertEqual(p2.id, 9)
        with self.assertRaises(Exception):
            p.nombre = "otro"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
