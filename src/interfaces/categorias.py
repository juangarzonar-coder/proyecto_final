import customtkinter as ctk
from interfaces.estilos import *
from crud.crud_categorias import insertar_categoria, mostrar_categorias, eliminar_categoria


def abrir_categorias(contenedor_principal):
    for w in contenedor_principal.winfo_children():
        w.destroy()

    header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(20, 10))
    btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
    section_title(header, "Gestión de Categorías", "🏷").pack(side="left", padx=20)

    body = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=30, pady=10)
    body.grid_columnconfigure(0, weight=0)
    body.grid_columnconfigure(1, weight=1)
    body.grid_rowconfigure(0, weight=1)

    form_frame = styled_frame(body)
    form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 16))
    form_frame.configure(width=280)

    ctk.CTkLabel(form_frame, text="Nueva Categoría", font=FONTS["subtitle"],
                 text_color=COLORS["accent"]).pack(pady=(20, 14), padx=20)

    field_label(form_frame, "Nombre de categoría").pack(anchor="w", padx=20, pady=(8, 2))
    entry_nombre = styled_entry(form_frame, placeholder="Ej: Detergentes", width=220)
    entry_nombre.pack(padx=20)

    right = ctk.CTkFrame(body, fg_color="transparent")
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_rowconfigure(1, weight=1)
    right.grid_columnconfigure(0, weight=1)

    cols = [
        {"id": "id",  "text": "ID",         "width": 80, "anchor": "center"},
        {"id": "nom", "text": "Categoría",   "width": 400},
    ]
    action_bar = ctk.CTkFrame(right, fg_color="transparent")
    action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    tbl_frame, tree = make_table(right, cols, height=16)
    tbl_frame.grid(row=1, column=0, sticky="nsew")

    def refrescar():
        fill_table(tree, mostrar_categorias())

    def guardar():
        nom = entry_nombre.get().strip()
        if not nom:
            show_error("Escribe un nombre de categoría.")
            return
        try:
            insertar_categoria(nom)
            show_success("Categoría registrada.")
            entry_nombre.delete(0, "end")
            refrescar()
        except Exception as ex:
            show_error(f"Error: {ex}")

    def eliminar():
        sel = tree.selection()
        if not sel:
            show_error("Selecciona una categoría.")
            return
        vals = tree.item(sel[0])["values"]
        if confirm_delete(f'"{vals[1]}"'):
            try:
                eliminar_categoria(vals[0])
                show_success("Categoría eliminada.")
                refrescar()
            except Exception as ex:
                show_error(f"No se pudo eliminar (puede tener productos asociados): {ex}")

    btn_primary(form_frame, "Guardar Categoría", guardar, width=220, icon="💾").pack(padx=20, pady=(16, 6))
    btn_danger(form_frame, "Eliminar", eliminar, width=220, icon="🗑").pack(padx=20, pady=(0, 20))
    btn_primary(action_bar, "Actualizar Lista", refrescar, width=180, icon="🔄").pack(side="left")

    refrescar()


def _volver(contenedor):
    from interfaces.menu_principal import construir_menu
    construir_menu(contenedor)
