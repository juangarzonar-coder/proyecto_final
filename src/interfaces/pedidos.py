import customtkinter as ctk
from interfaces.estilos import *
from crud.crud_pedidos import crear_pedido, agregar_detalle, mostrar_pedidos, mostrar_detalles, eliminar_pedido
from crud.crud_clientes import mostrar_clientes
from crud.crud_productos import mostrar_productos
import datetime


def abrir_pedidos(contenedor_principal):
    for w in contenedor_principal.winfo_children():
        w.destroy()

    header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(20, 10))
    btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
    section_title(header, "Gestión de Pedidos", "📋").pack(side="left", padx=20)

    # Tabs
    tabview = ctk.CTkTabview(
        contenedor_principal,
        fg_color=COLORS["bg_card"],
        segmented_button_fg_color=COLORS["bg_input"],
        segmented_button_selected_color=COLORS["accent_dim"],
        segmented_button_selected_hover_color=COLORS["accent"],
        segmented_button_unselected_color=COLORS["bg_input"],
        segmented_button_unselected_hover_color=COLORS["border"],
        text_color=COLORS["text_primary"],
        corner_radius=12,
    )
    tabview.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    tabview.add("  Pedidos  ")
    tabview.add("  Nuevo Pedido  ")
    tabview.add("  Detalle Pedidos  ")

    # ─Lista de pedidos 
    tab1 = tabview.tab("  Pedidos  ")
    tab1.grid_rowconfigure(1, weight=1)
    tab1.grid_columnconfigure(0, weight=1)

    action1 = ctk.CTkFrame(tab1, fg_color="transparent")
    action1.grid(row=0, column=0, sticky="ew", pady=(10, 8))

    cols1 = [
        {"id": "id",    "text": "ID",      "width": 50, "anchor": "center"},
        {"id": "cli",   "text": "Cliente",  "width": 200},
        {"id": "fec",   "text": "Fecha",    "width": 110, "anchor": "center"},
        {"id": "est",   "text": "Estado",   "width": 110, "anchor": "center"},
        {"id": "tot",   "text": "Total ($)", "width": 110, "anchor": "e"},
    ]
    tbl_frame1, tree1 = make_table(tab1, cols1, height=16)
    tbl_frame1.grid(row=1, column=0, sticky="nsew")

    def refrescar_pedidos():
        fill_table(tree1, mostrar_pedidos())

    def eliminar_ped():
        sel = tree1.selection()
        if not sel:
            show_error("Selecciona un pedido.")
            return
        vals = tree1.item(sel[0])["values"]
        if confirm_delete(f"el pedido #{vals[0]}"):
            try:
                eliminar_pedido(vals[0])
                show_success("Pedido eliminado.")
                refrescar_pedidos()
            except Exception as ex:
                show_error(f"Error: {ex}")

    btn_primary(action1, "Actualizar", refrescar_pedidos, width=160, icon="🔄").pack(side="left")
    btn_danger(action1, "Eliminar pedido", eliminar_ped, width=180, icon="🗑").pack(side="left", padx=(10, 0))

    #Nuevo pedido 
    tab2 = tabview.tab("  Nuevo Pedido  ")
    tab2.grid_columnconfigure(0, weight=1)
    tab2.grid_columnconfigure(1, weight=1)

    #datos del pedido
    col_izq = styled_frame(tab2)
    col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

    ctk.CTkLabel(col_izq, text="Datos del Pedido", font=FONTS["subtitle"],
                 text_color=COLORS["accent"]).pack(pady=(16, 10), padx=20)

    clientes = mostrar_clientes()
    cli_map = {c[1]: c[0] for c in clientes} if clientes else {}
    cli_names = list(cli_map.keys()) if cli_map else ["Sin clientes"]

    field_label(col_izq, "Cliente").pack(anchor="w", padx=20, pady=(6, 2))
    var_cli = ctk.StringVar(value=cli_names[0])
    styled_optionmenu(col_izq, values=cli_names, variable=var_cli, width=280).pack(padx=20)

    field_label(col_izq, "Fecha").pack(anchor="w", padx=20, pady=(10, 2))
    entry_fecha = styled_entry(col_izq, placeholder=str(datetime.date.today()), width=280)
    entry_fecha.pack(padx=20)
    entry_fecha.insert(0, str(datetime.date.today()))

    field_label(col_izq, "Estado").pack(anchor="w", padx=20, pady=(10, 2))
    var_estado = ctk.StringVar(value="Pendiente")
    styled_optionmenu(col_izq, values=["Pendiente", "En proceso", "Entregado", "Cancelado"],
                      variable=var_estado, width=280).pack(padx=20)

    # agregar producto al pedido
    col_der = styled_frame(tab2)
    col_der.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

    ctk.CTkLabel(col_der, text="Agregar Producto", font=FONTS["subtitle"],
                 text_color=COLORS["success"]).pack(pady=(16, 10), padx=20)

    productos = mostrar_productos()
    prod_map = {p[1]: (p[0], p[3]) for p in productos} if productos else {}  # nombre -> (id, precio)
    prod_names = list(prod_map.keys()) if prod_map else ["Sin productos"]

    field_label(col_der, "Producto").pack(anchor="w", padx=20, pady=(6, 2))
    var_prod = ctk.StringVar(value=prod_names[0])
    styled_optionmenu(col_der, values=prod_names, variable=var_prod, width=280).pack(padx=20)

    field_label(col_der, "Cantidad").pack(anchor="w", padx=20, pady=(10, 2))
    entry_cant = styled_entry(col_der, placeholder="1", width=280)
    entry_cant.pack(padx=20)

    field_label(col_der, "Precio unitario ($)").pack(anchor="w", padx=20, pady=(10, 2))
    entry_precio = styled_entry(col_der, placeholder="0.00", width=280)
    entry_precio.pack(padx=20)

    # Auto-llenar precio al seleccionar producto
    def on_prod_change(val):
        if val in prod_map:
            entry_precio.delete(0, "end")
            entry_precio.insert(0, str(prod_map[val][1]))

    var_prod.trace_add("write", lambda *_: on_prod_change(var_prod.get()))

    # Botón de guardar pedido completo
    id_pedido_actual = {"val": None}

    def crear_nuevo_pedido():
        try:
            cli_id = cli_map.get(var_cli.get())
            fecha = entry_fecha.get().strip()
            estado = var_estado.get()
            id_p = crear_pedido(fecha, estado, cli_id)
            id_pedido_actual["val"] = id_p
            show_success(f"Pedido #{id_p} creado. Ahora agrega los productos.")
        except Exception as ex:
            show_error(f"Error al crear pedido: {ex}")

    def agregar_prod_pedido():
        if not id_pedido_actual["val"]:
            show_error("Primero crea el pedido con el botón 'Crear Pedido'.")
            return
        try:
            prod_sel = var_prod.get()
            id_prod = prod_map[prod_sel][0]
            cant = int(entry_cant.get())
            precio = float(entry_precio.get())
            agregar_detalle(id_pedido_actual["val"], id_prod, cant, precio)
            show_success(f"Producto '{prod_sel}' agregado al pedido #{id_pedido_actual['val']}.")
            entry_cant.delete(0, "end")
            refrescar_pedidos()
        except ValueError:
            show_error("Cantidad y precio deben ser números válidos.")
        except Exception as ex:
            show_error(f"Error: {ex}")

    btn_primary(col_izq, "Crear Pedido", crear_nuevo_pedido, width=280, icon="📋").pack(padx=20, pady=(16, 20))
    btn_success(col_der, "Agregar Producto", agregar_prod_pedido, width=280, icon="➕").pack(padx=20, pady=(16, 20))

    # Detalle 
    tab3 = tabview.tab("  Detalle Pedidos  ")
    tab3.grid_rowconfigure(1, weight=1)
    tab3.grid_columnconfigure(0, weight=1)

    action3 = ctk.CTkFrame(tab3, fg_color="transparent")
    action3.grid(row=0, column=0, sticky="ew", pady=(10, 8))

    cols3 = [
        {"id": "pid",  "text": "Pedido #",   "width": 80, "anchor": "center"},
        {"id": "prod", "text": "Producto",    "width": 220},
        {"id": "cant", "text": "Cantidad",    "width": 90, "anchor": "center"},
        {"id": "prec", "text": "P. Unitario", "width": 110, "anchor": "e"},
        {"id": "sub",  "text": "Subtotal",    "width": 110, "anchor": "e"},
    ]
    tbl_frame3, tree3 = make_table(tab3, cols3, height=16)
    tbl_frame3.grid(row=1, column=0, sticky="nsew")

    def refrescar_detalles():
        fill_table(tree3, mostrar_detalles())

    btn_primary(action3, "Actualizar", refrescar_detalles, width=160, icon="🔄").pack(side="left")

    refrescar_pedidos()
    refrescar_detalles()


def _volver(contenedor):
    from interfaces.menu_principal import construir_menu
    construir_menu(contenedor)
