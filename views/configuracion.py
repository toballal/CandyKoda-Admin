import flet as ft

from components.sidebar import sidebar
from database.configuracion_sistema import (
    obtener_configuraciones,
    establecer_modo_mantenimiento,
    guardar_configuraciones,
)


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
ROJO = "#FF4FA3"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#C3C3CE"


def configuracion_view(page: ft.Page):

    configuracion = obtener_configuraciones()

    # =========================================================
    # CAMPOS
    # =========================================================

    nombre_sistema = ft.TextField(
        label="Nombre del sistema",
        value=configuracion["nombre_sistema"],
        prefix_icon=ft.Icons.STORE_OUTLINED,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
    )

    stock_minimo = ft.TextField(
        label="Stock mínimo predeterminado",
        value=configuracion["stock_minimo"],
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.INVENTORY_2_OUTLINED,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
    )

    moneda = ft.Dropdown(
        label="Moneda",
        value=(
            configuracion["moneda"]
            if configuracion["moneda"] in {"CLP"}
            else "CLP"
        ),
        options=[
            ft.DropdownOption(
                key="CLP",
                text="Peso chileno (CLP)",
            )
        ],
    )

    puerto_arduino = ft.TextField(
        label="Puerto Arduino",
        value=configuracion["puerto_arduino"],
        prefix_icon=ft.Icons.USB,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
    )

    velocidad_serial = ft.Dropdown(
        label="Velocidad serial",
        value=(
            configuracion["velocidad_serial"]
            if configuracion["velocidad_serial"]
            in {"9600", "19200", "57600", "115200"}
            else "9600"
        ),
        options=[
            ft.DropdownOption(
                key="9600",
                text="9600",
            ),
            ft.DropdownOption(
                key="19200",
                text="19200",
            ),
            ft.DropdownOption(
                key="57600",
                text="57600",
            ),
            ft.DropdownOption(
                key="115200",
                text="115200",
            ),
        ],
    )

    video_fondo = ft.Switch(
        label="Mostrar video de fondo",
        value=configuracion["video_fondo"].strip().casefold()
        in {"1", "true", "si", "sí"},
        active_color=MORADO,
    )

    modo_mantenimiento = ft.Switch(
        label="Pausar ventas en Candy Koda Market",
        value=configuracion["market_mantenimiento"].strip().casefold()
        in {"1", "true", "activo", "si", "sí"},
        active_color=ROSA,
    )

    # =========================================================
    # SNACKBAR
    # =========================================================

    def mostrar_mensaje(texto, color=VERDE):

        snack = ft.SnackBar(
            content=ft.Text(
                texto,
                color="#FFFFFF",
            ),
            bgcolor=color,
        )

        page.show_dialog(snack)

    def cambiar_modo_mantenimiento(e):

        usuario = getattr(
            page,
            "usuario_actual",
            None,
        ) or {}

        id_usuario = (
            usuario.get("id_usuario")
            if isinstance(usuario, dict)
            else None
        )

        if establecer_modo_mantenimiento(
            bool(e.control.value),
            id_usuario,
        ):

            mostrar_mensaje(
                "Market pausado por mantenimiento."
                if e.control.value
                else "Market habilitado para ventas."
            )

        else:

            e.control.value = not e.control.value
            e.control.update()

            mostrar_mensaje(
                "No se pudo cambiar el estado del Market.",
                ROJO,
            )

    modo_mantenimiento.on_change = cambiar_modo_mantenimiento

    # =========================================================
    # GUARDAR
    # =========================================================

    def guardar_configuracion(e):

        nombre = (
            nombre_sistema.value or ""
        ).strip()

        puerto = (
            puerto_arduino.value or ""
        ).strip()

        if not nombre:

            mostrar_mensaje(
                "Ingrese el nombre del sistema.",
                ROJO,
            )

            return

        if not puerto:

            mostrar_mensaje(
                "Ingrese el puerto del Arduino.",
                ROJO,
            )

            return

        try:

            stock = int(
                stock_minimo.value
            )

            if stock < 0:
                raise ValueError

        except ValueError:

            mostrar_mensaje(
                "El stock mínimo debe ser un número válido.",
                ROJO,
            )

            return

        usuario = getattr(page, "usuario_actual", None) or {}
        id_usuario = (
            usuario.get("id_usuario")
            if isinstance(usuario, dict)
            else None
        )

        valores = {
            "nombre_sistema": nombre,
            "stock_minimo": str(stock),
            "moneda": moneda.value or "CLP",
            "puerto_arduino": puerto,
            "velocidad_serial": velocidad_serial.value or "9600",
            "video_fondo": "1" if video_fondo.value else "0",
        }

        if guardar_configuraciones(valores, id_usuario):
            page.configuracion_sistema = {
                **getattr(page, "configuracion_sistema", {}),
                **valores,
            }
            page.title = f"{nombre} Admin"
            mostrar_mensaje(
                "Configuración guardada correctamente."
            )
        else:
            mostrar_mensaje(
                "No se pudo guardar la configuración.",
                ROJO,
            )

    # =========================================================
    # TARJETA DE CONFIGURACIÓN
    # =========================================================

    def seccion(
        titulo,
        descripcion,
        icono,
        controles,
    ):

        return ft.Container(
            bgcolor=COLOR_CARD,
            border_radius=16,
            border=ft.Border.all(
                1,
                COLOR_BORDE,
            ),
            padding=22,
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.Container(
                                width=46,
                                height=46,
                                border_radius=12,
                                bgcolor=ft.Colors.with_opacity(
                                    0.13,
                                    MORADO,
                                ),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    icono,
                                    color=MORADO,
                                    size=24,
                                ),
                            ),

                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        titulo,
                                        size=17,
                                        color=TEXTO_PRINCIPAL,
                                        weight=ft.FontWeight.BOLD,
                                    ),

                                    ft.Text(
                                        descripcion,
                                        size=12,
                                        color=TEXTO_SECUNDARIO,
                                    ),
                                ],
                            ),
                        ],
                    ),

                    ft.Divider(
                        color=COLOR_BORDE,
                        height=1,
                    ),

                    *controles,
                ],
            ),
        )

    # =========================================================
    # GENERAL
    # =========================================================

    general = seccion(
        "General",
        "Configuración general de Candy Koda",
        ft.Icons.TUNE_ROUNDED,
        [
            ft.Row(
                spacing=15,
                controls=[
                    ft.Container(
                        expand=True,
                        content=nombre_sistema,
                    ),

                    ft.Container(
                        width=220,
                        content=moneda,
                    ),
                ],
            ),

            ft.Row(
                controls=[
                    ft.Container(
                        width=300,
                        content=stock_minimo,
                    ),
                ],
            ),
        ],
    )

    # =========================================================
    # HARDWARE
    # =========================================================

    hardware = seccion(
        "Hardware",
        "Configura la comunicación con el Arduino",
        ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
        [
            ft.Row(
                spacing=15,
                controls=[
                    ft.Container(
                        expand=True,
                        content=puerto_arduino,
                    ),

                    ft.Container(
                        expand=True,
                        content=velocidad_serial,
                    ),
                ],
            ),

            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor=COLOR_CARD_2,
                content=ft.Row(
                    spacing=12,
                    controls=[
                        ft.Icon(
                            ft.Icons.INFO_OUTLINE,
                            color=MORADO,
                            size=20,
                        ),

                        ft.Text(
                            "Los cambios del puerto se aplicarán "
                            "al volver a conectar el Arduino.",
                            size=12,
                            color=TEXTO_SECUNDARIO,
                        ),
                    ],
                ),
            ),
        ],
    )

    # =========================================================
    # INTERFAZ
    # =========================================================

    interfaz = seccion(
        "Interfaz",
        "Personaliza algunos elementos visuales",
        ft.Icons.PALETTE_OUTLINED,
        [
            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor=COLOR_CARD_2,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    "Video de fondo",
                                    size=14,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.W_500,
                                ),

                                ft.Text(
                                    "Mostrar el video decorativo "
                                    "en el fondo de la aplicación.",
                                    size=11,
                                    color=TEXTO_SECUNDARIO,
                                ),
                            ],
                        ),

                        video_fondo,
                    ],
                ),
            )
        ],
    )

    # =========================================================
    # CONTENIDO
    # =========================================================

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=ft.Colors.with_opacity(
            0.85,
            COLOR_FONDO,
        ),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=22,
            controls=[

                # CABECERA
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Configuración",
                                    size=30,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "Administra las preferencias generales del sistema.",
                                    size=14,
                                    color=TEXTO_SECUNDARIO,
                                ),
                            ],
                        ),

                        ft.ElevatedButton(
                            "Guardar cambios",
                            icon=ft.Icons.SAVE_OUTLINED,
                            height=45,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            on_click=guardar_configuracion,
                        ),
                    ],
                ),

                general,
                hardware,
                interfaz,

                seccion(
                    "Operación del Market",
                    "Controla si el tótem puede recibir nuevas compras",
                    ft.Icons.POINT_OF_SALE_ROUNDED,
                    [
                        ft.Container(
                            padding=15,
                            border_radius=10,
                            bgcolor=COLOR_CARD_2,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        spacing=3,
                                        controls=[
                                            ft.Text(
                                                "Modo de mantenimiento",
                                                size=14,
                                                color=TEXTO_PRINCIPAL,
                                                weight=ft.FontWeight.W_500,
                                            ),

                                            ft.Text(
                                                "Bloquea nuevas compras y muestra una "
                                                "pantalla informativa en el tótem.",
                                                size=11,
                                                color=TEXTO_SECUNDARIO,
                                            ),
                                        ],
                                    ),

                                    modo_mantenimiento,
                                ],
                            ),
                        )
                    ],
                ),

                ft.Container(
                    height=20,
                ),
            ],
        ),
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/configuracion",
        padding=0,
        spacing=0,
        bgcolor=ft.Colors.TRANSPARENT,
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    sidebar(page),
                    contenido,
                ],
            )
        ],
    )
