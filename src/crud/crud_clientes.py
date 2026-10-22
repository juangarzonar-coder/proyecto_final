from conexion import conectar

def insertar_cliente(nombre, telefono, correo, direccion):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO Cliente (Nombre, Telefono, Correo, Direccion) VALUES (?, ?, ?, ?)",
        (nombre, telefono, correo, direccion)
    )
    con.commit()
    cur.close(); con.close()

def mostrar_clientes():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM Cliente")
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_cliente(id_cliente):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM Cliente WHERE id_cliente = ?", (id_cliente,))
    con.commit()
    cur.close(); con.close()

def actualizar_cliente(id_cliente, nombre, telefono, correo, direccion):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "UPDATE Cliente SET Nombre=?, Telefono=?, Correo=?, Direccion=? WHERE id_cliente=?",
        (nombre, telefono, correo, direccion, id_cliente)
    )
    con.commit()
    cur.close(); con.close()
