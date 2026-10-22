# Arquitectura del Sistema de Gestión EmpresaLimpieza

**Arquitectura de Software · Universidad Católica Luis Amigó · Entrega 3**
Docente: Fernando de Jesús Higuita
Integrantes: Juan Sebastián Garzón · Camilo Londoño · Juan José Henao · José David Bermúdez

> Este documento describe la **arquitectura objetivo** después de la refactorización,
> qué componentes la forman, por qué se tomó cada decisión y qué tanto se ha avanzado.
> Continúa la Entrega 1 (análisis de problemas) y la Entrega 2 (atributos y escenarios).

---

## Contenido

1. [Contexto y módulo MVP](#1-contexto-y-módulo-mvp)
2. [Arquitectura actual y problemas](#2-arquitectura-actual-y-problemas-semana-3)
3. [Arquitectura objetivo](#3-arquitectura-objetivo)
4. [Componentes y responsabilidades](#4-componentes-y-responsabilidades)
5. [Decisiones de refactorización](#5-decisiones-de-refactorización)
6. [Escenarios de calidad actualizados](#6-escenarios-de-calidad-actualizados-semana-8)

---

## 1. Contexto y módulo MVP

El sistema apoya la gestión de una empresa que fabrica y vende productos de limpieza
para hogar y vehículos: productos, materias primas, proveedores, clientes, pedidos e
información financiera. Es una **aplicación de escritorio** en Python con CustomTkinter
y `ttk.Treeview`, gráficas en Matplotlib y datos en **SQL Server**.

**Módulo MVP: Gestión de Productos** (crear, listar, actualizar y eliminar productos).
Lo elegimos porque reúne los cuatro problemas de la Semana 3, es el motor del negocio
(precios y stock alimentan pedidos y finanzas) y otros módulos dependen de él.

| Alcance de la re-arquitectura | Estado |
|-------------------------------|--------|
| **Productos** (MVP) | Migrado a la nueva arquitectura |
| Clientes | Siguiente: comprueba la reutilización de componentes |
| Pedidos | Después: reglas entre entidades |
| Materias Primas, Categorías, Proveedores, Panel Financiero | Fuera del alcance; siguen con la estructura heredada |

## 2. Arquitectura actual y problemas (Semana 3)

```
main.py → menu_principal.py → interfaces/*.py ──(llamada directa)──► crud/*.py → conexion.py → SQL Server
                                   │
                                   └─ valida, convierte tipos, decide insertar/actualizar,
                                      maneja errores y muestra mensajes
```

| # | Problema | Evidencia en el código original | Atributo afectado |
|---|----------|----------------------------------|-------------------|
| P1 | Las interfaces tienen demasiadas responsabilidades | `interfaces/productos.py`: una función de 140 líneas con 4 funciones anidadas. `guardar()` lee widgets, convierte con `float()`/`int()`, valida y llama al CRUD. No hay entidad `Producto`. | Mantenibilidad, Testabilidad |
| P2 | La interfaz depende directamente de la BD | `productos.py` importa 4 funciones de `crud_productos`; cada una abre su propia conexión con una cadena fija. Sin `rollback` ni cierre si algo falla. | Testabilidad, Modificabilidad |
| P3 | Código repetido entre módulos | El mismo bucle de formulario, lectura de selección y llenado se repite en productos, clientes, proveedores, materias y categorías. | Reutilización, Mantenibilidad |
| P4 | Manejo de errores no uniforme | 19 bloques `except Exception`, mensajes con texto técnico de ODBC, sin registro; `financiero.py` reemplaza fallos por `0, 0, 0`. | Confiabilidad |

## 3. Arquitectura objetivo

**Estilo:** arquitectura **por capas** con **repositorios** e **inyección de
dependencias**, más una **migración incremental** (patrón estrangulador) que deja
convivir el código nuevo (`src/inventario/`) con el heredado (`src/interfaces/`,
`src/crud/`) mientras se migra.

**Regla de dependencias:** las flechas solo apuntan hacia abajo o hacia el dominio. El
dominio no depende de nada. Los servicios dependen de *contratos*, no de SQL Server.

```
┌──────────────────── Presentación ────────────────────┐
│ VistaProductos ─► FormularioCRUD / TablaCRUD         │   CustomTkinter
│       └────────► ProductosControlador ─► Resultado   │   (solo aquí)
└───────────────────────────┬──────────────────────────┘
                            ▼
┌───────────────────── Servicios ──────────────────────┐
│ ProductoServicio  (casos de uso + reglas de negocio) │
└──────────┬───────────────────────────────┬───────────┘
           ▼                               ▼ «Protocol»
┌──── Dominio ─────┐          ┌────── Acceso a datos ──────┐
│ Producto         │◄─────────│ ProductoRepositorioSQL     │──► SQL Server
│ Categoria        │          │ ProductoRepositorioMemoria │    (pyodbc)
│ validaciones     │          │ GestorConexion             │
└──────────────────┘          └────────────────────────────┘
        Comunes (todas las capas): errores · registro (logs/app.log) · config
```

### Vistas del sistema (C4, versión 1)

Las fuentes editables están en [`diagramas/fuentes/`](diagramas/fuentes/) (Graphviz
`.dot`) y las versiones exportadas en [`diagramas/exportados/`](diagramas/exportados/)
(SVG y PNG). Se exportan con Graphviz: `dot -Tpng archivo.dot -o archivo.png`.

#### Nivel 1 · Contexto
![Contexto](diagramas/exportados/c4-1-contexto.png)

#### Nivel 2 · Contenedores
En C4 un contenedor es algo que se ejecuta o almacena datos por separado. El sistema
tiene tres: la aplicación de escritorio, la base de datos y el archivo de registro.
Las capas no son contenedores porque corren en el mismo proceso; por eso se muestran
en el nivel 3.

![Contenedores](diagramas/exportados/c4-2-contenedores.png)

#### Nivel 3 · Componentes del módulo MVP (Productos)
![Componentes](diagramas/exportados/c4-3-componentes-productos.png)

#### Despliegue
![Despliegue](diagramas/exportados/despliegue.png)

## 4. Componentes y responsabilidades

Rutas relativas a `src/`. **Reemplaza** indica qué parte del código original absorbe cada componente.

| Componente | Capa | Responsabilidad | Depende de | Archivo / paquete | Reemplaza |
|------------|------|-----------------|------------|-------------------|-----------|
| `main` | Arranque | Crea la ventana raíz, configura el registro y carga el menú | `menu_principal`, `comun.registro` | `main.py` | — (se agrega `configurar_registro()`) |
| Menú principal | Presentación (heredada) | Navegación entre módulos con `importlib` | `estilos`, vistas de cada módulo | `interfaces/menu_principal.py` | — (solo cambia la ruta de Productos) |
| `VistaProductos` | Presentación | Construye la pantalla, envía acciones al controlador y muestra `Resultado` | `FormularioCRUD`, `TablaCRUD`, `ProductosControlador`, `estilos` | `inventario/presentacion/vistas/productos_vista.py` | `interfaces/productos.py` (eliminado) |
| `FormularioCRUD` | Presentación | Formulario declarativo: leer, llenar, limpiar y marcar errores por campo | `estilos`, CustomTkinter | `inventario/presentacion/componentes/formulario.py` | Bucles de campos y `cargar_en_form()` repetidos en 5 módulos |
| `TablaCRUD` | Presentación | Treeview con carga de filas y selección por id | `estilos` (`make_table`, `fill_table`) | `inventario/presentacion/componentes/tabla.py` | Lectura manual de `tree.selection()` |
| `ProductosControlador` | Presentación | Estado de edición; arma los datos del formulario; devuelve `Resultado` sin abrir ventanas | `ProductoServicio`, `ejecutar_accion` | `inventario/presentacion/controladores/productos_controlador.py` | `guardar()`, `eliminar()`, `refrescar()`, `id_editando` |
| `ejecutar_accion` / `Resultado` | Presentación | Único punto que traduce errores en mensajes amigables y los registra | `comun.errores`, `comun.registro` | `inventario/presentacion/controladores/manejo_errores.py`, `resultado.py` | 19 `except Exception` + `show_error(f"...{ex}")` |
| `ProductoServicio` | Servicios | Casos de uso crear/actualizar/eliminar/listar; reglas: categoría existente, no borrar productos en pedidos | Contratos de repositorio, `Producto` | `inventario/servicios/producto_servicio.py` | Coordinación que hacía la interfaz |
| `Producto`, `Categoria` | Dominio | Entidades inmutables que no pueden existir inválidas | `validaciones` | `inventario/dominio/producto.py`, `categoria.py` | Tuplas de `mostrar_productos()` |
| `validaciones` | Dominio | Reglas puras: texto requerido, longitud, precio > 0, stock ≥ 0, id válido; acumula errores por campo | `comun.errores` | `inventario/dominio/validaciones.py` | `if not nom`, `float()`, `int()` en `guardar()` |
| `ProductoRepositorio`, `CategoriaRepositorio` | Acceso a datos | Contratos (`typing.Protocol`) que usa el servicio | `Producto`, `Categoria` | `inventario/repositorios/interfaces.py` | — (nuevo) |
| `ProductoRepositorioSQL`, `CategoriaRepositorioSQL` | Acceso a datos | SQL parametrizado; mapea filas a entidades; FK → `ProductoEnUsoError` | `GestorConexion`, dominio | `inventario/repositorios/sqlserver/` | `crud/crud_productos.py` y `mostrar_categorias()` (para Productos) |
| Repositorios en memoria | Acceso a datos | Implementación para pruebas y modo demo | Dominio | `inventario/repositorios/memoria.py` | — (nuevo) |
| `GestorConexion` | Acceso a datos | Abrir/cerrar, commit/rollback y traducción de SQLSTATE a errores propios | `config`, `comun` | `inventario/repositorios/sqlserver/conexion.py` | `conectar()` + `commit/close` repetidos |
| Errores propios | Comunes | Jerarquía `ErrorAplicacion` con mensaje para el usuario y causa técnica | — | `inventario/comun/errores.py` | — (nuevo) |
| Registro | Comunes | `logging` a `logs/app.log` con rotación | — | `inventario/comun/registro.py` | — (nuevo) |
| Configuración | Comunes | Conexión por variables de entorno; modo `sqlserver`/`memoria` | — | `inventario/config.py` | Cadena fija en `conexion.py` |
| Raíz de composición | Comunes | Único lugar que elige implementaciones y arma la cadena controlador → servicio → repositorios | Todas | `inventario/arranque.py` | — (nuevo) |
| `estilos` | Presentación (heredada) | Paleta, fuentes y widgets base | CustomTkinter | `interfaces/estilos.py` | — (se reutiliza sin cambios) |
| Módulos heredados | Presentación + datos (heredado) | Clientes, Pedidos, Materias, Proveedores, Categorías, Financiero | `crud/*`, `conexion.py` | `interfaces/*.py`, `crud/*.py`, `conexion.py` | Pendientes de migrar por etapas |

## 5. Decisiones de refactorización

Detalle completo en [`docs/adr/`](adr/), un archivo por decisión.

| ADR | Problema (Semana 3) | Cambio propuesto | Código afectado | Atributo que mejora (Semana 8) | Estado |
|-----|---------------------|------------------|-----------------|--------------------------------|--------|
| [0001](adr/0001-arquitectura-por-capas.md) | P1 · Interfaces con demasiadas responsabilidades | Capas presentación/servicios/dominio/datos; controlador separado de la vista; entidad `Producto` | `interfaces/productos.py` → `inventario/presentacion`, `servicios`, `dominio` | **Mantenibilidad** (Esc. 1) | Implementada |
| [0002](adr/0002-repositorios-e-inyeccion-de-dependencias.md) | P2 · Interfaz acoplada a la BD | Repositorios con contrato `Protocol`, implementación SQL y en memoria; inyección por constructor; configuración por entorno | `crud/crud_productos.py`, `conexion.py` → `inventario/repositorios`, `config.py`, `arranque.py` | **Testabilidad** (Esc. 2) | Implementada |
| [0003](adr/0003-errores-propios-y-registro-centralizado.md) | P4 · Manejo de errores no uniforme | Jerarquía de errores propia, traducción por SQLSTATE, punto único de manejo, `logging` a archivo, no ocultar fallos con valores falsos | `except Exception` de `productos.py` → `comun/`, `manejo_errores.py`, `conexion.py` | **Confiabilidad** (Esc. 3) | Implementada |

## 6. Escenarios de calidad actualizados (Semana 8)

Se refinan los escenarios de la Entrega 2 con el formato de seis partes y una medida
**verificable en el repositorio**.

### Escenario 1 · Mantenibilidad: agregar un campo al producto

| Parte | Descripción |
|-------|-------------|
| Fuente | Desarrollador del equipo |
| Estímulo | Se solicita agregar el campo **SKU** (código de referencia) al producto |
| Artefacto | Módulo Productos (dominio, repositorio SQL y vista) |
| Entorno | Tiempo de desarrollo, sobre el código refactorizado |
| Respuesta | El campo se agrega sin modificar el servicio, el controlador ni otros módulos (clientes, pedidos…) |
| Medida | ≤ **3 archivos** de `src/` modificados (antes: 9 puntos en 4 archivos), ≤ 4 horas, 0 archivos de otros módulos, pruebas existentes en verde |

**Verificación:** se agregó el campo en una copia del proyecto: **3 archivos, 18 líneas**
(`dominio/producto.py`, `repositorios/sqlserver/producto_repositorio.py`, `presentacion/vistas/productos_vista.py`) y las 47 pruebas pasan. Además requiere `ALTER TABLE Producto ADD SKU VARCHAR(30) NULL`.
✔ **Cumple**

### Escenario 2 · Testabilidad: probar reglas sin interfaz ni base de datos

| Parte | Descripción |
|-------|-------------|
| Fuente | Desarrollador antes de hacer *commit* |
| Estímulo | Ejecuta las pruebas automáticas del módulo |
| Artefacto | Dominio, servicios, controlador y repositorios de Productos |
| Entorno | Desarrollo, **sin** ventana de CustomTkinter y **sin** SQL Server |
| Respuesta | Las pruebas verifican las reglas (precio > 0, stock ≥ 0, nombre obligatorio, categoría existente, no borrar productos en pedidos) y reportan cualquier falla automáticamente |
| Medida | ≥ **15 pruebas**, ≥ **80 %** de cobertura del módulo (excepto widgets), < **10 s** |

**Verificación:** `python -m unittest discover -s tests -t .` → **47 pruebas en 0,13 s**, con **93 % de cobertura** del módulo (sin contar widgets). ✔ **Cumple**

### Escenario 3 · Confiabilidad: eliminar un producto que está en un pedido

| Parte | Descripción |
|-------|-------------|
| Fuente | Empleado usando la aplicación |
| Estímulo | Intenta eliminar un producto que ya está en un pedido existente |
| Artefacto | Pantalla de Productos, servicio, repositorio y base de datos |
| Entorno | Operación normal |
| Respuesta | Se bloquea el borrado sin dañar la información, el detalle queda en `logs/app.log`, el usuario ve un aviso claro y la aplicación sigue respondiendo |
| Medida | 100 % de los fallos registrados; 0 mensajes con texto técnico (ODBC/SQLSTATE); pantalla disponible en < 2 s |

**Verificación:** 4 pruebas automáticas cubren el bloqueo, el registro en archivo, la
ausencia de texto técnico y la estabilidad (ver [ADR-0003](adr/0003-errores-propios-y-registro-centralizado.md#verificación-escenario-3)).
✔ **Cumple** en pruebas. El tiempo < 2 s se medirá con SQL Server real en la Semana 14.
