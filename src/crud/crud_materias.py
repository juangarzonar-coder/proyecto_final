from conexion import conectar

def insertar_materia(nombre, unidad, stock, proveedor):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO MateriaPrima (Nombre_materia, Unidad_medida, Stock, id_proveedor) VALUES (?, ?, ?, ?)",
        (nombre, unidad, stock, proveedor)
    )
    con.commit()
    cur.close(); con.close()

def mostrar_materias():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT m.id_materia, m.Nombre_materia, m.Unidad_medida, m.Stock, p.Nombre
        FROM MateriaPrima m
        LEFT JOIN Proveedor p ON m.id_proveedor = p.id_proveedor
    """)
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_materia(id_materia):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM MateriaPrima WHERE id_materia = ?", (id_materia,))
    con.commit()
    cur.close(); con.close()

def actualizar_materia(id_materia, nombre, unidad, stock, proveedor):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "UPDATE MateriaPrima SET Nombre_materia=?, Unidad_medida=?, Stock=?, id_proveedor=? WHERE id_materia=?",
        (nombre, unidad, stock, proveedor, id_materia)
    )
    con.commit()
    cur.close(); con.close()
