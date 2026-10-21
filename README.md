# EmpresaLimpieza · Re-arquitectura del Sistema de Gestión

Proyecto del curso **Arquitectura de Software**, Universidad Católica Luis Amigó (2026).
Docente: Fernando de Jesús Higuita.
**Integrantes:** Juan Sebastián Garzón · Camilo Londoño · Juan José Henao · José David Bermúdez

## Descripción del proyecto

Aplicación de escritorio para una empresa que fabrica y vende **productos de limpieza
para hogar y vehículos**. Gestiona productos, materias primas, proveedores, clientes,
pedidos e información financiera. Está hecha en **Python**, **CustomTkinter**,
`ttk.Treeview`, **Matplotlib** y **SQL Server**.

Este repositorio contiene la refactorización del sistema hacia una **arquitectura por
capas**: presentación → servicios → dominio ← acceso a datos (repositorios).

### Módulo MVP: Gestión de Productos

Crear, listar, editar y eliminar productos. Es el primer módulo migrado a la nueva
arquitectura (`src/inventario/`) y funciona desde el menú principal. Lo elegimos porque
reúne los cuatro problemas identificados y otros módulos (Pedidos, Financiero) dependen
de sus datos.

## Problemas arquitectónicos identificados

| # | Problema | Atributo afectado |
|---|----------|-------------------|
| P1 | Las interfaces tienen demasiadas responsabilidades: `guardar()` lee widgets, convierte tipos, valida y llama a la BD | Mantenibilidad, Testabilidad |
| P2 | La interfaz depende directamente de `crud/` y de SQL Server, sin rollback ni cierre garantizado de la conexión | Testabilidad, Modificabilidad |
| P3 | Código repetido entre módulos (formularios, tablas, selección de filas) | Reutilización, Mantenibilidad |
| P4 | 19 bloques `except Exception`, mensajes técnicos al usuario, sin registro de errores | Confiabilidad |

## Documentación de arquitectura

📐 [`docs/arquitectura.md`](docs/arquitectura.md): arquitectura objetivo, componentes y
responsabilidades, decisiones de refactorización y escenarios de calidad.

- Decisiones (ADR): [`docs/adr/`](docs/adr/)
- Diagramas C4 y de despliegue: [`docs/diagramas/`](docs/diagramas/)

## Instrucciones de ejecución

**Requisitos:** Python 3.10+, SQL Server con la base `EmpresaLimpiezaDB` y el ODBC Driver 17 for SQL Server.

```bash
pip install -r requirements.txt
python src/main.py
```

Por defecto se conecta a `localhost` / `EmpresaLimpiezaDB` con autenticación de Windows.
Para otro servidor, definan las variables de entorno `INVENTARIO_DB_SERVER`, `INVENTARIO_DB_NAME`
y, si usan usuario SQL, `INVENTARIO_DB_USER` e `INVENTARIO_DB_PASSWORD`.

Para abrir el módulo Productos **sin base de datos**, con datos de ejemplo:

```powershell
$env:INVENTARIO_REPO = "memoria"
python src/main.py
```

Los errores quedan registrados en `logs/app.log`.

**Pruebas** (no requieren base de datos ni interfaz gráfica):

```bash
python -m unittest discover -s tests -t . -v
```
