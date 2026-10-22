from conexion import conectar

def insertar_producto(nombre, descripcion, precio, stock, categoria):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO Producto (Nombre_producto, Descripcion, Precio, Stock, id_categoria) VALUES (?, ?, ?, ?, ?)",
        (nombre, descripcion, precio, stock, categoria)
    )
    con.commit()
    cur.close(); con.close()

def mostrar_productos():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT p.id_producto, p.Nombre_producto, p.Descripcion, p.Precio, p.Stock, c.Nombre_categoria
        FROM Producto p
        LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_producto(id_producto):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM Producto WHERE id_producto = ?", (id_producto,))
    con.commit()
    cur.close(); con.close()

def actualizar_producto(id_producto, nombre, descripcion, precio, stock, categoria):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "UPDATE Producto SET Nombre_producto=?, Descripcion=?, Precio=?, Stock=?, id_categoria=? WHERE id_producto=?",
        (nombre, descripcion, precio, stock, categoria, id_producto)
    )
    con.commit()
    cur.close(); con.close()
