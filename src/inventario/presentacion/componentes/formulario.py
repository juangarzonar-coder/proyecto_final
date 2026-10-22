"""Formulario genérico para las pantallas de registro."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import customtkinter as ctk

from interfaces.estilos import (
    COLORS,
    FONTS,
    field_label,
    styled_entry,
    styled_frame,
    styled_optionmenu,
)


@dataclass(frozen=True)
class Campo:
    clave: str
    etiqueta: str
    placeholder: str = ""
    tipo: str = "texto"  # "texto" | "opciones"


class FormularioCRUD:
    ANCHO = 240

    def __init__(self, padre, titulo: str, campos: Sequence[Campo]) -> None:
        self.marco = styled_frame(padre)
        self.marco.configure(width=300)

        self._titulo = ctk.CTkLabel(
            self.marco, text=titulo, font=FONTS["subtitle"], text_color=COLORS["accent"]
        )
        self._titulo.pack(pady=(20, 14), padx=20)

        self._campos = list(campos)
        self._entradas: dict[str, ctk.CTkEntry] = {}
        self._opciones: dict[str, tuple[ctk.CTkOptionMenu, ctk.StringVar]] = {}
        self._avisos: dict[str, ctk.CTkLabel] = {}

        for campo in self._campos:
            field_label(self.marco, campo.etiqueta).pack(anchor="w", padx=20, pady=(8, 2))
            if campo.tipo == "opciones":
                var = ctk.StringVar(value="")
                menu = styled_optionmenu(self.marco, values=[""], variable=var, width=self.ANCHO)
                menu.pack(padx=20)
                self._opciones[campo.clave] = (menu, var)
            else:
                entrada = styled_entry(self.marco, placeholder=campo.placeholder, width=self.ANCHO)
                entrada.pack(padx=20)
                self._entradas[campo.clave] = entrada
            aviso = ctk.CTkLabel(
                self.marco, text="", font=FONTS["small"], text_color=COLORS["danger"], anchor="w"
            )
            aviso.pack(anchor="w", padx=20)
            self._avisos[campo.clave] = aviso

    # ── API pública ──────────────────────────────────────────────────────────
    def set_titulo(self, texto: str) -> None:
        self._titulo.configure(text=texto)

    def set_opciones(self, clave: str, valores: Sequence[str]) -> None:
        menu, var = self._opciones[clave]
        valores = list(valores) or [""]
        menu.configure(values=valores)
        var.set(valores[0])

    def valores(self) -> dict[str, str]:
        datos = {k: e.get().strip() for k, e in self._entradas.items()}
        datos.update({k: var.get() for k, (_, var) in self._opciones.items()})
        return datos

    def llenar(self, valores: Mapping[str, str]) -> None:
        self.limpiar_errores()
        for clave, entrada in self._entradas.items():
            entrada.delete(0, "end")
            if valores.get(clave):
                entrada.insert(0, str(valores[clave]))
        for clave, (menu, var) in self._opciones.items():
            if valores.get(clave) in menu.cget("values"):
                var.set(valores[clave])

    def limpiar(self) -> None:
        for entrada in self._entradas.values():
            entrada.delete(0, "end")
        self.limpiar_errores()

    def mostrar_errores(self, errores: Mapping[str, str]) -> None:
        self.limpiar_errores()
        for clave, mensaje in errores.items():
            if clave in self._avisos:
                self._avisos[clave].configure(text=mensaje)
            if clave in self._entradas:
                self._entradas[clave].configure(border_color=COLORS["danger"])

    def limpiar_errores(self) -> None:
        for aviso in self._avisos.values():
            aviso.configure(text="")
        for entrada in self._entradas.values():
            entrada.configure(border_color=COLORS["border"])
