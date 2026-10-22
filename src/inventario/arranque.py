"""Crea el servicio y el controlador de productos con los repositorios que correspondan."""

from __future__ import annotations

from inventario.config import ConfiguracionBD, modo_repositorio
from inventario.presentacion.controladores.productos_controlador import ProductosControlador
from inventario.servicios.producto_servicio import ProductoServicio

_servicio_demo: ProductoServicio | None = None


def crear_servicio_productos(modo: str | None = None) -> ProductoServicio:
    global _servicio_demo
    modo = modo or modo_repositorio()
    if modo == "memoria":
        # Se reutiliza para no perder los datos al volver a abrir la pantalla.
        if _servicio_demo is None:
            from inventario.repositorios.memoria import datos_demo

            productos, categorias = datos_demo()
            _servicio_demo = ProductoServicio(productos, categorias)
        return _servicio_demo

    from inventario.repositorios.sqlserver.categoria_repositorio import CategoriaRepositorioSQL
    from inventario.repositorios.sqlserver.conexion import GestorConexion
    from inventario.repositorios.sqlserver.producto_repositorio import ProductoRepositorioSQL

    gestor = GestorConexion(ConfiguracionBD.desde_entorno())
    return ProductoServicio(ProductoRepositorioSQL(gestor), CategoriaRepositorioSQL(gestor))


def crear_controlador_productos(modo: str | None = None) -> ProductosControlador:
    return ProductosControlador(crear_servicio_productos(modo))
