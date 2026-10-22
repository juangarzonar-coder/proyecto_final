"""Acceso a la tabla Categoria en SQL Server."""

from __future__ import annotations

from inventario.dominio.categoria import Categoria
from inventario.repositorios.sqlserver.conexion import GestorConexion


class CategoriaRepositorioSQL:
    def __init__(self, gestor: GestorConexion) -> None:
        self._gestor = gestor

    def listar(self) -> list[Categoria]:
        with self._gestor.cursor("listar categorías") as cur:
            cur.execute(
                "SELECT id_categoria, Nombre_categoria FROM Categoria ORDER BY Nombre_categoria"
            )
            return [Categoria(int(f[0]), f[1]) for f in cur.fetchall()]

    def existe(self, id_categoria: int) -> bool:
        with self._gestor.cursor("verificar categoría") as cur:
            cur.execute("SELECT COUNT(*) FROM Categoria WHERE id_categoria = ?", (id_categoria,))
            return int(cur.fetchone()[0]) > 0
