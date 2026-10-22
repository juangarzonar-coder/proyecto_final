import customtkinter as ctk
from interfaces.estilos import *
from crud.crud_proveedores import insertar_proveedor, mostrar_proveedores, eliminar_proveedor, actualizar_proveedor


def abrir_proveedores(contenedor_principal):
    for w in contenedor_principal.winfo_children():
        w.destroy()

    header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(20, 10))
    btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
    section_title(header, "Gestión de Proveedores", "🏭").pack(side="left", padx=20)

    body = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=30, pady=10)
    body.grid_columnconfigure(0, weight=0)
    body.grid_columnconfigure(1, weight=1)
    body.grid_rowconfigure(0, weight=1)

    form_frame = styled_frame(body)
    form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 16))
    form_frame.configure(width=300)

    ctk.CTkLabel(form_frame, text="Datos del Proveedor", font=FONTS["subtitle"],
                 text_color=COLORS["accent"]).pack(pady=(20, 14), padx=20)

    campos = {}
    for nombre, ph in [
        ("Nombre",    "Nombre empresa/persona"),
        ("Teléfono",  "+57 300 000 0000"),
        ("Correo",    "correo@empresa.com"),
        ("Dirección", "Calle y ciudad"),
    ]:
        field_label(form_frame, nombre).pack(anchor="w", padx=20, pady=(8, 2))
        e = styled_entry(form_frame, placeholder=ph, width=240)
        e.pack(padx=20)
        campos[nombre] = e

    right = ctk.CTkFrame(body, fg_color="transparent")
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_rowconfigure(1, weight=1)
    right.grid_columnconfigure(0, weight=1)

    cols = [
        {"id": "id",  "text": "ID",        "width": 50, "anchor": "center"},
        {"id": "nom", "text": "Nombre",     "width": 200},
        {"id": "tel", "text": "Teléfono",   "width": 140},
        {"id": "cor", "text": "Correo",     "width": 200},
        {"id": "dir", "text": "Dirección",  "width": 220},
    ]
    action_bar = ctk.CTkFrame(right, fg_color="transparent")
    action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    tbl_frame, tree = make_table(right, cols, height=16)
    tbl_frame.grid(row=1, column=0, sticky="nsew")

    id_editando = {"val": None}

    def refrescar():
        fill_table(tree, mostrar_proveedores())

    def guardar():
        try:
            nom  = campos["Nombre"].get().strip()
            tel  = campos["Teléfono"].get().strip()
            cor  = campos["Correo"].get().strip()
            dir_ = campos["Dirección"].get().strip()
            if not nom:
                show_error("El nombre es obligatorio.")
                return
            if id_editando["val"]:
                actualizar_proveedor(id_editando["val"], nom, tel, cor, dir_)
                show_success("Proveedor actualizado.")
                id_editando["val"] = None
                btn_guardar.configure(text="  Guardar Proveedor")
            else:
                insertar_proveedor(nom, tel, cor, dir_)
                show_success("Proveedor registrado.")
            for e in campos.values(): e.delete(0, "end")
            refrescar()
        except Exception as ex:
            show_error(f"Error: {ex}")

    def eliminar():
        sel = tree.selection()
        if not sel:
            show_error("Selecciona un proveedor.")
            return
        vals = tree.item(sel[0])["values"]
        if confirm_delete(f'"{vals[1]}"'):
            try:
                eliminar_proveedor(vals[0])
                show_success("Proveedor eliminado.")
                refrescar()
            except Exception as ex:
                show_error(f"No se pudo eliminar: {ex}")

    def cargar_form(event):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])["values"]
        id_editando["val"] = vals[0]
        for k, v in zip(["Nombre", "Teléfono", "Correo", "Dirección"], vals[1:]):
            campos[k].delete(0, "end")
            campos[k].insert(0, v)
        btn_guardar.configure(text="  Actualizar")

    tree.bind("<ButtonRelease-1>", cargar_form)

    btn_guardar = btn_primary(form_frame, "Guardar Proveedor", guardar, width=240, icon="💾")
    btn_guardar.pack(padx=20, pady=(16, 6))
    btn_danger(form_frame, "Eliminar", eliminar, width=240, icon="🗑").pack(padx=20, pady=(0, 20))
    btn_primary(action_bar, "Actualizar Lista", refrescar, width=180, icon="🔄").pack(side="left")

    refrescar()


def _volver(contenedor):
    from interfaces.menu_principal import construir_menu
    construir_menu(contenedor)
