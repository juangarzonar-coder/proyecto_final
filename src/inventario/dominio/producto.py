"""Entidad Producto."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any, Mapping

from inventario.dominio import validaciones as v

NOMBRE_MAX = 100
DESCRIPCION_MAX = 255


@dataclass(frozen=True)
class Producto:
    nombre: str
    precio: Decimal
    stock: int
    id_categoria: int
    descripcion: str = ""
    id: int | None = None
    nombre_categoria: str | None = None  # viene del JOIN con Categoria

    def __post_init__(self) -> None:
        # Valida y normaliza los datos al crear el objeto.
        datos = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "stock": self.stock,
            "id_categoria": self.id_categoria,
        }
        normalizados = _validar(datos)
        for campo, valor in normalizados.items():
            object.__setattr__(self, campo, valor)

    @classmethod
    def desde_datos(cls, datos: Mapping[str, Any], *, id: int | None = None) -> "Producto":
        """Crea un Producto a partir de los textos del formulario."""
        normalizados = _validar(datos)
        return cls(id=id, **normalizados)

    def con_id(self, nuevo_id: int) -> "Producto":
        return replace(self, id=nuevo_id)

    def con_categoria(self, nombre_categoria: str | None) -> "Producto":
        return replace(self, nombre_categoria=nombre_categoria)


def _validar(datos: Mapping[str, Any]) -> dict[str, Any]:
    c = v.ColectorErrores()
    resultado = {
        "nombre": c.validar("nombre", v.texto_requerido, datos.get("nombre"), maximo=NOMBRE_MAX),
        "descripcion": c.validar(
            "descripcion", v.texto_opcional, datos.get("descripcion"), maximo=DESCRIPCION_MAX
        ),
        "precio": c.validar("precio", v.decimal_positivo, datos.get("precio")),
        "stock": c.validar("stock", v.entero_no_negativo, datos.get("stock")),
        "id_categoria": c.validar("id_categoria", v.id_requerido, datos.get("id_categoria")),
    }
    c.lanzar_si_hay_errores()
    return resultado
