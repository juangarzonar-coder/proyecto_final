"""
Estilos y utilidades centralizadas para el sistema EmpresaLimpieza.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox

# ─── PALETA DE COLORES 
COLORS = {
    "bg_dark":       "#0D0F14",
    "bg_card":       "#161B27",
    "bg_input":      "#1E2535",
    "bg_sidebar":    "#111520",
    "accent":        "#00C8FF",
    "accent_dim":    "#0099CC",
    "accent_glow":   "#00C8FF22",
    "success":       "#00E5A0",
    "warning":       "#FFB800",
    "danger":        "#FF4D6A",
    "danger_dim":    "#CC2244",
    "text_primary":  "#E8EDF5",
    "text_secondary":"#7A8499",
    "text_muted":    "#4A5268",
    "border":        "#252D40",
    "border_focus":  "#00C8FF55",
    "row_even":      "#161B27",
    "row_odd":       "#1A2030",
    "row_selected":  "#00C8FF18",
    "header_bg":     "#0D1420",
}

# ─── FUENTES 
FONTS = {
    "title":    ("Segoe UI Semibold", 26),
    "subtitle": ("Segoe UI", 14),
    "label":    ("Segoe UI", 12),
    "input":    ("Segoe UI", 13),
    "button":   ("Segoe UI Semibold", 12),
    "table":    ("Consolas", 11),
    "table_hd": ("Segoe UI Semibold", 11),
    "kpi":      ("Segoe UI Semibold", 28),
    "kpi_lbl":  ("Segoe UI", 11),
    "small":    ("Segoe UI", 10),
}


def setup_ctk():
    """Configurar CustomTkinter con el tema oscuro."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def styled_frame(parent, **kwargs):
    """Frame con fondo de tarjeta."""
    return ctk.CTkFrame(
        parent,
        fg_color=kwargs.pop("fg_color", COLORS["bg_card"]),
        corner_radius=kwargs.pop("corner_radius", 12),
        border_width=kwargs.pop("border_width", 1),
        border_color=kwargs.pop("border_color", COLORS["border"]),
        **kwargs
    )


def section_title(parent, text, icon=""):
    """Etiqueta de título de sección."""
    return ctk.CTkLabel(
        parent,
        text=f"{icon}  {text}" if icon else text,
        font=FONTS["title"],
        text_color=COLORS["text_primary"],
    )


def field_label(parent, text):
    return ctk.CTkLabel(
        parent, text=text,
        font=FONTS["label"],
        text_color=COLORS["text_secondary"],
        anchor="w"
    )


def styled_entry(parent, placeholder="", width=260, **kwargs):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        width=width,
        height=38,
        fg_color=COLORS["bg_input"],
        border_color=COLORS["border"],
        border_width=1,
        text_color=COLORS["text_primary"],
        placeholder_text_color=COLORS["text_muted"],
        font=FONTS["input"],
        corner_radius=8,
        **kwargs
    )


def styled_optionmenu(parent, values, width=260, **kwargs):
    return ctk.CTkOptionMenu(
        parent,
        values=values,
        width=width,
        height=38,
        fg_color=COLORS["bg_input"],
        button_color=COLORS["accent_dim"],
        button_hover_color=COLORS["accent"],
        text_color=COLORS["text_primary"],
        font=FONTS["input"],
        corner_radius=8,
        **kwargs
    )


def btn_primary(parent, text, command, width=200, icon=""):
    label = f"{icon} {text}" if icon else text
    return ctk.CTkButton(
        parent,
        text=label,
        command=command,
        width=width,
        height=40,
        fg_color=COLORS["accent_dim"],
        hover_color=COLORS["accent"],
        text_color="#000000",
        font=FONTS["button"],
        corner_radius=8,
    )


def btn_danger(parent, text, command, width=160, icon=""):
    label = f"{icon} {text}" if icon else text
    return ctk.CTkButton(
        parent,
        text=label,
        command=command,
        width=width,
        height=36,
        fg_color=COLORS["danger_dim"],
        hover_color=COLORS["danger"],
        text_color=COLORS["text_primary"],
        font=FONTS["button"],
        corner_radius=8,
    )


def btn_back(parent, command):
    return ctk.CTkButton(
        parent,
        text="← Volver al Menú",
        command=command,
        width=180,
        height=36,
        fg_color=COLORS["bg_input"],
        hover_color=COLORS["border"],
        text_color=COLORS["text_secondary"],
        font=FONTS["button"],
        corner_radius=8,
        border_width=1,
        border_color=COLORS["border"],
    )


def btn_success(parent, text, command, width=160, icon=""):
    label = f"{icon} {text}" if icon else text
    return ctk.CTkButton(
        parent,
        text=label,
        command=command,
        width=width,
        height=36,
        fg_color="#006644",
        hover_color=COLORS["success"],
        text_color=COLORS["text_primary"],
        font=FONTS["button"],
        corner_radius=8,
    )


def setup_treeview_style():
    """Configurar el estilo de todos los Treeview de la app."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Custom.Treeview",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        fieldbackground=COLORS["bg_card"],
        rowheight=32,
        font=FONTS["table"],
        borderwidth=0,
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=COLORS["header_bg"],
        foreground=COLORS["accent"],
        font=FONTS["table_hd"],
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", COLORS["accent_dim"])],
        foreground=[("selected", "#000000")],
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", COLORS["bg_input"])],
    )


def make_table(parent, columns: list, height=14):
    """
    Crea un Treeview estilizado con scrollbar.
    columns: lista de dicts con 'id', 'text', 'width', 'anchor'
    Retorna (frame, tree)
    """
    setup_treeview_style()

    frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)

    col_ids = [c["id"] for c in columns]
    tree = ttk.Treeview(
        frame,
        columns=col_ids,
        show="headings",
        height=height,
        style="Custom.Treeview",
    )

    for col in columns:
        tree.heading(col["id"], text=col["text"])
        tree.column(col["id"], width=col.get("width", 120), anchor=col.get("anchor", "w"), stretch=True)

    # Scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Alternating row colors
    tree.tag_configure("even", background=COLORS["row_even"])
    tree.tag_configure("odd",  background=COLORS["row_odd"])

    return frame, tree


def fill_table(tree, rows):
    """Limpia y rellena el treeview con filas nuevas."""
    for item in tree.get_children():
        tree.delete(item)
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=list(row), tags=(tag,))


def kpi_card(parent, valor, etiqueta, color=None, icon=""):
    """Tarjeta KPI con número grande y etiqueta."""
    color = color or COLORS["accent"]
    frame = ctk.CTkFrame(
        parent,
        fg_color=COLORS["bg_card"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 22), text_color=color).pack(pady=(18, 2))
    ctk.CTkLabel(frame, text=str(valor), font=FONTS["kpi"], text_color=color).pack()
    ctk.CTkLabel(frame, text=etiqueta, font=FONTS["kpi_lbl"], text_color=COLORS["text_secondary"]).pack(pady=(2, 18))
    return frame


def confirm_delete(nombre="este registro"):
    return messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Estás seguro de que deseas eliminar {nombre}?\nEsta acción no se puede deshacer."
    )


def show_error(msg):
    messagebox.showerror("Error", msg)


def show_success(msg):
    messagebox.showinfo("Éxito", msg)
