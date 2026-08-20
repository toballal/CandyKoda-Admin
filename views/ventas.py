import flet as ft

from database.ventas import get_ventas
from database.ventas import get_detalle_venta

from components.sidebar import sidebar
from components.detalle_venta import detalle_venta


# =========================================================
# COLORES
# =========================================================

MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
ROJO = "#FF4FA3"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#CACAD4"


def historial_ventas_view(page: ft.Page):

    # =========================================================
    # USUARIO ACTUAL
    # =========================================================

    usuario_actual = getattr(page, "usuario_actual", None) or {}

    nombre_usuario = usuario_actual.get(
        "nombre",
        "Administrador"
    )

    rol_usuario = usuario_actual.get(
        "rol",
        "Sin rol"
    )

    # =========================================================
    # OBTENER VENTAS
    # =========================================================

    ventas_get = get_ventas()

    ventas = []

    for venta in ventas_get:

        ventas.append({
            "id": venta[0],
            "cliente": venta[1],
            "uid": venta[2],
            "total": venta[3],
            "estado": venta[4],
            "fecha": venta[5]
        })

    # =========================================================
    # CONTENEDOR DE VENTAS
    # =========================================================

    lista_ventas = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    pagina_actual = 0
    por_pagina = 7

    criterio_orden = "recientes"

    ventas_filtradas = list(ventas)

    # =========================================================
    # PAGINACIÓN
    # =========================================================

    texto_pagina = ft.Text(
        "Página 1 de 1",
        size=12,
        color=TEXTO_SECUNDARIO
    )

    boton_anterior = ft.IconButton(
        icon=ft.Icons.CHEVRON_LEFT,
        icon_color=MORADO,
        tooltip="Página anterior"
    )

    boton_siguiente = ft.IconButton(
        icon=ft.Icons.CHEVRON_RIGHT,
        icon_color=MORADO,
        tooltip="Página siguiente"
    )

    # =========================================================
    # MENSAJE
    # =========================================================

    mensaje = ft.Text(
        "",
        size=14
    )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    total_ventas = sum(
        float(venta["total"] or 0)
        for venta in ventas
        if venta["estado"] == "Completada"
    )

    cantidad_ventas = len([
        venta
        for venta in ventas
        if venta["estado"] == "Completada"
    ])

    # =========================================================
    # MOSTRAR UNA VENTA
    # =========================================================

    def mostrar_venta(venta):

        if venta["estado"] == "Completada":

            color_estado = VERDE
            icono_estado = ft.Icons.CHECK_CIRCLE

        else:

            color_estado = ROSA
            icono_estado = ft.Icons.CANCEL

        fecha = venta["fecha"]

        if hasattr(fecha, "strftime"):

            fecha_texto = fecha.strftime("%d/%m/%Y")
            hora_texto = fecha.strftime("%H:%M")

        else:

            fecha_texto = str(fecha)
            hora_texto = ""

        tarjeta = ft.Container(

            padding=ft.Padding(
                left=18,
                top=14,
                right=18,
                bottom=14
            ),

            bgcolor=COLOR_CARD,

            border_radius=12,

            border=ft.Border.all(
                1,
                COLOR_BORDE
            ),

            content=ft.Row(

                alignment=ft.MainAxisAlignment.START,

                vertical_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[

                    # =================================================
                    # ID DE VENTA
                    # =================================================

                    ft.Container(
                        width=80,

                        content=ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Venta",
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    f'#{venta["id"]}',
                                    size=17,
                                    color=MORADO,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # FECHA
                    # =================================================

                    ft.Container(
                        width=130,

                        content=ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Fecha",
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    fecha_texto,
                                    size=14,
                                    color=TEXTO_PRINCIPAL
                                ),

                                ft.Text(
                                    hora_texto,
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # CLIENTE
                    # =================================================

                    ft.Container(
                        width=170,

                        content=ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Cliente",
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    venta["cliente"],
                                    size=14,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    f'Tarjeta: {venta["uid"]}',
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # MÉTODO DE PAGO
                    # =================================================

                    ft.Container(
                        width=130,

                        content=ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Pago",
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Row(

                                    spacing=5,

                                    controls=[

                                        ft.Icon(
                                            ft.Icons.PAYMENT,
                                            size=17,
                                            color=MORADO
                                        ),

                                        ft.Text(
                                            "Tarjeta NFC",
                                            size=13,
                                            color=TEXTO_PRINCIPAL
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # TOTAL
                    # =================================================

                    ft.Container(
                        width=120,

                        content=ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Total",
                                    size=10,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    f'${float(venta["total"] or 0):,.0f}',
                                    size=18,
                                    color=ROSA,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        )
                    ),

                    # =================================================
                    # ESTADO
                    # =================================================

                    ft.Container(

                        width=120,

                        padding=8,

                        bgcolor=ft.Colors.with_opacity(
                            0.09,
                            color_estado
                        ),

                        border_radius=8,

                        content=ft.Row(

                            spacing=5,

                            controls=[

                                ft.Icon(
                                    icono_estado,
                                    size=17,
                                    color=color_estado
                                ),

                                ft.Text(
                                    venta["estado"],
                                    size=12,
                                    color=color_estado,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        )
                    ),

                    # ESPACIO
                    ft.Container(
                        expand=True
                    ),

                    # =================================================
                    # BOTÓN VER
                    # =================================================

                    ft.IconButton(

                        icon=ft.Icons.VISIBILITY_OUTLINED,

                        icon_color=MORADO,

                        icon_size=20,

                        bgcolor=ft.Colors.with_opacity(
                            0.15,
                            MORADO
                        ),

                        hover_color=ft.Colors.with_opacity(
                            0.25,
                            MORADO
                        ),

                        tooltip="Ver venta",

                        on_click=lambda e, v=venta:
                            ver_detalle(v)
                    )
                ]
            )
        )

        lista_ventas.controls.append(tarjeta)

    # =========================================================
    # MOSTRAR VENTAS
    # =========================================================

    def mostrar_ventas(lista):

        nonlocal pagina_actual
        nonlocal ventas_filtradas

        lista_ventas.controls.clear()

        ventas_filtradas = list(lista)

        # =====================================================
        # ORDENAMIENTO
        # =====================================================

        if criterio_orden == "mayor_total":

            ventas_filtradas.sort(
                key=lambda venta: float(
                    venta["total"] or 0
                ),
                reverse=True
            )

        elif criterio_orden == "menor_total":

            ventas_filtradas.sort(
                key=lambda venta: float(
                    venta["total"] or 0
                )
            )

        else:

            ventas_filtradas.sort(
                key=lambda venta: str(
                    venta["fecha"]
                ),
                reverse=(
                    criterio_orden == "recientes"
                )
            )

        # =====================================================
        # PAGINACIÓN
        # =====================================================

        total_paginas = max(
            1,
            (
                len(ventas_filtradas)
                + por_pagina
                - 1
            ) // por_pagina
        )

        pagina_actual = min(
            pagina_actual,
            total_paginas - 1
        )

        inicio = pagina_actual * por_pagina

        texto_pagina.value = (
            f"Página {pagina_actual + 1} "
            f"de {total_paginas} · "
            f"{len(ventas_filtradas)} ventas"
        )

        boton_anterior.disabled = (
            pagina_actual == 0
        )

        boton_siguiente.disabled = (
            pagina_actual >= total_paginas - 1
        )

        # =====================================================
        # SIN RESULTADOS
        # =====================================================

        if len(ventas_filtradas) == 0:

            lista_ventas.controls.append(

                ft.Container(

                    padding=40,

                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),

                        spacing=8,

                        controls=[

                            ft.Icon(
                                ft.Icons.RECEIPT_LONG_OUTLINED,
                                size=60,
                                color=MORADO
                            ),

                            ft.Text(
                                "No se encontraron ventas",
                                size=18,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Prueba con otro término de búsqueda",
                                size=13,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                )
            )

        else:

            for venta in ventas_filtradas[
                inicio:inicio + por_pagina
            ]:

                mostrar_venta(venta)

    # =========================================================
    # CAMBIAR PÁGINA
    # =========================================================

    def cambiar_pagina(delta):

        nonlocal pagina_actual

        pagina_actual = max(
            0,
            pagina_actual + delta
        )

        mostrar_ventas(ventas_filtradas)

        page.update()

    # =========================================================
    # CAMBIAR ORDEN
    # =========================================================

    def cambiar_orden(e):

        nonlocal criterio_orden
        nonlocal pagina_actual

        criterio_orden = e.control.value

        pagina_actual = 0

        mostrar_ventas(ventas_filtradas)

        page.update()

    boton_anterior.on_click = (
        lambda e: cambiar_pagina(-1)
    )

    boton_siguiente.on_click = (
        lambda e: cambiar_pagina(1)
    )

    # =========================================================
    # VER DETALLE
    # =========================================================

    def ver_detalle(venta):

        detalles = get_detalle_venta(
            venta["id"]
        )

        dialogo = ft.AlertDialog(

            modal=True,

            bgcolor=COLOR_CARD,

            content=detalle_venta(
                venta,
                detalles
            ),

            actions=[

                ft.TextButton(

                    "Cerrar",

                    icon=ft.Icons.CLOSE,

                    style=ft.ButtonStyle(

                        color=MORADO,

                        bgcolor=ft.Colors.with_opacity(
                            0.13,
                            MORADO
                        )
                    ),

                    on_click=lambda e:
                        cerrar_dialogo(dialogo)
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # CERRAR DIÁLOGO
    # =========================================================

    def cerrar_dialogo(dialogo):

        dialogo.open = False

        page.update()

    # =========================================================
    # BUSCAR VENTA
    # =========================================================

    def buscar_venta(e):

        nonlocal pagina_actual

        pagina_actual = 0

        texto = (
            e.control.value or ""
        ).lower().strip()

        if texto == "":

            mostrar_ventas(ventas)

            page.update()

            return

        resultados = []

        for venta in ventas:

            fecha = venta["fecha"]

            if hasattr(fecha, "strftime"):

                fecha_texto = fecha.strftime(
                    "%d/%m/%Y"
                )

            else:

                fecha_texto = str(fecha)

            cliente = str(
                venta["cliente"] or ""
            ).lower()

            uid = str(
                venta["uid"] or ""
            ).lower()

            estado = str(
                venta["estado"] or ""
            ).lower()

            if (
                texto in str(
                    venta["id"]
                ).lower()

                or texto in cliente

                or texto in uid

                or texto in fecha_texto.lower()

                or texto in estado
            ):

                resultados.append(venta)

        mostrar_ventas(resultados)

        page.update()

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(

        hint_text=(
            "Buscar por cliente, número de venta, "
            "tarjeta o fecha..."
        ),

        prefix=ft.Icon(
            ft.Icons.SEARCH,
            color=MORADO,
            size=20
        ),

        width=480,

        height=45,

        text_size=13,

        bgcolor=COLOR_CARD,

        border_color=COLOR_BORDE,

        focused_border_color=MORADO,

        cursor_color=ROSA,

        color=TEXTO_PRINCIPAL,

        hint_style=ft.TextStyle(
            color=TEXTO_SECUNDARIO,
            size=13
        ),

        border_radius=10,

        on_change=buscar_venta
    )

    # =========================================================
    # TARJETA DE VENTAS
    # =========================================================

    tarjeta_ventas = ft.Container(

        width=230,

        height=105,

        padding=18,

        bgcolor=COLOR_CARD,

        border_radius=14,

        border=ft.Border.all(
            1,
            COLOR_BORDE
        ),

        content=ft.Row(

            spacing=12,

            controls=[

                ft.Container(

                    width=50,

                    height=50,

                    bgcolor=ft.Colors.with_opacity(
                        0.13,
                        MORADO
                    ),

                    border_radius=12,

                    alignment=ft.Alignment.CENTER,

                    content=ft.Icon(
                        ft.Icons.RECEIPT_LONG,
                        color=MORADO,
                        size=28
                    )
                ),

                ft.Column(

                    spacing=2,

                    alignment=ft.MainAxisAlignment.CENTER,

                    controls=[

                        ft.Text(
                            "Ventas realizadas",
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            str(cantidad_ventas),
                            size=24,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                )
            ]
        )
    )

    # =========================================================
    # TARJETA DINERO
    # =========================================================

    tarjeta_dinero = ft.Container(

        width=230,

        height=105,

        padding=18,

        bgcolor=COLOR_CARD,

        border_radius=14,

        border=ft.Border.all(
            1,
            COLOR_BORDE
        ),

        content=ft.Row(

            spacing=12,

            controls=[

                ft.Container(

                    width=50,

                    height=50,

                    bgcolor=ft.Colors.with_opacity(
                        0.13,
                        ROSA
                    ),

                    border_radius=12,

                    alignment=ft.Alignment.CENTER,

                    content=ft.Icon(
                        ft.Icons.ATTACH_MONEY,
                        color=ROSA,
                        size=28
                    )
                ),

                ft.Column(

                    spacing=2,

                    alignment=ft.MainAxisAlignment.CENTER,

                    controls=[

                        ft.Text(
                            "Total vendido",
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            f"${total_ventas:,.0f}",
                            size=21,
                            color=ROSA,
                            weight=ft.FontWeight.BOLD
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

        padding=ft.Padding(
            left=18,
            top=13,
            right=18,
            bottom=13
        ),

        bgcolor=COLOR_CARD_2,

        border_radius=10,

        content=ft.Row(

            controls=[

                ft.Container(
                    width=80,

                    content=ft.Text(
                        "Venta",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,

                    content=ft.Text(
                        "Fecha",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=170,

                    content=ft.Text(
                        "Cliente",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,

                    content=ft.Text(
                        "Pago",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=120,

                    content=ft.Text(
                        "Total",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=120,

                    content=ft.Text(
                        "Estado",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    expand=True
                ),

                ft.Container(
                    width=40,

                    content=ft.Text(
                        "Acción",
                        size=10,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                )
            ]
        )
    )

    # =========================================================
    # CARGAR VENTAS
    # =========================================================

    mostrar_ventas(ventas)

    # =========================================================
    # CONTENIDO PRINCIPAL
    # =========================================================

    contenido = ft.Container(

        expand=True,

        padding=30,

        content=ft.Column(

            expand=True,

            spacing=22,

            controls=[

                # =================================================
                # CABECERA
                # =================================================

                ft.Row(

                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    controls=[

                        ft.Column(

                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Historial de ventas",
                                    size=30,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "Consulta y revisa las ventas realizadas",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.Container(

                            padding=ft.Padding(
                                left=14,
                                top=8,
                                right=14,
                                bottom=8
                            ),

                            bgcolor=COLOR_CARD,

                            border=ft.Border.all(
                                1,
                                COLOR_BORDE
                            ),

                            border_radius=12,

                            content=ft.Row(

                                spacing=7,

                                controls=[

                                    ft.Icon(
                                        ft.Icons.ADMIN_PANEL_SETTINGS,
                                        color=ROSA
                                    ),

                                    ft.Column(

                                        spacing=0,

                                        controls=[

                                            ft.Text(
                                                nombre_usuario,
                                                size=13,
                                                color=TEXTO_PRINCIPAL,
                                                weight=ft.FontWeight.BOLD
                                            ),

                                            ft.Text(
                                                rol_usuario,
                                                size=11,
                                                color=TEXTO_SECUNDARIO
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    ]
                ),

                # =================================================
                # ESTADÍSTICAS
                # =================================================

                ft.Row(

                    spacing=15,

                    controls=[
                        tarjeta_ventas,
                        tarjeta_dinero
                    ]
                ),

                # =================================================
                # BUSCADOR Y ORDEN
                # =================================================

                ft.Row(

                    controls=[

                        buscador,

                        ft.Container(
                            expand=True
                        ),

                        ft.Dropdown(

                            value="recientes",

                            width=180,

                            height=45,

                            text_size=12,

                            bgcolor=COLOR_CARD,

                            border_color=COLOR_BORDE,

                            on_select=cambiar_orden,

                            options=[

                                ft.DropdownOption(
                                    key="recientes",
                                    text="Más recientes"
                                ),

                                ft.DropdownOption(
                                    key="antiguos",
                                    text="Más antiguas"
                                ),

                                ft.DropdownOption(
                                    key="mayor_total",
                                    text="Mayor total"
                                ),

                                ft.DropdownOption(
                                    key="menor_total",
                                    text="Menor total"
                                )
                            ]
                        )
                    ],

                    alignment=ft.MainAxisAlignment.START
                ),

                # =================================================
                # TABLA
                # =================================================

                ft.Container(

                    expand=True,

                    bgcolor=ft.Colors.TRANSPARENT,

                    padding=0,

                    content=ft.Column(

                        expand=True,

                        spacing=10,

                        controls=[

                            encabezado,

                            ft.Container(
                                expand=True,
                                content=lista_ventas
                            ),

                            mensaje,

                            ft.Row(

                                alignment=(
                                    ft.MainAxisAlignment.END
                                ),

                                controls=[
                                    boton_anterior,
                                    texto_pagina,
                                    boton_siguiente
                                ]
                            )
                        ]
                    )
                )
            ]
        )
    )

    # =========================================================
    # SIDEBAR
    # =========================================================

    menu_lateral = sidebar(page)

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(

        route="/ventas",

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

                    menu_lateral,

                    ft.Container(

                        expand=True,

                        bgcolor=ft.Colors.with_opacity(
                            0.85,
                            COLOR_FONDO
                        ),

                        content=contenido
                    )
                ]
            )
        ]
    )