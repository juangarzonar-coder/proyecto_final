from conexion import conectar

def insertar_proveedor(nombre, telefono, correo, direccion):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO Proveedor (Nombre, Telefono, Correo, Direccion) VALUES (?, ?, ?, ?)",
        (nombre, telefono, correo, direccion)
    )
    con.commit()
    cur.close(); con.close()

def mostrar_proveedores():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM Proveedor")
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_proveedor(id_proveedor):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM Proveedor WHERE id_proveedor = ?", (id_proveedor,))
    con.commit()
    cur.close(); con.close()

def actualizar_proveedor(id_proveedor, nombre, telefono, correo, direccion):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "UPDATE Proveedor SET Nombre=?, Telefono=?, Correo=?, Direccion=? WHERE id_proveedor=?",
        (nombre, telefono, correo, direccion, id_proveedor)
    )
    con.commit()
    cur.close(); con.close()
