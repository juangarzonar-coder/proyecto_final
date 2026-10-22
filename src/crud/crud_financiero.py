from conexion import conectar

def ventas_por_mes():
    """Ventas totales agrupadas por mes."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT 
            FORMAT(p.Fecha, 'yyyy-MM') AS Mes,
            SUM(d.Cantidad * d.Precio_unitario) AS Total
        FROM Pedido p
        INNER JOIN DetallePedido d ON p.id_pedido = d.id_pedido
        WHERE p.Estado != 'Cancelado'
        GROUP BY FORMAT(p.Fecha, 'yyyy-MM')
        ORDER BY Mes
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def top_productos_vendidos():
    """Top 5 productos más vendidos por ingresos."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT TOP 5
            pr.Nombre_producto,
            SUM(d.Cantidad) AS Unidades,
            SUM(d.Cantidad * d.Precio_unitario) AS Ingresos
        FROM DetallePedido d
        INNER JOIN Producto pr ON pr.id_producto = d.id_producto
        INNER JOIN Pedido p ON p.id_pedido = d.id_pedido
        WHERE p.Estado != 'Cancelado'
        GROUP BY pr.Nombre_producto
        ORDER BY Ingresos DESC
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def ventas_por_estado():
    """Cantidad de pedidos por estado."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT Estado, COUNT(*) AS Cantidad
        FROM Pedido
        GROUP BY Estado
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def top_clientes():
    """Top 5 clientes por total de compras."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT TOP 5
            c.Nombre,
            COUNT(p.id_pedido) AS NumPedidos,
            SUM(d.Cantidad * d.Precio_unitario) AS TotalCompras
        FROM Cliente c
        INNER JOIN Pedido p ON p.id_cliente = c.id_cliente
        INNER JOIN DetallePedido d ON d.id_pedido = p.id_pedido
        WHERE p.Estado != 'Cancelado'
        GROUP BY c.Nombre
        ORDER BY TotalCompras DESC
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def resumen_financiero():
    """KPIs: total ventas, total pedidos, ticket promedio."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT 
            COUNT(DISTINCT p.id_pedido) AS TotalPedidos,
            ISNULL(SUM(d.Cantidad * d.Precio_unitario), 0) AS TotalVentas,
            ISNULL(AVG(sub.Total), 0) AS TicketPromedio
        FROM Pedido p
        LEFT JOIN DetallePedido d ON p.id_pedido = d.id_pedido
        LEFT JOIN (
            SELECT id_pedido, SUM(Cantidad * Precio_unitario) AS Total
            FROM DetallePedido GROUP BY id_pedido
        ) sub ON sub.id_pedido = p.id_pedido
        WHERE p.Estado != 'Cancelado'
    """)
    datos = cur.fetchone()
    cur.close(); con.close()
    return datos
