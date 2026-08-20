import flet as ft

from components.sidebar import sidebar
from database.movimientos import obtener_movimientos_tarjeta


# =========================================================
# COLORES
# =========================================================

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


def movimientos_view(page: ft.Page):

    movimientos = obtener_movimientos_tarjeta()

    filtro_tipo = None

    # =========================================================
    # CONTADORES
    # =========================================================

    texto_total = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_recargas = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_compras = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_monto = ft.Text(
        "$0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar cliente, UID o descripción...",
        prefix_icon=ft.Icons.SEARCH,
        width=400,
        height=45,
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
        cursor_color=ROSA,
        color=TEXTO_PRINCIPAL,
        border_radius=12
    )

    lista_movimientos = ft.Column(
        spacing=10
    )

    # =========================================================
    # FORMATEAR DINERO
    # =========================================================

    def dinero(valor):

        try:
            numero = float(valor or 0)

            return (
                f"${numero:,.0f}"
                .replace(",", ".")
            )

        except (ValueError, TypeError):
            return "$0"

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        total = len(movimientos)

        recargas = sum(
            1
            for m in movimientos
            if m.get("tipo") == "Recarga"
        )

        compras = sum(
            1
            for m in movimientos
            if m.get("tipo") == "Compra"
        )

        monto_total = sum(
            abs(float(m.get("monto") or 0))
            for m in movimientos
        )

        texto_total.value = str(total)
        texto_recargas.value = str(recargas)
        texto_compras.value = str(compras)

        texto_monto.value = dinero(
            monto_total
        )

    # =========================================================
    # COLOR / ICONO DEL TIPO
    # =========================================================

    def obtener_estilo_tipo(tipo):

        if tipo == "Recarga":

            return (
                VERDE,
                ft.Icons.ADD_CIRCLE_OUTLINE
            )

        elif tipo == "Compra":

            return (
                ROSA,
                ft.Icons.SHOPPING_CART_OUTLINED
            )

        elif tipo in ("Devolución", "Devolucion"):

            return (
                AZUL,
                ft.Icons.REPLAY
            )

        elif tipo == "Ajuste":

            return (
                AMARILLO,
                ft.Icons.TUNE
            )

        return (
            TEXTO_SECUNDARIO,
            ft.Icons.SWAP_HORIZ
        )

    # =========================================================
    # DETALLE
    # =========================================================

    def ver_detalles(movimiento):

        tipo = movimiento.get(
            "tipo",
            ""
        )

        # Mostrar correctamente "Devolución"
        if tipo == "Devolucion":
            tipo_mostrar = "Devolución"
        else:
            tipo_mostrar = tipo

        color_tipo, icono_tipo = (
            obtener_estilo_tipo(tipo)
        )

        fecha = movimiento.get(
            "fecha"
        )

        if hasattr(fecha, "strftime"):

            fecha_texto = fecha.strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        else:

            fecha_texto = str(
                fecha or ""
            )

        def dato(
            icono,
            titulo,
            valor
        ):

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
                        icono_tipo,
                        color=color_tipo
                    ),

                    ft.Text(
                        f"Movimiento #{movimiento['id_movimiento']}",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=440,

                content=ft.Column(
                    tight=True,
                    spacing=12,

                    controls=[

                        # TIPO
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
                                color_tipo
                            ),

                            content=ft.Text(
                                tipo_mostrar,
                                color=color_tipo,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        dato(
                            ft.Icons.PERSON_OUTLINE,
                            "Cliente",
                            movimiento.get(
                                "cliente",
                                "Sin cliente"
                            )
                        ),

                        dato(
                            ft.Icons.NFC,
                            "UID de tarjeta",
                            movimiento.get(
                                "uid",
                                ""
                            )
                        ),

                        dato(
                            ft.Icons.ATTACH_MONEY,
                            "Monto",
                            dinero(
                                movimiento.get(
                                    "monto"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            "Saldo anterior",
                            dinero(
                                movimiento.get(
                                    "saldo_anterior"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.ACCOUNT_BALANCE_WALLET,
                            "Saldo nuevo",
                            dinero(
                                movimiento.get(
                                    "saldo_nuevo"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.ACCESS_TIME,
                            "Fecha",
                            fecha_texto
                        ),

                        dato(
                            ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                            "Usuario responsable",
                            movimiento.get(
                                "usuario"
                            ) or "Sistema"
                        ),

                        dato(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            "Descripción",
                            movimiento.get(
                                "descripcion"
                            ) or "Sin descripción"
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

    # =========================================================
    # CREAR FILA
    # =========================================================

    def crear_fila(movimiento):

        tipo = movimiento.get(
            "tipo",
            ""
        )

        # Mostrar correctamente "Devolución"
        if tipo == "Devolucion":
            tipo_mostrar = "Devolución"
        else:
            tipo_mostrar = tipo

        color_tipo, icono_tipo = (
            obtener_estilo_tipo(tipo)
        )

        fecha = movimiento.get(
            "fecha"
        )

        if hasattr(fecha, "strftime"):

            fecha_texto = fecha.strftime(
                "%d/%m/%Y %H:%M"
            )

        else:

            fecha_texto = str(
                fecha or ""
            )

        monto = float(
            movimiento.get(
                "monto"
            ) or 0
        )

        # =====================================================
        # SIGNO VISUAL DEL MONTO
        # =====================================================

        if tipo in (
            "Recarga",
            "Devolucion",
            "Devolución"
        ):

            monto_texto = (
                "+"
                + dinero(monto)
            )

        elif tipo == "Compra":

            monto_texto = (
                "-"
                + dinero(abs(monto))
            )

        else:

            monto_texto = dinero(
                monto
            )

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
                right=12,
                bottom=14
            ),

            content=ft.Row(
                spacing=0,

                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    # =================================================
                    # FECHA
                    # =================================================

                    ft.Container(
                        width=160,

                        content=ft.Text(
                            fecha_texto,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =================================================
                    # CLIENTE
                    # =================================================

                    ft.Container(
                        width=210,

                        content=ft.Column(
                            spacing=2,

                            controls=[
                                ft.Text(
                                    movimiento.get(
                                        "cliente",
                                        "Sin cliente"
                                    ),
                                    size=13,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    movimiento.get(
                                        "uid",
                                        ""
                                    ),
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # TIPO
                    # =================================================

                    ft.Container(
                        width=150,

                        content=ft.Row(
                            spacing=7,

                            controls=[
                                ft.Icon(
                                    icono_tipo,
                                    size=17,
                                    color=color_tipo
                                ),

                                ft.Text(
                                    tipo_mostrar,
                                    size=12,
                                    color=color_tipo,
                                    weight=ft.FontWeight.W_600
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # MONTO
                    # =================================================

                    ft.Container(
                        width=130,

                        content=ft.Text(
                            monto_texto,
                            size=13,
                            color=color_tipo,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    # =================================================
                    # SALDO ANTERIOR
                    # =================================================

                    ft.Container(
                        width=150,

                        content=ft.Text(
                            dinero(
                                movimiento.get(
                                    "saldo_anterior"
                                )
                            ),
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =================================================
                    # SALDO NUEVO
                    # =================================================

                    ft.Container(
                        width=140,

                        content=ft.Text(
                            dinero(
                                movimiento.get(
                                    "saldo_nuevo"
                                )
                            ),
                            size=13,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        expand=True
                    ),

                    # =================================================
                    # ACCIONES
                    # =================================================

                    ft.Container(
                        width=60,
                        alignment=ft.Alignment.CENTER,

                        content=ft.IconButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            icon_size=20,
                            icon_color=MORADO,
                            width=40,
                            height=40,
                            padding=0,
                            tooltip="Ver detalles",

                            on_click=lambda e, m=movimiento: (
                                ver_detalles(m)
                            )
                        )
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR MOVIMIENTOS
    # =========================================================

    def cargar_movimientos():

        lista_movimientos.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for movimiento in movimientos:

            cliente = str(
                movimiento.get(
                    "cliente",
                    ""
                )
            ).lower()

            uid = str(
                movimiento.get(
                    "uid",
                    ""
                )
            ).lower()

            descripcion = str(
                movimiento.get(
                    "descripcion",
                    ""
                ) or ""
            ).lower()

            tipo = movimiento.get(
                "tipo",
                ""
            )

            coincide_busqueda = (
                texto in cliente
                or texto in uid
                or texto in descripcion
            )

            coincide_tipo = (
                filtro_tipo is None
                or tipo == filtro_tipo
            )

            if (
                coincide_busqueda
                and coincide_tipo
            ):

                lista_movimientos.controls.append(
                    crear_fila(
                        movimiento
                    )
                )

                encontrados += 1

        # =====================================================
        # SIN RESULTADOS
        # =====================================================

        if encontrados == 0:

            lista_movimientos.controls.append(

                ft.Container(
                    height=190,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),

                        spacing=8,

                        controls=[

                            ft.Icon(
                                ft.Icons.RECEIPT_LONG_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron movimientos",
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Prueba con otro término o filtro",
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                )
            )

    # =========================================================
    # FILTROS
    # =========================================================

    def mostrar_filtros(e):

        tipo_dropdown = ft.Dropdown(
            label="Tipo de movimiento",
            value=filtro_tipo,

            options=[

                ft.DropdownOption(
                    key="Recarga",
                    text="Recarga"
                ),

                ft.DropdownOption(
                    key="Compra",
                    text="Compra"
                ),

                ft.DropdownOption(
                    key="Devolucion",
                    text="Devolución"
                ),

                ft.DropdownOption(
                    key="Ajuste",
                    text="Ajuste"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_tipo

            filtro_tipo = (
                tipo_dropdown.value
            )

            page.pop_dialog()

            cargar_movimientos()
            page.update()

        def limpiar(e):

            nonlocal filtro_tipo

            filtro_tipo = None

            page.pop_dialog()

            cargar_movimientos()
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
                        "Filtrar movimientos",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=380,
                content=tipo_dropdown
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

    # =========================================================
    # TARJETAS DE RESUMEN
    # =========================================================

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

                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),

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

    # =========================================================
    # ENCABEZADO DE LA TABLA
    # =========================================================

    encabezado = ft.Container(
        bgcolor=COLOR_CARD_2,
        border_radius=10,

        padding=ft.Padding(
            left=18,
            top=12,
            right=12,
            bottom=12
        ),

        content=ft.Row(
            spacing=0,

            controls=[

                ft.Container(
                    width=160,

                    content=ft.Text(
                        "FECHA",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=210,

                    content=ft.Text(
                        "CLIENTE / TARJETA",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=150,

                    content=ft.Text(
                        "TIPO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,

                    content=ft.Text(
                        "MONTO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=150,

                    content=ft.Text(
                        "SALDO ANTERIOR",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=140,

                    content=ft.Text(
                        "SALDO NUEVO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    expand=True
                ),

                ft.Container(
                    width=60,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Text(
                        "ACCIONES",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                )
            ]
        )
    )

    # =========================================================
    # EVENTOS
    # =========================================================

    buscador.on_change = lambda e: (
        cargar_movimientos(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_movimientos()

    # =========================================================
    # CONTENIDO PRINCIPAL
    # =========================================================

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

                # =================================================
                # TÍTULO
                # =================================================

                ft.Column(
                    spacing=4,

                    controls=[

                        ft.Text(
                            "Movimientos de tarjetas",
                            size=30,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Consulta el historial de operaciones realizadas con tarjetas NFC",
                            size=14,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                ),

                # =================================================
                # RESUMEN
                # =================================================

                ft.Row(
                    spacing=15,

                    controls=[

                        tarjeta_resumen(
                            "Movimientos",
                            texto_total,
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            MORADO,
                            "Operaciones registradas"
                        ),

                        tarjeta_resumen(
                            "Recargas",
                            texto_recargas,
                            ft.Icons.ADD_CARD,
                            VERDE,
                            "Recargas realizadas"
                        ),

                        tarjeta_resumen(
                            "Compras",
                            texto_compras,
                            ft.Icons.SHOPPING_CART_OUTLINED,
                            ROSA,
                            "Pagos realizados"
                        ),

                        tarjeta_resumen(
                            "Monto movido",
                            texto_monto,
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            AMARILLO,
                            "Total de operaciones"
                        )
                    ]
                ),

                # =================================================
                # BUSCADOR Y FILTROS
                # =================================================

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

                # =================================================
                # ENCABEZADO
                # =================================================

                encabezado,

                # =================================================
                # LISTA
                # =================================================

                lista_movimientos
            ]
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/movimientos",
        padding=0,
        spacing=0,
        bgcolor=ft.Colors.TRANSPARENT,

        controls=[

            ft.Row(
                expand=True,
                spacing=0,

                vertical_alignment=(
                    ft.CrossAxisAlignment.STRETCH
                ),

                controls=[

                    sidebar(page),

                    contenido
                ]
            )
        ]
    )