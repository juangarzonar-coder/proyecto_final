"""Pruebas del log, la configuración y el arranque."""

import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from inventario import arranque
from inventario.comun.registro import configurar_registro, obtener_logger
from inventario.config import ConfiguracionBD, modo_repositorio
from inventario.presentacion.controladores.productos_controlador import ProductosControlador


class TestRegistro(unittest.TestCase):
    def test_los_fallos_quedan_escritos_en_el_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "logs" / "app.log"
            raiz = configurar_registro(ruta)
            configurar_registro(ruta)  # la segunda llamada no debe duplicar el handler
            try:
                ctrl = arranque.crear_controlador_productos("memoria")
                ctrl.eliminar(1)  # el producto 1 está en un pedido
                for h in raiz.handlers:
                    h.flush()
                contenido = ruta.read_text(encoding="utf-8")
            finally:
                for h in list(raiz.handlers):
                    if not isinstance(h, logging.NullHandler):
                        raiz.removeHandler(h)
                        h.close()
        self.assertIn("ProductoEnUsoError", contenido)
        self.assertIn("WARNING", contenido)

    def test_nombres_de_logger(self):
        self.assertEqual(obtener_logger("servicios").name, "inventario.servicios")
        self.assertEqual(obtener_logger("inventario.x").name, "inventario.x")


class TestConfiguracionEntorno(unittest.TestCase):
    def test_lee_variables_de_entorno(self):
        entorno = {
            "INVENTARIO_DB_SERVER": "srv01",
            "INVENTARIO_DB_NAME": "Pruebas",
            "INVENTARIO_DB_TIMEOUT": "2",
            "INVENTARIO_REPO": "Memoria",
        }
        with mock.patch.dict(os.environ, entorno):
            cfg = ConfiguracionBD.desde_entorno()
            self.assertEqual(modo_repositorio(), "memoria")
        self.assertEqual((cfg.servidor, cfg.base_datos, cfg.timeout), ("srv01", "Pruebas", 2))
        self.assertIn("SERVER=srv01", cfg.cadena_conexion())


class TestArranque(unittest.TestCase):
    def setUp(self):
        arranque._servicio_demo = None

    def test_modo_memoria_arma_la_cadena_completa(self):
        ctrl = arranque.crear_controlador_productos("memoria")
        self.assertIsInstance(ctrl, ProductosControlador)
        self.assertEqual(len(ctrl.listar().datos), 3)
        self.assertIs(arranque.crear_servicio_productos("memoria"), arranque.crear_servicio_productos("memoria"))

    def test_modo_sqlserver_no_conecta_hasta_usarse(self):
        servicio = arranque.crear_servicio_productos("sqlserver")
        self.assertEqual(type(servicio._productos).__name__, "ProductoRepositorioSQL")


if __name__ == "__main__":
    unittest.main()
