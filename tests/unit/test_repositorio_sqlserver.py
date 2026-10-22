"""Pruebas del repositorio SQL usando una conexión falsa."""

import unittest
from decimal import Decimal

from inventario.comun.errores import (
    ErrorConexion,
    ErrorNoEncontrado,
    ErrorPersistencia,
    ProductoEnUsoError,
)
from inventario.config import ConfiguracionBD
from inventario.dominio.producto import Producto
from inventario.repositorios.sqlserver.categoria_repositorio import CategoriaRepositorioSQL
from inventario.repositorios.sqlserver.conexion import GestorConexion
from inventario.repositorios.sqlserver.producto_repositorio import ProductoRepositorioSQL
from tests.fakes import ConexionFalsa, CursorFalso, ErrorPyodbcFalso, IntegrityError

FILA = (1, "Limpiavidrios", None, Decimal("8000.00"), 30, 1, "Hogar")


def repo_con(cursor):
    conexion = ConexionFalsa(cursor)
    gestor = GestorConexion(ConfiguracionBD(), conectar=lambda _cfg: conexion)
    return ProductoRepositorioSQL(gestor), conexion


class TestGestorConexion(unittest.TestCase):
    def test_commit_y_cierre_cuando_todo_sale_bien(self):
        repo, con = repo_con(CursorFalso(resultados=[FILA]))
        productos = repo.listar()
        self.assertEqual(productos[0].nombre_categoria, "Hogar")
        self.assertEqual((con.commits, con.rollbacks, con.cerrada), (1, 0, True))

    def test_rollback_y_cierre_cuando_falla(self):
        cursor = CursorFalso(error=ErrorPyodbcFalso("42S02", "Invalid object name"))
        repo, con = repo_con(cursor)
        with self.assertLogs("inventario", level="ERROR"), self.assertRaises(ErrorPersistencia):
            repo.listar()
        self.assertEqual((con.commits, con.rollbacks, con.cerrada, cursor.cerrado), (0, 1, True, True))

    def test_no_poder_conectar_es_error_de_conexion(self):
        def conectar(_cfg):
            raise ErrorPyodbcFalso("08001", "TCP Provider: timeout")

        repo = ProductoRepositorioSQL(GestorConexion(ConfiguracionBD(), conectar=conectar))
        with self.assertLogs("inventario", level="ERROR"), self.assertRaises(ErrorConexion):
            repo.listar()


class TestProductoRepositorioSQL(unittest.TestCase):
    def test_agregar_usa_output_inserted_y_devuelve_id(self):
        cursor = CursorFalso(resultados=[(42,)])
        repo, _ = repo_con(cursor)
        p = repo.agregar(Producto("Jabón", Decimal("100"), 1, 1))
        self.assertEqual(p.id, 42)
        self.assertIn("OUTPUT INSERTED.id_producto", cursor.ejecutados[0][0])

    def test_actualizar_inexistente(self):
        repo, _ = repo_con(CursorFalso(rowcount=0))
        with self.assertRaises(ErrorNoEncontrado):
            repo.actualizar(Producto("Jabón", Decimal("100"), 1, 1, id=5))

    def test_violacion_de_llave_foranea_es_producto_en_uso(self):
        cursor = CursorFalso(error=IntegrityError("23000", "REFERENCE constraint FK_Detalle"))
        repo, con = repo_con(cursor)
        with self.assertLogs("inventario", level="ERROR"), self.assertRaises(ProductoEnUsoError):
            repo.eliminar(1)
        self.assertEqual(con.rollbacks, 1)

    def test_esta_en_pedidos_y_categorias(self):
        repo, _ = repo_con(CursorFalso(resultados=[(2,)]))
        self.assertTrue(repo.esta_en_pedidos(1))
        con = ConexionFalsa(CursorFalso(resultados=[(1, "Hogar")]))
        cats = CategoriaRepositorioSQL(GestorConexion(ConfiguracionBD(), conectar=lambda _c: con))
        self.assertEqual(cats.listar()[0].nombre, "Hogar")


class TestConfiguracion(unittest.TestCase):
    def test_cadena_con_autenticacion_windows_y_sql(self):
        self.assertIn("Trusted_Connection=yes", ConfiguracionBD().cadena_conexion())
        cadena = ConfiguracionBD(usuario="sa", clave="x").cadena_conexion()
        self.assertIn("UID=sa", cadena)
        self.assertNotIn("Trusted_Connection", cadena)


if __name__ == "__main__":
    unittest.main()
