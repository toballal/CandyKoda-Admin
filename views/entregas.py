import flet as ft

from components.sidebar import sidebar
from database.entregas import obtener_entregas


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
AMARILLO = "#FFC107"
ROJO = "#FF4FA3"
AZUL = "#9B59FF"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#C3C3CE"


def entregas_view(page: ft.Page):

    entregas = obtener_entregas()

    filtro_estado = None

    texto_total = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_completadas = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_errores = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_pendientes = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    buscador = ft.TextField(
        hint_text="Buscar venta, producto o dispensador...",
        prefix_icon=ft.Icons.SEARCH,
        width=420,
        height=45,
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
        cursor_color=ROSA,
        color=TEXTO_PRINCIPAL,
        border_radius=12
    )

    lista_entregas = ft.Column(
        spacing=10
    )

    def formatear_fecha(fecha):

        if fecha is None:
            return "-"

        if hasattr(fecha, "strftime"):
            return fecha.strftime("%d/%m/%Y %H:%M")

        return str(fecha)

    def obtener_estilo_estado(estado):

        if estado == "Completada":
            return (
                VERDE,
                ft.Icons.CHECK_CIRCLE_OUTLINE
            )

        elif estado == "Error":
            return (
                ROJO,
                ft.Icons.ERROR_OUTLINE
            )

        elif estado == "Pendiente":
            return (
                AMARILLO,
                ft.Icons.SCHEDULE_ROUNDED
            )

        elif estado == "Dispensando":
            return (
                AZUL,
                ft.Icons.SYNC_ROUNDED
            )

        return (
            TEXTO_SECUNDARIO,
            ft.Icons.HELP_OUTLINE
        )

    def actualizar_estadisticas():

        total = len(entregas)

        completadas = sum(
            1
            for entrega in entregas
            if entrega.get("estado") == "Completada"
        )

        errores = sum(
            1
            for entrega in entregas
            if entrega.get("estado") == "Error"
        )

        pendientes = sum(
            1
            for entrega in entregas
            if entrega.get("estado") in (
                "Pendiente",
                "Dispensando"
            )
        )

        texto_total.value = str(total)
        texto_completadas.value = str(completadas)
        texto_errores.value = str(errores)
        texto_pendientes.value = str(pendientes)

    def ver_detalles(entrega):

        estado = entrega.get(
            "estado",
            ""
        )

        color_estado, icono_estado = obtener_estilo_estado(
            estado
        )

        sensor_confirmado = bool(
            entrega.get(
                "sensor_confirmado",
                False
            )
        )

        if sensor_confirmado:
            sensor_texto = "Confirmado"
        else:
            sensor_texto = "No confirmado"

        def dato(icono, titulo, valor):

            return ft.Container(
                padding=12,
                bgcolor=COLOR_CARD_2,
                border_radius=10,

                content=ft.Row(
                    spacing=12,

                    controls=[
                        ft.Icon(
                            icono,
                            color=MORADO,
                            size=20
                        ),

                        ft.Column(
                            spacing=2,

                            controls=[
                                ft.Text(
                                    titulo,
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    str(valor),
                                    size=14,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.W_500
                                )
                            ]
                        )
                    ]
                )
            )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[
                    ft.Icon(
                        icono_estado,
                        color=color_estado
                    ),

                    ft.Text(
                        f"Entrega #{entrega['id_entrega']}",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=460,

                content=ft.Column(
                    tight=True,
                    spacing=10,

                    controls=[
                        ft.Container(
                            padding=ft.Padding(
                                left=12,
                                top=6,
                                right=12,
                                bottom=6
                            ),
                            border_radius=20,
                            bgcolor=ft.Colors.with_opacity(
                                0.13,
                                color_estado
                            ),

                            content=ft.Text(
                                estado,
                                color=color_estado,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        dato(
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            "Venta",
                            f"#{entrega.get('id_venta', '-')}"
                        ),

                        dato(
                            ft.Icons.COOKIE_OUTLINED,
                            "Producto",
                            entrega.get(
                                "producto",
                                "-"
                            )
                        ),

                        dato(
                            ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                            "Dispensador",
                            entrega.get(
                                "dispensador",
                                "-"
                            )
                        ),

                        dato(
                            ft.Icons.INVENTORY_2_OUTLINED,
                            "Cantidad solicitada",
                            entrega.get(
                                "cantidad_solicitada",
                                0
                            )
                        ),

                        dato(
                            ft.Icons.DONE_ALL,
                            "Cantidad entregada",
                            entrega.get(
                                "cantidad_entregada",
                                0
                            )
                        ),

                        dato(
                            ft.Icons.SENSORS_OUTLINED,
                            "Sensor",
                            sensor_texto
                        ),

                        dato(
                            ft.Icons.PLAY_CIRCLE_OUTLINE,
                            "Fecha de inicio",
                            formatear_fecha(
                                entrega.get(
                                    "fecha_inicio"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.STOP_CIRCLE_OUTLINED,
                            "Fecha de finalización",
                            formatear_fecha(
                                entrega.get(
                                    "fecha_fin"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.ERROR_OUTLINE,
                            "Mensaje de error",
                            entrega.get(
                                "mensaje_error"
                            ) or "Sin errores"
                        )
                    ]
                )
            ),

            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e: page.pop_dialog()
                )
            ]
        )

        page.show_dialog(dialogo)

    def crear_fila(entrega):

        estado = entrega.get(
            "estado",
            ""
        )

        color_estado, icono_estado = obtener_estilo_estado(
            estado
        )

        sensor_confirmado = bool(
            entrega.get(
                "sensor_confirmado",
                False
            )
        )

        if sensor_confirmado:
            sensor_icono = ft.Icons.CHECK_CIRCLE_OUTLINE
            sensor_color = VERDE
            sensor_texto = "Sí"

        else:
            sensor_icono = ft.Icons.CANCEL_OUTLINED
            sensor_color = ROJO
            sensor_texto = "No"

        return ft.Container(
            bgcolor=COLOR_CARD,
            border_radius=12,

            border=ft.Border.all(
                1,
                COLOR_BORDE
            ),

            padding=ft.Padding(
                left=18,
                top=14,
                right=18,
                bottom=14
            ),

            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[
                    ft.Container(
                        width=90,

                        content=ft.Text(
                            f"#{entrega.get('id_venta', '-')}",
                            size=13,
                            color=MORADO,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        width=180,

                        content=ft.Text(
                            entrega.get(
                                "producto",
                                "-"
                            ),
                            size=13,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.W_500
                        )
                    ),

                    ft.Container(
                        width=170,

                        content=ft.Text(
                            entrega.get(
                                "dispensador",
                                "-"
                            ),
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    ft.Container(
                        width=110,

                        content=ft.Text(
                            str(
                                entrega.get(
                                    "cantidad_solicitada",
                                    0
                                )
                            ),
                            size=13,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        width=110,

                        content=ft.Text(
                            str(
                                entrega.get(
                                    "cantidad_entregada",
                                    0
                                )
                            ),
                            size=13,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        width=100,

                        content=ft.Row(
                            spacing=6,

                            controls=[
                                ft.Icon(
                                    sensor_icono,
                                    size=17,
                                    color=sensor_color
                                ),

                                ft.Text(
                                    sensor_texto,
                                    size=12,
                                    color=sensor_color
                                )
                            ]
                        )
                    ),

                    ft.Container(
                        width=140,

                        content=ft.Row(
                            spacing=6,

                            controls=[
                                ft.Icon(
                                    icono_estado,
                                    size=17,
                                    color=color_estado
                                ),

                                ft.Text(
                                    estado,
                                    size=12,
                                    color=color_estado,
                                    weight=ft.FontWeight.W_600
                                )
                            ]
                        )
                    ),

                    ft.Container(
                        expand=True
                    ),

                    ft.Container(
                        width=55,
                        alignment=ft.Alignment.CENTER,

                        content=ft.IconButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            icon_color=MORADO,
                            icon_size=20,
                            tooltip="Ver detalles",

                            on_click=lambda e,
                            entrega_actual=entrega: ver_detalles(
                                entrega_actual
                            )
                        )
                    )
                ]
            )
        )

    def cargar_entregas():

        lista_entregas.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for entrega in entregas:

            venta = str(
                entrega.get(
                    "id_venta",
                    ""
                )
            ).lower()

            producto = str(
                entrega.get(
                    "producto",
                    ""
                )
            ).lower()

            dispensador = str(
                entrega.get(
                    "dispensador",
                    ""
                )
            ).lower()

            estado = entrega.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in venta
                or texto in producto
                or texto in dispensador
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_estado
            ):

                lista_entregas.controls.append(
                    crear_fila(
                        entrega
                    )
                )

                encontrados += 1

        if encontrados == 0:

            lista_entregas.controls.append(
                ft.Container(
                    height=190,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,

                        controls=[
                            ft.Icon(
                                ft.Icons.LOCAL_SHIPPING_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron entregas",
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Las entregas aparecerán cuando se procesen pedidos",
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                )
            )

    def mostrar_filtros(e):

        campo_estado = ft.Dropdown(
            label="Estado",
            value=filtro_estado,

            options=[
                ft.DropdownOption(
                    key="Pendiente",
                    text="Pendiente"
                ),

                ft.DropdownOption(
                    key="Dispensando",
                    text="Dispensando"
                ),

                ft.DropdownOption(
                    key="Completada",
                    text="Completada"
                ),

                ft.DropdownOption(
                    key="Error",
                    text="Error"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_estado

            filtro_estado = campo_estado.value

            page.pop_dialog()

            cargar_entregas()
            page.update()

        def limpiar(e):

            nonlocal filtro_estado

            filtro_estado = None

            page.pop_dialog()

            cargar_entregas()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[
                    ft.Icon(
                        ft.Icons.FILTER_LIST,
                        color=MORADO
                    ),

                    ft.Text(
                        "Filtrar entregas",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=350,
                content=campo_estado
            ),

            actions=[
                ft.TextButton(
                    "Limpiar",
                    on_click=limpiar
                ),

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.ElevatedButton(
                    "Aplicar",
                    icon=ft.Icons.FILTER_ALT,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=aplicar
                )
            ]
        )

        page.show_dialog(dialogo)

    def tarjeta_resumen(
        titulo,
        valor,
        icono,
        color,
        descripcion
    ):

        return ft.Container(
            expand=True,
            height=125,
            padding=20,
            border_radius=16,
            bgcolor=COLOR_CARD,

            content=ft.Row(
                spacing=15,

                controls=[
                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=13,

                        bgcolor=ft.Colors.with_opacity(
                            0.13,
                            color
                        ),

                        alignment=ft.Alignment.CENTER,

                        content=ft.Icon(
                            icono,
                            color=color,
                            size=26
                        )
                    ),

                    ft.Column(
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,

                        controls=[
                            ft.Text(
                                titulo,
                                size=12,
                                color=TEXTO_SECUNDARIO
                            ),

                            valor,

                            ft.Text(
                                descripcion,
                                size=11,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                ]
            )
        )

    def columna(
        texto,
        width=None,
        expand=False
    ):

        return ft.Container(
            width=width,
            expand=expand,

            content=ft.Text(
                texto,
                size=10,
                color=TEXTO_SECUNDARIO,
                weight=ft.FontWeight.BOLD
            )
        )

    encabezado = ft.Container(
        bgcolor=COLOR_CARD_2,
        border_radius=10,

        padding=ft.Padding(
            left=18,
            top=12,
            right=18,
            bottom=12
        ),

        content=ft.Row(
            controls=[
                columna(
                    "VENTA",
                    90
                ),

                columna(
                    "PRODUCTO",
                    180
                ),

                columna(
                    "DISPENSADOR",
                    170
                ),

                columna(
                    "SOLICITADO",
                    110
                ),

                columna(
                    "ENTREGADO",
                    110
                ),

                columna(
                    "SENSOR",
                    100
                ),

                columna(
                    "ESTADO",
                    140
                ),

                columna(
                    "",
                    expand=True
                ),

                columna(
                    "",
                    55
                )
            ]
        )
    )

    buscador.on_change = lambda e: (
        cargar_entregas(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_entregas()

    contenido = ft.Container(
        expand=True,
        padding=30,

        bgcolor=ft.Colors.with_opacity(
            0.85,
            COLOR_FONDO
        ),

        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=22,

            controls=[
                ft.Column(
                    spacing=4,

                    controls=[
                        ft.Text(
                            "Entregas",
                            size=30,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Supervisa la entrega física de productos realizada por los dispensadores",
                            size=14,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                ),

                ft.Row(
                    spacing=15,

                    controls=[
                        tarjeta_resumen(
                            "Entregas",
                            texto_total,
                            ft.Icons.LOCAL_SHIPPING_OUTLINED,
                            MORADO,
                            "Registradas"
                        ),

                        tarjeta_resumen(
                            "Completadas",
                            texto_completadas,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Entregas correctas"
                        ),

                        tarjeta_resumen(
                            "Con error",
                            texto_errores,
                            ft.Icons.ERROR_OUTLINE,
                            ROJO,
                            "Requieren revisión"
                        ),

                        tarjeta_resumen(
                            "Pendientes",
                            texto_pendientes,
                            ft.Icons.SCHEDULE_ROUNDED,
                            AMARILLO,
                            "Pendientes o dispensando"
                        )
                    ]
                ),

                ft.Row(
                    controls=[
                        buscador,

                        ft.Container(
                            expand=True
                        ),

                        ft.OutlinedButton(
                            "Filtros",
                            icon=ft.Icons.FILTER_LIST,
                            height=45,
                            on_click=mostrar_filtros
                        )
                    ]
                ),

                encabezado,

                lista_entregas
            ]
        )
    )

    return ft.View(
        route="/entregas",
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
                    contenido
                ]
            )
        ]
    )