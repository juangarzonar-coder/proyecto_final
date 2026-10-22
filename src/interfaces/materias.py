import customtkinter as ctk
from interfaces.estilos import *
from crud.crud_materias import insertar_materia, mostrar_materias, eliminar_materia, actualizar_materia
from crud.crud_proveedores import mostrar_proveedores


def abrir_materias(contenedor_principal):
    for w in contenedor_principal.winfo_children():
        w.destroy()

    header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(20, 10))
    btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
    section_title(header, "Materias Primas", "🧪").pack(side="left", padx=20)

    body = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=30, pady=10)
    body.grid_columnconfigure(0, weight=0)
    body.grid_columnconfigure(1, weight=1)
    body.grid_rowconfigure(0, weight=1)

    form_frame = styled_frame(body)
    form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 16))
    form_frame.configure(width=300)

    ctk.CTkLabel(form_frame, text="Nueva Materia Prima", font=FONTS["subtitle"],
                 text_color=COLORS["accent"]).pack(pady=(20, 14), padx=20)

    campos = {}
    for nombre, ph in [
        ("Nombre",  "Ej: Hipoclorito de sodio"),
        ("Unidad",  "kg / L / unidad"),
        ("Stock",   "0"),
    ]:
        field_label(form_frame, nombre).pack(anchor="w", padx=20, pady=(8, 2))
        e = styled_entry(form_frame, placeholder=ph, width=240)
        e.pack(padx=20)
        campos[nombre] = e

    field_label(form_frame, "Proveedor").pack(anchor="w", padx=20, pady=(10, 2))
    provs = mostrar_proveedores()
    prov_map = {p[1]: p[0] for p in provs} if provs else {}
    prov_names = list(prov_map.keys()) if prov_map else ["Sin proveedores"]

    var_prov = ctk.StringVar(value=prov_names[0])
    dd_prov = styled_optionmenu(form_frame, values=prov_names, variable=var_prov, width=240)
    dd_prov.pack(padx=20, pady=(0, 6))

    right = ctk.CTkFrame(body, fg_color="transparent")
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_rowconfigure(1, weight=1)
    right.grid_columnconfigure(0, weight=1)

    cols = [
        {"id": "id",   "text": "ID",       "width": 50, "anchor": "center"},
        {"id": "nom",  "text": "Nombre",    "width": 200},
        {"id": "uni",  "text": "Unidad",    "width": 100, "anchor": "center"},
        {"id": "stk",  "text": "Stock",     "width": 80, "anchor": "center"},
        {"id": "prov", "text": "Proveedor", "width": 180},
    ]
    action_bar = ctk.CTkFrame(right, fg_color="transparent")
    action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    tbl_frame, tree = make_table(right, cols, height=16)
    tbl_frame.grid(row=1, column=0, sticky="nsew")

    id_editando = {"val": None}

    def refrescar():
        fill_table(tree, mostrar_materias())

    def guardar():
        try:
            nom  = campos["Nombre"].get().strip()
            uni  = campos["Unidad"].get().strip()
            stk  = int(campos["Stock"].get())
            prov_id = prov_map.get(var_prov.get())
            if not nom:
                show_error("El nombre es obligatorio.")
                return
            if id_editando["val"]:
                actualizar_materia(id_editando["val"], nom, uni, stk, prov_id)
                show_success("Materia actualizada.")
                id_editando["val"] = None
                btn_guardar.configure(text="  Guardar")
            else:
                insertar_materia(nom, uni, stk, prov_id)
                show_success("Materia registrada.")
            for e in campos.values(): e.delete(0, "end")
            refrescar()
        except ValueError:
            show_error("Stock debe ser un número entero.")
        except Exception as ex:
            show_error(f"Error: {ex}")

    def eliminar():
        sel = tree.selection()
        if not sel:
            show_error("Selecciona una materia prima.")
            return
        vals = tree.item(sel[0])["values"]
        if confirm_delete(f'"{vals[1]}"'):
            try:
                eliminar_materia(vals[0])
                show_success("Materia eliminada.")
                refrescar()
            except Exception as ex:
                show_error(f"No se pudo eliminar: {ex}")

    def cargar_form(event):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])["values"]
        id_editando["val"] = vals[0]
        campos["Nombre"].delete(0, "end"); campos["Nombre"].insert(0, vals[1])
        campos["Unidad"].delete(0, "end"); campos["Unidad"].insert(0, vals[2])
        campos["Stock"].delete(0, "end");  campos["Stock"].insert(0, vals[3])
        if vals[4] in prov_map:
            var_prov.set(vals[4])
        btn_guardar.configure(text="  Actualizar")

    tree.bind("<ButtonRelease-1>", cargar_form)

    btn_guardar = btn_primary(form_frame, "Guardar", guardar, width=240, icon="💾")
    btn_guardar.pack(padx=20, pady=(16, 6))
    btn_danger(form_frame, "Eliminar", eliminar, width=240, icon="🗑").pack(padx=20, pady=(0, 20))
    btn_primary(action_bar, "Actualizar Lista", refrescar, width=180, icon="🔄").pack(side="left")

    refrescar()


def _volver(contenedor):
    from interfaces.menu_principal import construir_menu
    construir_menu(contenedor)
