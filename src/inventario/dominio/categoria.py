"""Entidad Categoria."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Categoria:
    id: int
    nombre: str
