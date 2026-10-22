import customtkinter as ctk
from interfaces.estilos import *
from crud.crud_financiero import (
    ventas_por_mes, top_productos_vendidos, ventas_por_estado,
    top_clientes, resumen_financiero
)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

# Paleta de colores para gráficas
CHART_COLORS = ["#00C8FF", "#00E5A0", "#FFB800", "#FF4D6A", "#B44DFF",
                "#FF8C42", "#4DFFD2", "#FF6BD6", "#C8FF00", "#5B8CFF"]

DARK_BG   = "#0D0F14"
CARD_BG   = "#161B27"
GRID_COL  = "#252D40"
TEXT_COL  = "#E8EDF5"
ACCENT    = "#00C8FF"


def _apply_dark_style(fig, ax_list):
    fig.patch.set_facecolor(CARD_BG)
    for ax in ax_list:
        ax.set_facecolor(DARK_BG)
        ax.tick_params(colors=TEXT_COL, labelsize=9)
        ax.xaxis.label.set_color(TEXT_COL)
        ax.yaxis.label.set_color(TEXT_COL)
        ax.title.set_color(ACCENT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        ax.grid(color=GRID_COL, linestyle="--", linewidth=0.5, alpha=0.7)


def abrir_financiero(contenedor_principal):
    if not MATPLOTLIB_OK:
        for w in contenedor_principal.winfo_children():
            w.destroy()
        header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
        ctk.CTkLabel(
            contenedor_principal,
            text="⚠  Instala matplotlib para ver las gráficas:\n\npip install matplotlib",
            font=FONTS["subtitle"],
            text_color=COLORS["warning"],
        ).pack(expand=True)
        return

    for w in contenedor_principal.winfo_children():
        w.destroy()

    # Header 
    header = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    header.pack(fill="x", padx=30, pady=(20, 6))
    btn_back(header, lambda: _volver(contenedor_principal)).pack(side="left")
    section_title(header, "Análisis Financiero", "📊").pack(side="left", padx=20)

    btn_primary(header, "Actualizar datos", lambda: _recargar(contenedor_principal),
                width=180, icon="🔄").pack(side="right")

    #  KPIs 
    try:
        resumen = resumen_financiero()
        total_pedidos = resumen[0] if resumen else 0
        total_ventas  = resumen[1] if resumen else 0
        ticket_prom   = resumen[2] if resumen else 0
    except Exception:
        total_pedidos, total_ventas, ticket_prom = 0, 0, 0

    kpi_row = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    kpi_row.pack(fill="x", padx=30, pady=(4, 12))
    kpi_row.grid_columnconfigure((0, 1, 2), weight=1)

    kpi_card(kpi_row, f"${total_ventas:,.0f}", "Ventas Totales", COLORS["accent"], "💰").grid(
        row=0, column=0, sticky="ew", padx=6)
    kpi_card(kpi_row, str(total_pedidos), "Pedidos Completados", COLORS["success"], "📋").grid(
        row=0, column=1, sticky="ew", padx=6)
    kpi_card(kpi_row, f"${ticket_prom:,.0f}", "Ticket Promedio", COLORS["warning"], "🎯").grid(
        row=0, column=2, sticky="ew", padx=6)

    # ── Gráficas (2x2 grid)
    charts_frame = ctk.CTkFrame(contenedor_principal, fg_color="transparent")
    charts_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    charts_frame.grid_columnconfigure((0, 1), weight=1)
    charts_frame.grid_rowconfigure((0, 1), weight=1)

    # ── Gráfica 1: Ventas por mes 
    try:
        datos_mes = ventas_por_mes()
        meses  = [r[0] for r in datos_mes]
        totales = [float(r[1]) for r in datos_mes]
    except Exception:
        meses, totales = [], []

    fig1, ax1 = plt.subplots(figsize=(5, 3), tight_layout=True)
    if meses:
        bars = ax1.bar(meses, totales, color=ACCENT, alpha=0.85, width=0.5, zorder=3)
        ax1.bar_label(bars, fmt="$%.0f", label_type="edge", color=TEXT_COL, fontsize=8, padding=2)
        ax1.set_xticks(range(len(meses)))
        ax1.set_xticklabels(meses, rotation=30, ha="right", fontsize=8)
    else:
        ax1.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=TEXT_COL)
    ax1.set_title("Ventas por Mes", fontweight="bold", fontsize=11)
    ax1.set_ylabel("Total ($)")
    _apply_dark_style(fig1, [ax1])

    card1 = styled_frame(charts_frame)
    card1.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    FigureCanvasTkAgg(fig1, master=card1).get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ── Gráfica 2: Top 5 productos 
    try:
        datos_prod = top_productos_vendidos()
        prod_names  = [r[0][:18] for r in datos_prod]
        prod_ing    = [float(r[2]) for r in datos_prod]
    except Exception:
        prod_names, prod_ing = [], []

    fig2, ax2 = plt.subplots(figsize=(5, 3), tight_layout=True)
    if prod_names:
        y_pos = range(len(prod_names))
        h_bars = ax2.barh(list(y_pos), prod_ing,
                          color=CHART_COLORS[:len(prod_names)], alpha=0.85, height=0.55, zorder=3)
        ax2.set_yticks(list(y_pos))
        ax2.set_yticklabels(prod_names, fontsize=9)
        ax2.bar_label(h_bars, fmt="$%.0f", label_type="edge", color=TEXT_COL, fontsize=8, padding=3)
    else:
        ax2.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=TEXT_COL)
    ax2.set_title("Top 5 Productos por Ingresos", fontweight="bold", fontsize=11)
    ax2.set_xlabel("Ingresos ($)")
    ax2.invert_yaxis()
    _apply_dark_style(fig2, [ax2])

    card2 = styled_frame(charts_frame)
    card2.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
    FigureCanvasTkAgg(fig2, master=card2).get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ── Gráfica 3: Pedidos por estado (dona) 
    try:
        datos_estado = ventas_por_estado()
        est_labels = [r[0] for r in datos_estado]
        est_vals   = [r[1] for r in datos_estado]
    except Exception:
        est_labels, est_vals = [], []

    fig3, ax3 = plt.subplots(figsize=(5, 3), tight_layout=True)
    if est_labels:
        wedges, texts, autotexts = ax3.pie(
            est_vals, labels=est_labels,
            colors=CHART_COLORS[:len(est_labels)],
            autopct="%1.0f%%", startangle=140,
            wedgeprops={"edgecolor": CARD_BG, "linewidth": 2},
            pctdistance=0.75, labeldistance=1.12,
        )
        # Dona
        centre_circle = plt.Circle((0, 0), 0.52, fc=CARD_BG)
        ax3.add_artist(centre_circle)
        for t in texts:     t.set_color(TEXT_COL)
        for at in autotexts: at.set_color(DARK_BG); at.set_fontsize(9); at.set_fontweight("bold")
    else:
        ax3.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=TEXT_COL)
    ax3.set_title("Pedidos por Estado", fontweight="bold", fontsize=11)
    fig3.patch.set_facecolor(CARD_BG)
    ax3.set_facecolor(CARD_BG)
    ax3.title.set_color(ACCENT)
    for spine in ax3.spines.values(): spine.set_edgecolor(GRID_COL)

    card3 = styled_frame(charts_frame)
    card3.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
    FigureCanvasTkAgg(fig3, master=card3).get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ── Gráfica 4: Top 5 clientes 
    try:
        datos_cli = top_clientes()
        cli_names_  = [r[0][:18] for r in datos_cli]
        cli_totales = [float(r[2]) for r in datos_cli]
    except Exception:
        cli_names_, cli_totales = [], []

    fig4, ax4 = plt.subplots(figsize=(5, 3), tight_layout=True)
    if cli_names_:
        x_pos = range(len(cli_names_))
        ax4.bar(list(x_pos), cli_totales,
                color=[CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(cli_names_))],
                alpha=0.85, width=0.55, zorder=3)
        ax4.set_xticks(list(x_pos))
        ax4.set_xticklabels(cli_names_, rotation=20, ha="right", fontsize=9)
    else:
        ax4.text(0.5, 0.5, "Sin datos", ha="center", va="center", color=TEXT_COL)
    ax4.set_title("Top 5 Clientes por Compras", fontweight="bold", fontsize=11)
    ax4.set_ylabel("Total ($)")
    _apply_dark_style(fig4, [ax4])

    card4 = styled_frame(charts_frame)
    card4.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
    FigureCanvasTkAgg(fig4, master=card4).get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)


def _recargar(contenedor):
    abrir_financiero(contenedor)


def _volver(contenedor):
    from interfaces.menu_principal import construir_menu
    construir_menu(contenedor)
