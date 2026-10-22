import customtkinter as ctk
from interfaces.estilos import COLORS, FONTS, setup_ctk


# BOTONES DEL MENU
MODULOS = [
    ("📦", "Productos",         "abrir_productos",  "inventario.presentacion.vistas.productos_vista"),
    ("🧪", "Materias Primas",   "abrir_materias",   "interfaces.materias"),
    ("📋", "Pedidos",           "abrir_pedidos",    "interfaces.pedidos"),
    ("👥", "Clientes",          "abrir_clientes",   "interfaces.clientes"),
    ("🏷",  "Categorías",       "abrir_categorias", "interfaces.categorias"),
    ("🏭", "Proveedores",       "abrir_proveedores","interfaces.proveedores"),
    ("📊", "Análisis Financiero","abrir_financiero", "interfaces.financiero"),
]


def construir_menu(contenedor):
    """Construye el menú principal dentro del contenedor dado."""
    for w in contenedor.winfo_children():
        w.destroy()

    # ── Bienvenida / logo ────────────────────────────────────────────────────
    top = ctk.CTkFrame(contenedor, fg_color="transparent")
    top.pack(pady=(50, 30))

    ctk.CTkLabel(
        top,
        text="✨  EmpresaLimpieza",
        font=("Segoe UI Semibold", 36),
        text_color=COLORS["accent"],
    ).pack()

    ctk.CTkLabel(
        top,
        text="Sistema de Gestión Empresarial",
        font=FONTS["subtitle"],
        text_color=COLORS["text_secondary"],
    ).pack(pady=(4, 0))

    # Separador
    sep = ctk.CTkFrame(contenedor, height=2, fg_color=COLORS["accent_dim"])
    sep.pack(fill="x", padx=100, pady=(0, 30))

    # Botones de modulo
    grid_frame = ctk.CTkFrame(contenedor, fg_color="transparent")
    grid_frame.pack(expand=True)

    for i, (icon, nombre, func_name, modulo) in enumerate(MODULOS):
        row, col = divmod(i, 2)

        card = ctk.CTkFrame(
            grid_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
            width=240,
            height=90,
            cursor="hand2",
        )
        card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 28),
                     text_color=COLORS["accent"]).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(inner, text=nombre, font=("Segoe UI Semibold", 15),
                     text_color=COLORS["text_primary"]).pack(side="left")

        # Hover
        def make_hover(c, enter_color, leave_color):
            c.bind("<Enter>", lambda e: c.configure(fg_color=enter_color, border_color=COLORS["accent"]))
            c.bind("<Leave>", lambda e: c.configure(fg_color=leave_color, border_color=COLORS["border"]))
            for child in c.winfo_children():
                child.bind("<Enter>", lambda e: c.configure(fg_color=enter_color, border_color=COLORS["accent"]))
                child.bind("<Leave>", lambda e: c.configure(fg_color=leave_color, border_color=COLORS["border"]))

        make_hover(card, COLORS["bg_input"], COLORS["bg_card"])

        # abrir menu
        def make_click(fn, mod, cont):
            def click(event=None):
                import importlib
                m = importlib.import_module(mod)
                getattr(m, fn)(cont)
            return click

        handler = make_click(func_name, modulo, contenedor)
        card.bind("<Button-1>", handler)
        inner.bind("<Button-1>", handler)
        for child in inner.winfo_children():
            child.bind("<Button-1>", handler)

    # Footer 
    ctk.CTkLabel(
        contenedor,
        text="© 2025 EmpresaLimpieza · Sistema Interno",
        font=FONTS["small"],
        text_color=COLORS["text_muted"],
    ).pack(pady=(30, 20))
