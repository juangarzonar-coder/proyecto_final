"""Excepciones propias de la aplicación."""

from __future__ import annotations


class ErrorAplicacion(Exception):
    """Error base. mensaje_usuario es el texto que se muestra en pantalla."""

    mensaje_usuario = "Ocurrió un problema inesperado. Intente de nuevo."

    def __init__(self, mensaje: str | None = None, *, causa: BaseException | None = None):
        super().__init__(mensaje or self.mensaje_usuario)
        self.mensaje = mensaje or self.mensaje_usuario
        self.causa = causa


class ErrorValidacion(ErrorAplicacion):
    """errores es un diccionario {campo: mensaje}."""

    mensaje_usuario = "Revise los datos ingresados."

    def __init__(self, errores: dict[str, str]):
        self.errores = dict(errores)
        detalle = "; ".join(f"{campo}: {msg}" for campo, msg in self.errores.items())
        super().__init__(detalle or self.mensaje_usuario)


class ErrorNoEncontrado(ErrorAplicacion):
    mensaje_usuario = "El registro solicitado no existe o ya fue eliminado."


class ErrorReglaNegocio(ErrorAplicacion):
    mensaje_usuario = "La operación no está permitida por las reglas del negocio."


class ProductoEnUsoError(ErrorReglaNegocio):
    mensaje_usuario = (
        "No se puede eliminar el producto porque está incluido en uno o más pedidos."
    )

    def __init__(self, id_producto: int, *, causa: BaseException | None = None):
        self.id_producto = id_producto
        super().__init__(self.mensaje_usuario, causa=causa)


class ErrorPersistencia(ErrorAplicacion):
    mensaje_usuario = "No se pudo completar la operación en la base de datos."


class ErrorConexion(ErrorPersistencia):
    mensaje_usuario = (
        "No hay conexión con la base de datos. Verifique que el servidor esté disponible."
    )
