import customtkinter as ctk
from interfaces.estilos import COLORS, setup_ctk
from interfaces.menu_principal import construir_menu
from inventario.comun.registro import configurar_registro, obtener_logger


def main():
    configurar_registro()
    obtener_logger("main").info("Aplicación iniciada")
    setup_ctk()

    # ── Ventana raíz ─────────────────────────────────────────────────────────
    root = ctk.CTk()
    root.title("EmpresaLimpieza · Sistema de Gestión")
    root.geometry("1100x750")
    root.minsize(900, 620)
    root.configure(fg_color=COLORS["bg_dark"])

    # Icono de la ventana (opcional, solo Windows)
    try:
        root.iconbitmap("assets/icon.ico")
    except Exception:
        pass

    # ── Contenedor principal (único, reemplazable) ────────────────────────────
    contenedor = ctk.CTkFrame(root, fg_color=COLORS["bg_dark"], corner_radius=0)
    contenedor.pack(fill="both", expand=True)

    # Cargar el menú al inicio
    construir_menu(contenedor)

    root.mainloop()


if __name__ == "__main__":
    main()
