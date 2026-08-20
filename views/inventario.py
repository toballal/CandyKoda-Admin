import flet as ft

from components.sidebar import sidebar
from database.inventario import (
    obtener_inventario,
    agregar_stock,
    quitar_stock
)

# =========================================================
# COLORES
# =========================================================

ROSA = "#FF4FA3"
MORADO = "#9B59FF"
ROJO = "#FF4FA3"
AMARILLO = "#FFC107"
VERDE = "#9B59FF"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#C3C3CE"


def inventario_view(page: ft.Page):

    # =========================================================
    # DATOS
    # =========================================================

    productos = []

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    texto_total_productos = ft.Text(
        "0",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_stock_bajo = ft.Text(
        "0",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_sin_stock = ft.Text(
        "0",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar producto...",
        prefix_icon=ft.Icons.SEARCH,
        width=350,
        height=45,
        border_radius=10,
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
        color=TEXTO_PRINCIPAL,
        hint_style=ft.TextStyle(
            color=TEXTO_SECUNDARIO
        )
    )

    # =========================================================
    # FILTRO
    # =========================================================

    filtro_estado = ft.Dropdown(
        width=190,
        value="Todos",
        options=[
            ft.DropdownOption(
                key="Todos",
                text="Todos"
            ),
            ft.DropdownOption(
                key="Normal",
                text="Normal"
            ),
            ft.DropdownOption(
                key="Stock bajo",
                text="Stock bajo"
            ),
            ft.DropdownOption(
                key="Sin stock",
                text="Sin stock"
            ),
        ],
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
        border_radius=10,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # LISTA
    # =========================================================

    lista_inventario = ft.Column(
        spacing=10
    )

    # =========================================================
    # OBTENER ESTADO
    # =========================================================

    def obtener_estado(stock, stock_minimo):

        stock = int(stock or 0)
        stock_minimo = int(stock_minimo or 0)

        if stock <= 0:
            return (
                "Sin stock",
                ROJO,
                ft.Icons.ERROR_OUTLINE
            )

        if stock <= stock_minimo:
            return (
                "Stock bajo",
                AMARILLO,
                ft.Icons.WARNING_AMBER_ROUNDED
            )

        return (
            "Normal",
            VERDE,
            ft.Icons.CHECK_CIRCLE_OUTLINE
        )

    # =========================================================
    # MENSAJE
    # =========================================================

    def mostrar_mensaje(texto, color=VERDE):

        snack = ft.SnackBar(
            content=ft.Text(
                texto,
                color="#FFFFFF"
            ),
            bgcolor=color
        )

        page.show_dialog(snack)

    # =========================================================
    # CANTIDAD PARA AGREGAR
    # =========================================================

    cantidad_stock = ft.TextField(
        label="Cantidad",
        hint_text="Ej.: 20",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.ADD,
        width=300,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO
    )

    # =========================================================
    # GUARDAR STOCK
    # =========================================================

    def guardar_stock(producto):

        cantidad_stock.error_text = None

        valor = cantidad_stock.value

        if not valor or valor.strip() == "":
            cantidad_stock.error_text = "Ingrese una cantidad."
            page.update()
            return

        try:
            cantidad = int(valor)

        except ValueError:
            cantidad_stock.error_text = (
                "La cantidad debe ser un número entero."
            )
            page.update()
            return

        if cantidad <= 0:
            cantidad_stock.error_text = (
                "La cantidad debe ser mayor que 0."
            )
            page.update()
            return

        usuario = getattr(
            page,
            "usuario_actual",
            None
        ) or {}

        exito = agregar_stock(
            producto["id_producto"],
            cantidad,
            usuario.get("id_usuario")
        )

        if not exito:

            mostrar_mensaje(
                "No se pudo actualizar el stock.",
                ROJO
            )

            return

        page.pop_dialog()

        mostrar_mensaje(
            f"Se agregaron {cantidad} unidades a "
            f"{producto['nombre']}."
        )

        refrescar_inventario()

    # =========================================================
    # DIÁLOGO AGREGAR STOCK
    # =========================================================

    def abrir_agregar_stock(producto):

        cantidad_stock.value = ""
        cantidad_stock.error_text = None

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.ADD_CIRCLE_OUTLINE,
                        color=VERDE
                    ),

                    ft.Text(
                        "Agregar stock",
                        color=TEXTO_PRINCIPAL,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=350,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[

                        ft.Text(
                            producto["nombre"],
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO_PRINCIPAL
                        ),

                        ft.Container(
                            padding=12,
                            bgcolor=COLOR_CARD_2,
                            border_radius=10,

                            content=ft.Row(
                                spacing=10,
                                controls=[

                                    ft.Icon(
                                        ft.Icons.INVENTORY_2_OUTLINED,
                                        color=MORADO
                                    ),

                                    ft.Text(
                                        f"Stock actual: "
                                        f"{producto['stock']}",
                                        color=TEXTO_SECUNDARIO
                                    )
                                ]
                            )
                        ),

                        cantidad_stock
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.ElevatedButton(
                    "Agregar",
                    icon=ft.Icons.ADD,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=lambda e:
                        guardar_stock(producto)
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # DIÁLOGO QUITAR STOCK
    # =========================================================

    def abrir_quitar_stock(producto):

        cantidad_quitar = ft.TextField(
            label="Cantidad a quitar",
            hint_text="Ej.: 10",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.REMOVE,
            width=300,
            border_color=COLOR_BORDE,
            focused_border_color=ROJO
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        # -----------------------------------------------------
        # CONFIRMAR
        # -----------------------------------------------------

        def confirmar_quitar(e):

            mensaje_error.value = ""

            valor = cantidad_quitar.value

            if not valor or valor.strip() == "":
                mensaje_error.value = (
                    "Ingrese una cantidad."
                )
                page.update()
                return

            try:
                cantidad = int(valor)

            except ValueError:
                mensaje_error.value = (
                    "La cantidad debe ser un número entero."
                )
                page.update()
                return

            if cantidad <= 0:
                mensaje_error.value = (
                    "La cantidad debe ser mayor que 0."
                )
                page.update()
                return

            stock_actual = int(
                producto.get("stock") or 0
            )

            if cantidad > stock_actual:
                mensaje_error.value = (
                    f"No puedes quitar {cantidad} unidades. "
                    f"Solo hay {stock_actual} disponibles."
                )
                page.update()
                return

            usuario = getattr(
                page,
                "usuario_actual",
                None
            ) or {}

            exito = quitar_stock(
                producto["id_producto"],
                cantidad,
                usuario.get("id_usuario")
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    f"Se quitaron {cantidad} unidades de "
                    f"{producto['nombre']}.",
                    AMARILLO
                )

                refrescar_inventario()

            else:

                mensaje_error.value = (
                    "No se pudo actualizar el stock."
                )

                page.update()

        # -----------------------------------------------------
        # DIÁLOGO
        # -----------------------------------------------------

        dialogo = ft.AlertDialog(

            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[

                    ft.Icon(
                        ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        color=ROJO
                    ),

                    ft.Text(
                        "Quitar stock",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=380,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[

                        ft.Text(
                            producto["nombre"],
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Container(
                            padding=12,
                            bgcolor=COLOR_CARD_2,
                            border_radius=10,

                            content=ft.Row(
                                spacing=10,

                                controls=[

                                    ft.Icon(
                                        ft.Icons.INVENTORY_2_OUTLINED,
                                        color=ROJO
                                    ),

                                    ft.Text(
                                        f"Stock actual: "
                                        f"{producto['stock']}",
                                        color=TEXTO_SECUNDARIO
                                    )
                                ]
                            )
                        ),

                        cantidad_quitar,

                        mensaje_error
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                        page.pop_dialog()
                ),

                ft.ElevatedButton(
                    "Quitar stock",
                    icon=ft.Icons.REMOVE,
                    bgcolor=ROJO,
                    color="#FFFFFF",
                    on_click=confirmar_quitar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # CREAR FILA
    # =========================================================

    def crear_fila(producto):

        stock = int(
            producto.get("stock") or 0
        )

        stock_minimo = int(
            producto.get("stock_minimo") or 0
        )

        estado, color_estado, icono = obtener_estado(
            stock,
            stock_minimo
        )

        dispensador = producto.get(
            "dispensador"
        ) or "Sin asignar"

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

                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    # =========================================
                    # PRODUCTO
                    # =========================================

                    ft.Container(
                        width=250,

                        content=ft.Row(
                            spacing=10,

                            controls=[

                                ft.Container(
                                    width=42,
                                    height=42,
                                    border_radius=10,

                                    bgcolor=ft.Colors.with_opacity(
                                        0.08,
                                        ROSA
                                    ),

                                    alignment=ft.Alignment.CENTER,

                                    content=ft.Icon(
                                        ft.Icons.INVENTORY_2_OUTLINED,
                                        size=21,
                                        color=ROSA
                                    )
                                ),

                                ft.Column(
                                    spacing=2,

                                    controls=[

                                        ft.Text(
                                            producto["nombre"],
                                            size=14,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            color=(
                                                TEXTO_PRINCIPAL
                                            ),
                                            weight=(
                                                ft.FontWeight.W_600
                                            )
                                        ),

                                        ft.Text(
                                            f'ID #{producto["id_producto"]}',
                                            size=11,
                                            color=(
                                                TEXTO_SECUNDARIO
                                            )
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    # =========================================
                    # STOCK
                    # =========================================

                    ft.Container(
                        width=70,

                        content=ft.Text(
                            str(stock),
                            size=14,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    # =========================================
                    # STOCK MÍNIMO
                    # =========================================

                    ft.Container(
                        width=105,

                        content=ft.Text(
                            str(stock_minimo),
                            size=13,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =========================================
                    # DISPENSADOR
                    # =========================================

                    ft.Container(
                        width=140,

                        content=ft.Text(
                            str(dispensador),
                            size=12,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =========================================
                    # ESTADO
                    # =========================================

                    ft.Container(
                        width=130,

                        content=ft.Row(
                            spacing=7,

                            controls=[

                                ft.Icon(
                                    icono,
                                    size=18,
                                    color=color_estado
                                ),

                                ft.Text(
                                    estado,
                                    size=12,
                                    color=color_estado,
                                    weight=(
                                        ft.FontWeight.W_600
                                    )
                                )
                            ]
                        )
                    ),

                    # =========================================
                    # ACCIONES
                    # =========================================

                    ft.Container(
                        expand=True,

                        alignment=(
                            ft.Alignment.CENTER_RIGHT
                        ),

                        content=ft.Row(
                            alignment=(
                                ft.MainAxisAlignment.END
                            ),

                            spacing=5,

                            controls=[

                                # AGREGAR
                                ft.IconButton(
                                    icon=(
                                        ft.Icons
                                        .ADD_CIRCLE_OUTLINE
                                    ),

                                    icon_color=VERDE,
                                    icon_size=21,
                                    width=38,
                                    height=38,

                                    bgcolor=(
                                        ft.Colors.with_opacity(
                                            0.09,
                                            VERDE
                                        )
                                    ),

                                    hover_color=(
                                        ft.Colors.with_opacity(
                                            0.19,
                                            VERDE
                                        )
                                    ),

                                    tooltip="Agregar stock",

                                    on_click=lambda e, p=producto:
                                        abrir_agregar_stock(p)
                                ),

                                # QUITAR
                                ft.IconButton(
                                    icon=(
                                        ft.Icons
                                        .REMOVE_CIRCLE_OUTLINE
                                    ),

                                    icon_color=ROJO,
                                    icon_size=21,
                                    width=38,
                                    height=38,

                                    bgcolor=(
                                        ft.Colors.with_opacity(
                                            0.09,
                                            ROJO
                                        )
                                    ),

                                    hover_color=(
                                        ft.Colors.with_opacity(
                                            0.19,
                                            ROJO
                                        )
                                    ),

                                    tooltip="Quitar stock",

                                    on_click=lambda e, p=producto:
                                        abrir_quitar_stock(p)
                                )
                            ]
                        )
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR TABLA
    # =========================================================

    def cargar_tabla():

        lista_inventario.controls.clear()

        texto_busqueda = ""

        if buscador.value:
            texto_busqueda = (
                buscador.value
                .strip()
                .lower()
            )

        estado_seleccionado = (
            filtro_estado.value
            or "Todos"
        )

        cantidad_encontrada = 0

        for producto in productos:

            nombre = str(
                producto.get("nombre", "")
            ).lower()

            # ---------------------------------------------
            # BUSCADOR
            # ---------------------------------------------

            if (
                texto_busqueda
                and texto_busqueda not in nombre
            ):
                continue

            # ---------------------------------------------
            # ESTADO
            # ---------------------------------------------

            estado, _, _ = obtener_estado(
                producto.get("stock"),
                producto.get("stock_minimo")
            )

            if (
                estado_seleccionado != "Todos"
                and estado != estado_seleccionado
            ):
                continue

            cantidad_encontrada += 1

            lista_inventario.controls.append(
                crear_fila(producto)
            )

        # ---------------------------------------------
        # SIN RESULTADOS
        # ---------------------------------------------

        if cantidad_encontrada == 0:

            lista_inventario.controls.append(

                ft.Container(
                    height=180,

                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),

                        controls=[

                            ft.Icon(
                                ft.Icons.SEARCH_OFF,
                                size=42,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron productos.",
                                color=TEXTO_SECUNDARIO,
                                size=14
                            )
                        ]
                    )
                )
            )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        total = len(productos)

        stock_bajo = 0
        sin_stock = 0

        for producto in productos:

            stock = int(
                producto.get("stock") or 0
            )

            minimo = int(
                producto.get("stock_minimo") or 0
            )

            if stock <= 0:

                sin_stock += 1

            elif stock <= minimo:

                stock_bajo += 1

        texto_total_productos.value = str(total)
        texto_stock_bajo.value = str(stock_bajo)
        texto_sin_stock.value = str(sin_stock)

    # =========================================================
    # REFRESCAR INVENTARIO
    # =========================================================

    def refrescar_inventario(e=None):

        nonlocal productos

        try:

            productos = obtener_inventario() or []

            actualizar_estadisticas()
            cargar_tabla()

            page.update()

        except Exception as error:

            print(
                "Error al cargar inventario:",
                error
            )

            mostrar_mensaje(
                "Ocurrió un error al cargar el inventario.",
                ROJO
            )

    # =========================================================
    # FILTROS
    # =========================================================

    def filtrar(e):

        cargar_tabla()
        page.update()

    buscador.on_change = filtrar
    filtro_estado.on_change = filtrar

    # =========================================================
    # TARJETA DE ESTADÍSTICA
    # =========================================================

    def tarjeta_estadistica(
        titulo,
        control_valor,
        icono,
        color
    ):

        return ft.Container(

            expand=True,

            height=120,

            padding=20,

            bgcolor=COLOR_CARD,

            border_radius=15,

            border=ft.Border.all(
                1,
                COLOR_BORDE
            ),

            content=ft.Row(

                alignment=(
                    ft.MainAxisAlignment.SPACE_BETWEEN
                ),

                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    ft.Column(
                        spacing=5,

                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),

                        controls=[

                            ft.Text(
                                titulo,
                                size=14,
                                color=TEXTO_SECUNDARIO
                            ),

                            control_valor
                        ]
                    ),

                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=13,

                        bgcolor=(
                            ft.Colors.with_opacity(
                                0.13,
                                color
                            )
                        ),

                        alignment=ft.Alignment.CENTER,

                        content=ft.Icon(
                            icono,
                            color=color,
                            size=28
                        )
                    )
                ]
            )
        )

    # =========================================================
    # ENCABEZADO TABLA
    # =========================================================

    encabezado_tabla = ft.Container(

        bgcolor=COLOR_CARD_2,

        border_radius=10,

        padding=ft.Padding(
            left=18,
            top=12,
            right=12,
            bottom=12
        ),

        content=ft.Row(

            controls=[

                ft.Container(
                    width=250,

                    content=ft.Text(
                        "PRODUCTO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=70,

                    content=ft.Text(
                        "STOCK",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=105,

                    content=ft.Text(
                        "STOCK MÍNIMO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=140,

                    content=ft.Text(
                        "DISPENSADOR",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,

                    content=ft.Text(
                        "ESTADO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER_RIGHT,

                    content=ft.Text(
                        "ACCIONES",
                        size=11,
                        text_align=ft.TextAlign.RIGHT,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                )
            ]
        )
    )

    # =========================================================
    # TABLA
    # =========================================================

    tabla = ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        content=ft.Column(
            spacing=10,
            controls=[
                encabezado_tabla,
                ft.Container(
                    content=lista_inventario
                )
            ]
        )
    )

    # =========================================================
    # CONTENIDO PRINCIPAL
    # =========================================================

    contenido = ft.Container(

        expand=True,

        padding=30,

        bgcolor=COLOR_FONDO,

        content=ft.Column(

            expand=True,

            scroll=ft.ScrollMode.AUTO,

            spacing=20,

            controls=[

                # =============================================
                # TÍTULO
                # =============================================

                ft.Row(

                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    controls=[

                        ft.Column(

                            spacing=5,

                            controls=[

                                ft.Text(
                                    "Inventario",
                                    size=30,
                                    weight=(
                                        ft.FontWeight.BOLD
                                    ),
                                    color=TEXTO_PRINCIPAL
                                ),

                                ft.Text(
                                    "Controla el stock de los "
                                    "productos de Candy Koda.",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.ElevatedButton(
                            "Actualizar inventario",
                            icon=ft.Icons.REFRESH,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            height=45,
                            on_click=refrescar_inventario
                        )
                    ]
                ),

                # =============================================
                # ESTADÍSTICAS
                # =============================================

                ft.Row(
                    spacing=15,

                    controls=[

                        tarjeta_estadistica(
                            "Productos",
                            texto_total_productos,
                            ft.Icons.INVENTORY_2_OUTLINED,
                            MORADO
                        ),

                        tarjeta_estadistica(
                            "Stock bajo",
                            texto_stock_bajo,
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            AMARILLO
                        ),

                        tarjeta_estadistica(
                            "Sin stock",
                            texto_sin_stock,
                            ft.Icons.ERROR_OUTLINE,
                            ROJO
                        )
                    ]
                ),

                # =============================================
                # FILTROS
                # =============================================

                ft.Container(

                    padding=15,

                    bgcolor=COLOR_CARD,

                    border_radius=12,

                    border=ft.Border.all(
                        1,
                        COLOR_BORDE
                    ),

                    content=ft.Row(

                        alignment=(
                            ft.MainAxisAlignment.SPACE_BETWEEN
                        ),

                        controls=[

                            buscador,

                            ft.Row(

                                spacing=10,

                                controls=[

                                    ft.Icon(
                                        ft.Icons.FILTER_LIST,
                                        color=(
                                            TEXTO_SECUNDARIO
                                        )
                                    ),

                                    filtro_estado
                                ]
                            )
                        ]
                    )
                ),

                # =============================================
                # TABLA
                # =============================================

                tabla
            ]
        )
    )

    # =========================================================
    # CARGA INICIAL
    # =========================================================

    productos = obtener_inventario() or []

    actualizar_estadisticas()
    cargar_tabla()

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(

        route="/inventario",

        padding=0,

        bgcolor=ft.Colors.TRANSPARENT,

        controls=[

            ft.Row(

                expand=True,

                spacing=0,

                controls=[

                    sidebar(page),

                    contenido
                ]
            )
        ]
    )
