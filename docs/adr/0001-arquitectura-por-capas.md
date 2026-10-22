# ADR-0001: Arquitectura por capas con controlador de presentación

- **Estado:** Aceptada · Implementada en el módulo Productos
- **Fecha:** 2026-10-20
- **Problema que resuelve:** **P1 – Las interfaces tienen demasiadas responsabilidades** (Semana 3)
- **Atributos de calidad:** **Mantenibilidad** (Escenario 1) y Testabilidad (Escenario 2)

## Contexto

En `interfaces/productos.py` (150 líneas) toda la lógica vivía dentro de una sola
función, `abrir_productos()`, con **4 funciones anidadas**: `refrescar`, `guardar`,
`eliminar` y `cargar_en_form`. La función `guardar()`:

- leía directamente los `CTkEntry` (`campos["Precio"].get()`),
- convertía tipos (`float(...)`, `int(...)`),
- validaba (`if not nom: show_error(...)`),
- decidía entre insertar o actualizar según un diccionario mutable `id_editando = {"val": None}`,
- llamaba al CRUD y abría ventanas emergentes con el resultado.

No existía una entidad `Producto`: un producto era una tupla de la base de datos o un
conjunto de widgets. Cambiar una regla, como el precio mínimo, obligaba a editar la
pantalla, y no había forma de probarla sin abrir CustomTkinter.

## Decisión

Organizar el código nuevo en el paquete `src/inventario/` con cuatro capas y una
regla de dependencias **en un solo sentido**:

```
presentación ──► servicios ──► dominio ◄── acceso a datos
      │                │                          ▲
      └────────────────┴──── comun (errores, registro, config) ─┘
```

| Capa | Paquete | Responsabilidad | No puede |
|------|---------|-----------------|----------|
| Presentación | `presentacion/` | Vista (widgets) y **controlador** (estado de la pantalla y resultados) | Validar reglas de negocio ni usar SQL |
| Servicios | `servicios/` | Casos de uso: crear, actualizar, eliminar, listar; reglas de negocio | Importar CustomTkinter ni pyodbc |
| Dominio | `dominio/` | Entidades `Producto` y `Categoria`; validaciones puras | Depender de cualquier otra capa |
| Acceso a datos | `repositorios/` | Leer y escribir en SQL Server (ver ADR-0002) | Contener reglas de negocio o interfaz |

Dentro de la presentación se separa la **vista** (`VistaProductos`, que solo arma
widgets) del **controlador** (`ProductosControlador`). El controlador es Python puro:
recibe diccionarios de texto, devuelve un objeto `Resultado` y guarda el estado de
edición. Así la lógica de la pantalla se prueba sin interfaz gráfica.

La entidad `Producto` es un `dataclass` inmutable que **valida en su construcción**,
de modo que nunca existe un producto inválido en memoria. A diferencia del diagrama de
clases de la Entrega 2, **no tiene `insertar()` ni `actualizar()`**: guardarse no es
responsabilidad de la entidad.

## Código afectado

| Antes (código original) | Después |
|-------------------------|---------|
| `interfaces/productos.py` → `guardar()` (validación y conversión) | `dominio/validaciones.py`, `dominio/producto.py` |
| `interfaces/productos.py` → decisión insertar/actualizar, `id_editando` | `presentacion/controladores/productos_controlador.py` |
| Llamadas directas a `crud_productos` desde la interfaz | `servicios/producto_servicio.py` |
| Construcción de widgets | `presentacion/vistas/productos_vista.py` |
| `interfaces/productos.py` | **Eliminado**: `menu_principal.py` ahora carga `inventario.presentacion.vistas.productos_vista` |

## Consecuencias

**Positivas**
- Cada regla se cambia en un solo archivo. Por ejemplo, el precio mínimo está en `dominio/validaciones.py`.
- La lógica de la pantalla (guardar, editar, eliminar) se prueba sin abrir ventanas.
- Agregar un campo toca exactamente 3 archivos (ver Verificación).

**Negativas o costos**
- Hay más archivos que antes: 1 archivo de 150 líneas pasa a ~10 archivos pequeños. Se compensa con nombres claros y con el diagrama de componentes.
- El equipo debe respetar la regla de dependencias; por ahora se revisa en los pull requests.

## Verificación

- **Escenario 1 (agregar SKU):** se hizo la prueba de agregar el campo en una copia del proyecto.
  El cambio modifica **3 archivos** (`dominio/producto.py`, `repositorios/sqlserver/producto_repositorio.py`
  y `presentacion/vistas/productos_vista.py`), 18 líneas, sin tocar el servicio, el
  controlador ni otros módulos. Antes eran 9 puntos en 4 archivos. Todas las pruebas
  siguen pasando con el campo nuevo.
- `tests/unit/test_productos_controlador.py` prueba el flujo de la pantalla sin CustomTkinter.
