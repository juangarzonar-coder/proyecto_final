from conexion import conectar

def insertar_categoria(nombre):
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO Categoria (Nombre_categoria) VALUES (?)", (nombre,))
    con.commit()
    cur.close(); con.close()

def mostrar_categorias():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM Categoria")
    datos = cur.fetchall()
    cur.close(); con.close()
    return datos

def eliminar_categoria(id_categoria):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM Categoria WHERE id_categoria = ?", (id_categoria,))
    con.commit()
    cur.close(); con.close()
