"""Tabla genérica basada en el Treeview de estilos.py."""

from __future__ import annotations

from typing import Callable, Iterable, Sequence

from interfaces.estilos import fill_table, make_table


class TablaCRUD:
    def __init__(
        self,
        padre,
        columnas: Sequence[dict],
        al_seleccionar: Callable[[int], None] | None = None,
        alto: int = 16,
    ) -> None:
        self.marco, self.arbol = make_table(padre, list(columnas), height=alto)
        if al_seleccionar:
            self.arbol.bind("<ButtonRelease-1>", lambda _e: self._notificar(al_seleccionar))

    def cargar(self, filas: Iterable[Sequence]) -> None:
        fill_table(self.arbol, filas)

    def id_seleccionado(self) -> int | None:
        seleccion = self.arbol.selection()
        if not seleccion:
            return None
        valores = self.arbol.item(seleccion[0])["values"]
        return int(valores[0]) if valores else None

    def valor_seleccionado(self, columna: int) -> str | None:
        seleccion = self.arbol.selection()
        if not seleccion:
            return None
        return str(self.arbol.item(seleccion[0])["values"][columna])

    def _notificar(self, callback: Callable[[int], None]) -> None:
        id_ = self.id_seleccionado()
        if id_ is not None:
            callback(id_)
