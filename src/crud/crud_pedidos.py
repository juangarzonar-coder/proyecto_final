from conexion import conectar

def crear_pedido(fecha, estado, cliente):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO Pedido (Fecha, Estado, id_cliente) VALUES (?, ?, ?)",
        (fecha, estado, cliente)
    )
    con.commit()
    # Obtener el ID del pedido
    cur.execute("SELECT @@IDENTITY")
    id_pedido = cur.fetchone()[0]
    cur.close(); con.close()
    return int(id_pedido)

def agregar_detalle(id_pedido, id_producto, cantidad, precio):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO DetallePedido (id_pedido, id_producto, Cantidad, Precio_unitario) VALUES (?, ?, ?, ?)",
        (id_pedido, id_producto, cantidad, precio)
    )
    con.commit()
    cur.close(); con.close()

def mostrar_pedidos():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.id_pedido, c.Nombre, p.Fecha, p.Estado,
               ISNULL(SUM(d.Cantidad * d.Precio_unitario), 0) AS Total
        FROM Pedido p
        LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
        LEFT JOIN DetallePedido d ON p.id_pedido = d.id_pedido
        GROUP BY p.id_pedido, c.Nombre, p.Fecha, p.Estado
        ORDER BY p.Fecha DESC
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def mostrar_detalles():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.id_pedido, pr.Nombre_producto, d.Cantidad, d.Precio_unitario,
               d.Cantidad * d.Precio_unitario AS Subtotal
        FROM DetallePedido d
        INNER JOIN Pedido p ON p.id_pedido = d.id_pedido
        INNER JOIN Producto pr ON pr.id_producto = d.id_producto
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_pedido(id_pedido):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM DetallePedido WHERE id_pedido = ?", (id_pedido,))
    cur.execute("DELETE FROM Pedido WHERE id_pedido = ?", (id_pedido,))
    con.commit()
    cur.close(); con.close()
