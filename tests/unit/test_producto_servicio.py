"""Pruebas del servicio de productos con repositorios en memoria."""

import unittest

from inventario.comun.errores import ErrorNoEncontrado, ErrorValidacion, ProductoEnUsoError
from inventario.repositorios.interfaces import CategoriaRepositorio, ProductoRepositorio
from tests.fakes import DATOS_VALIDOS, crear_servicio


class TestProductoServicio(unittest.TestCase):
    def setUp(self):
        self.servicio, self.repo = crear_servicio(en_pedidos=(1,))

    def test_repositorios_memoria_cumplen_el_contrato(self):
        self.assertIsInstance(self.repo, ProductoRepositorio)
        self.assertIsInstance(self.repo._categorias, CategoriaRepositorio)

    def test_listar_incluye_nombre_de_categoria(self):
        productos = self.servicio.listar()
        self.assertEqual(len(productos), 2)
        self.assertEqual(productos[0].nombre_categoria, "Hogar")

    def test_crear_asigna_id_y_persiste(self):
        creado = self.servicio.crear(DATOS_VALIDOS)
        self.assertEqual(creado.id, 3)
        self.assertEqual(len(self.servicio.listar()), 3)

    def test_crear_con_datos_invalidos_no_persiste(self):
        with self.assertRaises(ErrorValidacion):
            self.servicio.crear(dict(DATOS_VALIDOS, precio="0"))
        self.assertEqual(len(self.servicio.listar()), 2)

    def test_crear_con_categoria_inexistente(self):
        with self.assertRaises(ErrorValidacion) as ctx:
            self.servicio.crear(dict(DATOS_VALIDOS, id_categoria=99))
        self.assertIn("id_categoria", ctx.exception.errores)

    def test_actualizar_modifica_el_producto(self):
        self.servicio.actualizar(2, dict(DATOS_VALIDOS, nombre="Cera premium", id_categoria=2))
        self.assertEqual(self.servicio.obtener(2).nombre, "Cera premium")

    def test_actualizar_inexistente(self):
        with self.assertRaises(ErrorNoEncontrado):
            self.servicio.actualizar(50, DATOS_VALIDOS)

    def test_eliminar_producto_libre(self):
        self.servicio.eliminar(2)
        with self.assertRaises(ErrorNoEncontrado):
            self.servicio.obtener(2)

    def test_eliminar_producto_en_pedido_se_bloquea(self):
        with self.assertRaises(ProductoEnUsoError):
            self.servicio.eliminar(1)
        self.assertIsNotNone(self.servicio.obtener(1))

    def test_eliminar_inexistente(self):
        with self.assertRaises(ErrorNoEncontrado):
            self.servicio.eliminar(77)


if __name__ == "__main__":
    unittest.main()
