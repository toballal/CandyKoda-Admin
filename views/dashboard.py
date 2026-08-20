import flet as ft
from datetime import datetime

from database.ventas import get_ventas_resumen
from database.dispensadores import get_dispensadores

from components.sidebar import sidebar
from components.graficos import (
    grafico_ventas,
    grafico_productos,
    grafico_logs
)

from database.logs import (
    obtener_logs_recientes,
    obtener_resumen_logs
)

from database.dashboard import (
    get_resumen_dashboard,
    get_ventas_ultimos_7_dias,
    get_productos_mas_vendidos,
    get_alertas_stock
)
from services.autorizacion import puede_acceder


def dashboard_view(page: ft.Page):

    usuario_actual = getattr(page, "usuario_actual", None) or {}

    nombre_usuario = usuario_actual.get(
        "nombre",
        "Administrador"
    )

    rol_usuario = usuario_actual.get(
        "rol",
        "Sin rol"
    )

    puede_ver_ventas = puede_acceder(usuario_actual, "/ventas")
    puede_ver_productos = puede_acceder(usuario_actual, "/productos")
    puede_ver_inventario = puede_acceder(usuario_actual, "/inventario")
    puede_ver_logs = puede_acceder(usuario_actual, "/logs")
    puede_ver_dispensadores = puede_acceder(
        usuario_actual,
        "/dispensadores"
    )

    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # =========================
    # COLORES
    # =========================

    COLOR_CARD = "#171722"
    COLOR_CARD_2 = "#202031"

    MORADO = "#9B59FF"
    ROSA = "#FF4FA3"
    AMARILLO = "#FFC107"
    VERDE = "#9B59FF"
    ROJO = "#FF4FA3"

    TEXTO_SECUNDARIO = "#C3C3CE"

    # =========================
    # NAVEGACIÓN
    # =========================

    def navegar(ruta):
        page.go(ruta)

    def cerrar_sesion(e):
        page.go("/")

    # =========================
    # OPCIÓN DEL MENÚ
    # =========================

    def opcion_menu(icono, texto, ruta):

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icono,
                        size=20,
                        color="#FFFFFF"
                    ),

                    ft.Text(
                        texto,
                        size=15,
                        color="#FFFFFF",
                        weight=ft.FontWeight.W_500
                    )
                ],
                spacing=15
            ),

            padding=ft.Padding.symmetric(
                horizontal=18,
                vertical=14
            ),

            border_radius=10,
            ink=True,

            on_click=lambda e: navegar(ruta)
        )

    # =========================
    # TARJETAS ESTADÍSTICAS
    # =========================

    resumen = {
        "ventas_hoy": 0,
        "ingresos_hoy": 0,
        "productos": 0,
        "stock_bajo": 0
    }
    if (
        puede_ver_ventas
        or puede_ver_productos
        or puede_ver_inventario
    ):
        resumen = get_resumen_dashboard(
            incluir_ventas=puede_ver_ventas,
            incluir_productos=puede_ver_productos,
            incluir_stock=puede_ver_inventario,
        )

    def tarjeta_estadistica(
        titulo,
        valor,
        icono,
        color,
        descripcion
    ):

        return ft.Container(
            expand=True,
            height=150,

            padding=20,

            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=[
                    COLOR_CARD,
                    ft.Colors.with_opacity(
                        0.07,
                        color
                    )
                ]
            ),

            border=ft.Border.all(
                1,
                ft.Colors.with_opacity(
                    0.19,
                    color
                )
            ),

            border_radius=20,

            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(
                    0.19,
                    "#000000"
                ),
                offset=ft.Offset(0, 6)
            ),

            content=ft.Column(
                controls=[

                    ft.Row(
                        controls=[

                            ft.Container(
                                width=45,
                                height=45,

                                bgcolor=ft.Colors.with_opacity(
                                    0.13,
                                    color
                                ),

                                border_radius=12,

                                alignment=ft.Alignment.CENTER,

                                content=ft.Icon(
                                    icono,
                                    color=color,
                                    size=24
                                )
                            ),

                            ft.Container(
                                expand=True
                            ),

                            ft.Container(
                                padding=ft.Padding.symmetric(
                                    horizontal=9,
                                    vertical=4
                                ),

                                bgcolor=ft.Colors.with_opacity(
                                    0.09,
                                    color
                                ),

                                border_radius=20,

                                content=ft.Text(
                                    descripcion,
                                    size=10,
                                    color=color,
                                    weight=ft.FontWeight.BOLD
                                )
                            )
                        ]
                    ),

                    ft.Text(
                        valor,
                        size=27,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF"
                    ),

                    ft.Row(
                        controls=[
                            ft.Text(
                                titulo,
                                size=14,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Container(
                                expand=True
                            )
                        ]
                    )
                ],

                spacing=7
            )
        )

    estadisticas = ft.Row(
        controls=[
            *([tarjeta_estadistica(
                "Ventas de hoy",
                str(resumen["ventas_hoy"]),
                ft.Icons.SHOPPING_BAG_ROUNDED,
                MORADO,
                "Completadas"
            )] if puede_ver_ventas else []),

            *([tarjeta_estadistica(
                "Ingresos de hoy",
                f"${resumen['ingresos_hoy']:,.0f}",
                ft.Icons.ATTACH_MONEY_ROUNDED,
                VERDE,
                "Total"
            )] if puede_ver_ventas else []),

            *([tarjeta_estadistica(
                "Productos",
                str(resumen["productos"]),
                ft.Icons.COOKIE_ROUNDED,
                ROSA,
                "Disponibles"
            )] if puede_ver_productos else []),

            *([tarjeta_estadistica(
                "Stock bajo",
                str(resumen["stock_bajo"]),
                ft.Icons.WARNING_AMBER_ROUNDED,
                AMARILLO,
                "Revisar"
            )] if puede_ver_inventario else [])
        ],

        spacing=18
    )

    # =========================
    # VENTAS RECIENTES
    # =========================

    ventas = get_ventas_resumen() if puede_ver_ventas else []

    filas_ventas = []

    for venta in ventas:

        id_venta = venta["id_venta"]
        cliente = venta["cliente"]
        total = venta["total"]
        estado = venta["estado"]
        fecha = venta["fecha"]

        fecha_form = fecha.strftime(
            "%d/%m/%Y %H:%M"
        )

        if estado == "Completada":
            color_estado = VERDE
        else:
            color_estado = ROJO

        fila = ft.Container(

            padding=ft.Padding.symmetric(
                vertical=12
            ),

            border=ft.Border(
                bottom=ft.BorderSide(
                    width=1,
                    color="#292930"
                )
            ),

            content=ft.Row(
                controls=[

                    ft.Text(
                        f"#{id_venta}",
                        width=80,
                        color="#FFFFFF"
                    ),

                    ft.Text(
                        cliente,
                        expand=True,
                        color="#FFFFFF"
                    ),

                    ft.Text(
                        f"${total:,.0f}",
                        width=100,
                        color="#FFFFFF",
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        width=110,

                        padding=ft.Padding.symmetric(
                            horizontal=10,
                            vertical=5
                        ),

                        bgcolor=ft.Colors.with_opacity(
                            0.13,
                            color_estado
                        ),

                        border_radius=20,

                        content=ft.Text(
                            estado,
                            size=12,
                            color=color_estado,
                            text_align=ft.TextAlign.CENTER
                        )
                    ),

                    ft.Text(
                        fecha_form,
                        width=75,
                        color=TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.RIGHT
                    )
                ]
            )
        )

        filas_ventas.append(fila)

    # =========================
    # CONTENEDOR VENTAS
    # =========================

    ventas_recientes = ft.Container(

        expand=2,

        bgcolor=COLOR_CARD,

        border=ft.Border.all(
            1,
            "#34344A"
        ),

        border_radius=18,

        padding=22,

        content=ft.Column(
            controls=[

                ft.Row(
                    controls=[

                        ft.Column(
                            controls=[

                                ft.Text(
                                    "Ventas recientes",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                ),

                                ft.Text(
                                    "Últimas 5 operaciones realizadas",
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ],

                            spacing=3
                        ),

                        ft.Container(
                            expand=True
                        ),

                        ft.TextButton(
                            "Ver todas",
                            on_click=lambda e: navegar(
                                "/ventas"
                            )
                        )
                    ]
                ),

                ft.Container(
                    height=15
                ),

                ft.Row(
                    controls=[

                        ft.Text(
                            "ID",
                            width=80,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            "Cliente",
                            expand=True,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            "Total",
                            width=100,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            "Estado",
                            width=110,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        ),

                        ft.Text(
                            "Fecha",
                            width=70,
                            size=12,
                            color=TEXTO_SECUNDARIO,
                            text_align=ft.TextAlign.RIGHT
                        )
                    ]
                ),

                *filas_ventas
            ]
        )
    )

    # =========================
    # ALERTAS
    # =========================

    alertas_stock = (
        get_alertas_stock()
        if puede_ver_inventario
        else []
    )

    tarjetas_alerta = []

    for producto in alertas_stock:

        sin_stock = int(
            producto["stock"] or 0
        ) <= 0

        color_alerta = (
            ROJO
            if sin_stock
            else AMARILLO
        )

        titulo_alerta = (
            "Sin stock"
            if sin_stock
            else "Stock bajo"
        )

        tarjetas_alerta.append(

            ft.Container(

                bgcolor=ft.Colors.with_opacity(
                    0.08,
                    color_alerta
                ),

                border=ft.Border.all(
                    1,
                    ft.Colors.with_opacity(
                        0.21,
                        color_alerta
                    )
                ),

                border_radius=12,

                padding=14,

                content=ft.Row(
                    controls=[

                        ft.Icon(
                            ft.Icons.ERROR_OUTLINE
                            if sin_stock
                            else ft.Icons.WARNING_AMBER_ROUNDED,
                            color=color_alerta
                        ),

                        ft.Column(
                            expand=True,
                            spacing=2,

                            controls=[

                                ft.Text(
                                    titulo_alerta,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    f"{producto['nombre']}: "
                                    f"{producto['stock']} unidades "
                                    f"(mínimo "
                                    f"{producto['stock_minimo']})",
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        )
                    ]
                )
            )
        )

    if not tarjetas_alerta:

        tarjetas_alerta.append(

            ft.Container(

                bgcolor=ft.Colors.with_opacity(
                    0.08,
                    VERDE
                ),

                border=ft.Border.all(
                    1,
                    ft.Colors.with_opacity(
                        0.21,
                        VERDE
                    )
                ),

                border_radius=12,

                padding=14,

                content=ft.Row(
                    controls=[

                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_ROUNDED,
                            color=VERDE
                        ),

                        ft.Column(
                            spacing=2,

                            controls=[

                                ft.Text(
                                    "Inventario saludable",
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "No hay productos bajo el stock mínimo",
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        )
                    ]
                )
            )
        )

    alertas = ft.Container(

        expand=True,

        bgcolor=COLOR_CARD,

        border=ft.Border.all(
            1,
            "#34344A"
        ),

        border_radius=18,

        padding=22,

        content=ft.Column(
            controls=[

                ft.Text(
                    "Alertas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF"
                ),

                ft.Text(
                    "Estado del sistema",
                    size=12,
                    color=TEXTO_SECUNDARIO
                ),

                ft.Container(
                    height=6
                ),

                *tarjetas_alerta,

                ft.TextButton(
                    "Ver inventario",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda e: navegar(
                        "/inventario"
                    )
                )
            ],

            spacing=10
        )
    )

    # =========================
    # GRÁFICOS
    # =========================

    datos_ventas_7_dias = (
        get_ventas_ultimos_7_dias()
        if puede_ver_ventas
        else []
    )

    datos_productos = (
        get_productos_mas_vendidos()
        if puede_ver_productos or puede_ver_inventario
        else []
    )

    graficos = ft.Row(
        controls=[
            *(
                [grafico_ventas(datos_ventas_7_dias)]
                if puede_ver_ventas
                else []
            ),
            *(
                [grafico_productos(datos_productos)]
                if puede_ver_productos or puede_ver_inventario
                else []
            )
        ],
        spacing=18
    )

    # =========================
    # ACTIVIDAD Y LOGS
    # =========================

    resumen_logs = obtener_resumen_logs() if puede_ver_logs else []

    logs_recientes = (
        obtener_logs_recientes(5)
        if puede_ver_logs
        else []
    )

    grafico_actividad = grafico_logs(
        resumen_logs,
        on_ver_logs=lambda e: navegar(
            "/logs"
        )
    )

    filas_logs = []

    for log in logs_recientes:

        nivel = log.get(
            "nivel",
            "Información"
        )

        if nivel == "Error":

            color_log = ROJO

            icono_log = (
                ft.Icons.ERROR_OUTLINE
            )

        elif nivel == "Advertencia":

            color_log = AMARILLO

            icono_log = (
                ft.Icons.WARNING_AMBER_ROUNDED
            )

        else:

            color_log = MORADO

            icono_log = (
                ft.Icons.INFO_OUTLINE
            )

        fecha_log = log.get(
            "fecha"
        )

        fecha_texto = (

            fecha_log.strftime(
                "%d/%m %H:%M"
            )

            if hasattr(
                fecha_log,
                "strftime"
            )

            else str(
                fecha_log or ""
            )
        )

        filas_logs.append(

            ft.Container(

                padding=ft.Padding.symmetric(
                    vertical=9
                ),

                border=ft.Border(
                    bottom=ft.BorderSide(
                        1,
                        "#34344A"
                    )
                ),

                content=ft.Row(
                    controls=[

                        ft.Container(
                            width=34,
                            height=34,
                            border_radius=9,

                            bgcolor=ft.Colors.with_opacity(
                                0.09,
                                color_log
                            ),

                            alignment=ft.Alignment.CENTER,

                            content=ft.Icon(
                                icono_log,
                                size=18,
                                color=color_log
                            )
                        ),

                        ft.Column(
                            expand=True,
                            spacing=2,

                            controls=[

                                ft.Text(
                                    log.get(
                                        "accion"
                                    )
                                    or
                                    "Actividad del sistema",

                                    size=13,

                                    color="#FFFFFF",

                                    weight=ft.FontWeight.W_600,

                                    max_lines=1,

                                    overflow=(
                                        ft.TextOverflow.ELLIPSIS
                                    )
                                ),

                                ft.Text(
                                    f"{log.get('usuario') or 'Sistema'} "
                                    f"· "
                                    f"{log.get('modulo') or '-'}",

                                    size=11,

                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.Text(
                            fecha_texto,
                            size=10,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                )
            )
        )

    if not filas_logs:

        filas_logs.append(

            ft.Container(

                expand=True,

                alignment=ft.Alignment.CENTER,

                content=ft.Text(
                    "No hay actividad registrada",
                    color=TEXTO_SECUNDARIO
                )
            )
        )

    actividad_reciente = ft.Container(

        expand=True,

        height=300,

        bgcolor=COLOR_CARD,

        border=ft.Border.all(
            1,
            "#34344A"
        ),

        border_radius=18,

        padding=22,

        content=ft.Column(
            expand=True,
            spacing=4,

            controls=[

                ft.Row(
                    controls=[

                        ft.Column(
                            spacing=3,

                            controls=[

                                ft.Text(
                                    "Actividad reciente",
                                    size=18,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "Últimos eventos registrados en los logs",
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.Container(
                            expand=True
                        ),

                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            icon_color=MORADO,
                            tooltip="Abrir logs",
                            on_click=lambda e: navegar(
                                "/logs"
                            )
                        )
                    ]
                ),

                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=filas_logs
                )
            ]
        )
    )

    panel_actividad = ft.Row(
        spacing=18,

        controls=[
            grafico_actividad,
            actividad_reciente
        ]
    )

    # =========================
    # DISPENSADORES
    # =========================

    dispensadores_get = (
        get_dispensadores()
        if puede_ver_dispensadores
        else []
    )

    def dispensador(
        numero,
        producto,
        cantidad,
        estado,
        color
    ):

        return ft.Container(

            expand=True,

            padding=18,

            bgcolor=COLOR_CARD_2,

            border_radius=14,

            content=ft.Row(
                controls=[

                    ft.Container(
                        width=45,
                        height=45,

                        bgcolor=ft.Colors.with_opacity(
                            0.13,
                            color
                        ),

                        border_radius=12,

                        alignment=ft.Alignment.CENTER,

                        content=ft.Icon(
                            ft.Icons.PRECISION_MANUFACTURING_ROUNDED,
                            color=color
                        )
                    ),

                    ft.Column(
                        controls=[

                            ft.Text(
                                f"Dispensador {numero}",
                                size=14,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                producto,
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ],

                        spacing=2
                    ),

                    ft.Container(
                        expand=True
                    ),

                    ft.Column(

                        controls=[

                            ft.Text(
                                f"{cantidad} unidades",
                                size=12,
                                color="#FFFFFF"
                            ),

                            ft.Row(

                                controls=[

                                    ft.Container(
                                        width=7,
                                        height=7,
                                        bgcolor=color,
                                        border_radius=10
                                    ),

                                    ft.Text(
                                        estado,
                                        size=11,
                                        color=color
                                    )
                                ],

                                spacing=5
                            )
                        ],

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.END
                        )
                    )
                ]
            )
        )

    # =========================
    # CREAR TARJETAS
    # =========================

    tarjetas_dispensadores = []

    for dato in dispensadores_get:

        estado = dato["estado"]

        if estado == "Disponible":

            color = VERDE

        elif estado == "Stock bajo":

            color = AMARILLO

        else:

            color = ROJO

        tarjetas_dispensadores.append(

            dispensador(

                dato["id_dispensador"],

                dato["producto"],

                dato["cantidad_disponible"],

                estado,

                color
            )
        )

    # =========================
    # CONTENEDOR DISPENSADORES
    # =========================

    dispensadores = ft.Container(

        bgcolor=COLOR_CARD,

        border=ft.Border.all(
            1,
            "#34344A"
        ),

        border_radius=18,

        padding=22,

        content=ft.Column(

            controls=[

                ft.Row(
                    controls=[

                        ft.Text(
                            "Dispensadores",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF"
                        ),

                        ft.Container(
                            expand=True
                        ),

                        ft.TextButton(
                            "Administrar",
                            on_click=lambda e: navegar(
                                "/dispensadores"
                            )
                        )
                    ]
                ),

                ft.Row(
                    controls=tarjetas_dispensadores,
                    spacing=15
                )
            ]
        )
    )

    # =========================
    # CONTENIDO
    # =========================

    contenido = ft.Container(

        expand=True,

        padding=30,

        bgcolor=ft.Colors.with_opacity(
            0.85,
            "#0D0D14"
        ),

        content=ft.Column(

            controls=[

                # =========================
                # CABECERA
                # =========================

                ft.Row(

                    controls=[

                        ft.Column(

                            controls=[

                                ft.Text(
                                    f"Hola, {nombre_usuario}",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                ),

                                ft.Text(
                                    f"Resumen general · {fecha_actual}",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ],

                            spacing=3
                        ),

                        ft.Container(
                            expand=True
                        ),

                        ft.IconButton(

                            icon=ft.Icons.REFRESH_ROUNDED,

                            icon_color=MORADO,

                            bgcolor=ft.Colors.with_opacity(
                                0.12,
                                MORADO
                            ),

                            hover_color=ft.Colors.with_opacity(
                                0.22,
                                MORADO
                            ),

                            tooltip="Actualizar panel (Ctrl+R)",

                            on_click=lambda e:
                                page.refrescar_vista_actual()
                        ),

                        ft.Container(

                            padding=ft.Padding.symmetric(
                                horizontal=14,
                                vertical=8
                            ),

                            bgcolor=COLOR_CARD,

                            border_radius=12,

                            content=ft.Row(

                                controls=[

                                    ft.CircleAvatar(

                                        content=ft.Image(
                                            src="LogoCandyKodaVerySimple.svg",
                                            width=26,
                                            height=26,
                                            fit=ft.BoxFit.CONTAIN
                                        ),

                                        bgcolor="#211731"
                                    ),

                                    ft.Column(

                                        controls=[

                                            ft.Text(
                                                nombre_usuario,
                                                size=13,
                                                color="#FFFFFF",
                                                weight=ft.FontWeight.BOLD
                                            ),

                                            ft.Text(
                                                rol_usuario,
                                                size=11,
                                                color=TEXTO_SECUNDARIO
                                            )
                                        ],

                                        spacing=0
                                    )
                                ]
                            )
                        )
                    ]
                ),

                ft.Container(
                    height=8
                ),

                # =========================
                # ESTADÍSTICAS
                # =========================

                *(
                    [estadisticas]
                    if estadisticas.controls
                    else []
                ),

                # =========================
                # GRÁFICOS
                # =========================

                *(
                    [graficos]
                    if graficos.controls
                    else []
                ),

                *([panel_actividad] if puede_ver_logs else []),

                # =========================
                # VENTAS Y ALERTAS
                # =========================

                *([ft.Row(

                    controls=[
                        *(
                            [ventas_recientes]
                            if puede_ver_ventas
                            else []
                        ),
                        *(
                            [alertas]
                            if puede_ver_inventario
                            else []
                        )
                    ],

                    spacing=18,

                    vertical_alignment=(
                        ft.CrossAxisAlignment.START
                    )
                )] if puede_ver_ventas or puede_ver_inventario else []),

                # =========================
                # DISPENSADORES
                # =========================

                *(
                    [dispensadores]
                    if puede_ver_dispensadores
                    else []
                )
            ],

            scroll=ft.ScrollMode.AUTO,

            spacing=20
        )
    )

    menu_lateral = sidebar(page)

    # =========================
    # VIEW
    # =========================

    return ft.View(

        route="/dashboard",

        padding=0,

        spacing=0,

        bgcolor=ft.Colors.TRANSPARENT,

        controls=[

            ft.Row(

                controls=[
                    menu_lateral,
                    contenido
                ],

                expand=True,

                spacing=0,

                vertical_alignment=(
                    ft.CrossAxisAlignment.STRETCH
                )
            )
        ]
    )
