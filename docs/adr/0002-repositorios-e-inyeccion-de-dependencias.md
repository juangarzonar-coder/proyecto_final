# ADR-0002: Patrón Repositorio con inyección de dependencias

- **Estado:** Aceptada · Implementada en el módulo Productos
- **Fecha:** 2026-10-20
- **Problema que resuelve:** **P2 – La interfaz depende directamente de la base de datos** (Semana 3)
- **Atributos de calidad:** **Testabilidad** (Escenario 2) y Modificabilidad

## Contexto

`interfaces/productos.py` importaba directamente `insertar_producto`, `mostrar_productos`,
`eliminar_producto` y `actualizar_producto` de `crud/crud_productos.py`. Cada una de
esas funciones:

- llamaba internamente a `conectar()`, con la cadena de conexión escrita a mano en `conexion.py`,
- repetía `con.cursor()` / `commit()` / `close()`,
- devolvía tuplas sin estructura,
- si fallaba a mitad de camino, **no cerraba la conexión ni hacía rollback**.

Probar cualquier cosa exigía una instancia real de SQL Server.

## Decisión

1. **Contratos** (`repositorios/interfaces.py`): `ProductoRepositorio` y
   `CategoriaRepositorio` se definen como `typing.Protocol`. Son las únicas
   abstracciones que conoce la capa de servicios.
2. **Dos implementaciones**:
   - `ProductoRepositorioSQL`: mismas consultas que el sistema original, ahora parametrizadas y devolviendo objetos `Producto`. El `INSERT` usa `OUTPUT INSERTED.id_producto` en vez de `@@IDENTITY`.
   - `ProductoRepositorioMemoria`: diccionarios en memoria. Sirve para las pruebas y para un **modo demo** (`INVENTARIO_REPO=memoria`) que permite abrir la aplicación sin SQL Server.
3. **`GestorConexion`** (`repositorios/sqlserver/conexion.py`): *context manager* que abre la conexión, hace `commit` o `rollback`, cierra siempre y traduce errores de pyodbc (ver ADR-0003). La función de conexión se puede inyectar, así que se prueba con una conexión falsa.
4. **Inyección de dependencias por constructor**: `ProductoServicio(productos, categorias)`. Las implementaciones se eligen en un solo lugar, la raíz de composición `arranque.py`.
5. **Configuración por variables de entorno** (`config.py`): `INVENTARIO_DB_SERVER`, `INVENTARIO_DB_NAME`, etc. `conexion.py` (heredado) también la usa, de modo que todo el sistema apunta a la misma base de datos.

## Código afectado

| Antes | Después |
|-------|---------|
| `crud/crud_productos.py` (usado por la interfaz de Productos) | `repositorios/sqlserver/producto_repositorio.py` |
| `crud/crud_categorias.mostrar_categorias()` (desde Productos) | `repositorios/sqlserver/categoria_repositorio.py` |
| `conectar()` + `commit/close` repetidos en cada función | `repositorios/sqlserver/conexion.py` → `GestorConexion.cursor()` |
| Cadena de conexión fija en `conexion.py` | `config.py` (`ConfiguracionBD.desde_entorno()`) |
| — | `repositorios/interfaces.py`, `repositorios/memoria.py`, `arranque.py` |

`crud/crud_productos.py` **se conserva** porque `interfaces/pedidos.py` todavía usa
`mostrar_productos()`. Se retirará al migrar Pedidos.

## Consecuencias

**Positivas**
- Servicios y controladores se prueban con repositorios en memoria: 47 pruebas en ~0,1 s.
- Cambiar de motor de base de datos o de forma de acceso solo afecta a `repositorios/` y `arranque.py`.
- Las conexiones siempre se cierran y los errores hacen rollback.
- El modo demo permite que cualquier integrante muestre la aplicación sin instalar SQL Server.

**Negativas o costos**
- El repositorio en memoria debe comportarse igual que el real; por ejemplo, simula la llave foránea con `productos_en_pedidos`. Si difieren, las pruebas podrían pasar y la aplicación fallar. Para reducir ese riesgo se agregarán pruebas de integración contra SQL Server en la Semana 14.
- Abrir una conexión por operación es más lento que reutilizarla. Para el volumen de datos del negocio no se nota; si hiciera falta, se agregaría un *pool* dentro de `GestorConexion`.

## Verificación

- `tests/unit/test_producto_servicio.py`: servicio con repositorios en memoria.
- `tests/unit/test_repositorio_sqlserver.py`: repositorio SQL con conexión falsa (commit, rollback, cierre, `OUTPUT INSERTED`, filas no encontradas).
- Cobertura medida: 93 % del código del módulo sin base de datos activa (Escenario 2).
