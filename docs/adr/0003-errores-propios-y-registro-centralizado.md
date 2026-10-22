# ADR-0003: Errores propios, manejo centralizado y registro de eventos

- **Estado:** Aceptada · Implementada en el módulo Productos
- **Fecha:** 2026-10-20
- **Problema que resuelve:** **P4 – El manejo de errores no es uniforme** (Semana 3)
- **Atributo de calidad:** **Confiabilidad** (Escenario 3), y Mantenibilidad en el diagnóstico

## Contexto

El sistema original tiene **19 bloques `except Exception`**: 2 en `productos.py`, 2 en
cada módulo CRUD de interfaz, 5 en `financiero.py` y otros. El patrón típico era:

```python
except Exception as ex:
    show_error(f"Error al guardar: {ex}")
```

Esto produce tres problemas:

1. **No se distingue el origen.** Un error de red, una clave duplicada o un error de programación muestran el mismo tipo de mensaje.
2. **Se muestran textos técnicos al usuario.** Por ejemplo: `('23000', '[23000] [Microsoft][ODBC Driver 17 for SQL Server]... REFERENCE constraint...')`.
3. **No queda registro.** Cuando el usuario cierra el aviso, el detalle se pierde.

Además, `financiero.py` reemplaza los datos por `0, 0, 0` cuando falla la consulta,
y presenta como válido un resultado que no lo es.

## Decisión

1. **Jerarquía de errores propia** (`comun/errores.py`):
   ```
   ErrorAplicacion
   ├── ErrorValidacion        (errores por campo: {campo: mensaje})
   ├── ErrorNoEncontrado
   ├── ErrorReglaNegocio
   │   └── ProductoEnUsoError
   └── ErrorPersistencia
       └── ErrorConexion
   ```
   Cada clase trae un `mensaje_usuario` amigable. El detalle técnico se guarda aparte, en `mensaje` y `causa`.
2. **Traducción en la frontera con la base de datos** (`GestorConexion`): se usa el SQLSTATE de pyodbc.
   - `08xxx` / `HYT00` → `ErrorConexion`
   - `23000` → `ErrorIntegridad` (la FK de `DetallePedido` → `ProductoEnUsoError`)
   - Cualquier otro → `ErrorPersistencia`
3. **Un único punto que convierte errores en mensajes**: `ejecutar_accion()` en `presentacion/controladores/manejo_errores.py`. Registra cada fallo con el nivel adecuado y devuelve un `Resultado`.
   - Validación → `INFO`
   - Regla de negocio → `WARNING`
   - Base de datos → `ERROR`
   - Error de programación → `ERROR` con traza completa

   La excepción no llega a Tkinter, así que la ventana sigue respondiendo.
4. **Regla de negocio explícita**: antes de borrar, `ProductoServicio.eliminar()` consulta `esta_en_pedidos()`. Si otro usuario agrega el producto a un pedido justo en ese momento, la FK de la base de datos sigue protegiendo los datos y el error se traduce igual.
5. **Registro centralizado** (`comun/registro.py`): `logs/app.log` con rotación (3 archivos × 1 MB), configurado una sola vez en `main.py`.
6. **No se ocultan fallos con valores falsos**: si no se pueden cargar las categorías, el desplegable muestra `(no disponible)` y un aviso, en lugar de una lista vacía como si no hubiera categorías. El mismo criterio se aplicará al panel financiero cuando se migre.

Solo quedan 3 `except Exception` en el código nuevo, todos registrados y comentados:
dos en la frontera con pyodbc (la librería no tiene una jerarquía confiable) y uno como
última barrera de la interfaz.

## Código afectado

| Antes | Después |
|-------|---------|
| `interfaces/productos.py` líneas 105-108 y 121-122 (`except Exception`) | `presentacion/controladores/manejo_errores.py` |
| Errores de pyodbc sin traducir | `repositorios/sqlserver/conexion.py` → `traducir_error_bd()` |
| Sin registro | `comun/registro.py`, `main.py` → `configurar_registro()` |
| — | `comun/errores.py` |

## Consecuencias

**Positivas**
- El usuario recibe mensajes claros y el equipo de soporte tiene el detalle en `logs/app.log`.
- Cada tipo de error se puede tratar distinto; por ejemplo, marcar en rojo solo el campo inválido.
- Las pruebas verifican tanto el mensaje mostrado como lo que queda registrado.

**Negativas o costos**
- Quien agregue un caso nuevo debe elegir la clase de error correcta.
- El archivo de log puede contener nombres de productos; no contiene contraseñas, porque la cadena de conexión nunca se registra.

## Verificación (Escenario 3)

| Medida del escenario | Cómo se comprueba | Resultado |
|----------------------|-------------------|-----------|
| El borrado se bloquea y la información no se daña | `test_escenario3_borrar_producto_en_pedido`, `test_violacion_de_llave_foranea_es_producto_en_uso` | ✔ El producto sigue existiendo y se hace rollback |
| 100 % de los fallos queda en un registro interno | Todas las rutas de `ejecutar_accion` escriben en el log; `test_los_fallos_quedan_escritos_en_el_archivo` lee `app.log` | ✔ |
| No se muestran mensajes con código técnico | `test_falla_de_conexion_se_registra_y_no_muestra_texto_tecnico` | ✔ "ODBC" no aparece en el mensaje |
| La aplicación no se traba | `test_error_de_programacion_no_tumba_la_app` | ✔ Devuelve `Resultado`, no lanza excepción |
| La pantalla responde en menos de 2 s | La verificación previa es 1 consulta `COUNT(*)` indexada por FK. Se medirá con SQL Server real en la Semana 14 | ⏳ Pendiente de medir con BD real |
