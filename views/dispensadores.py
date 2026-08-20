import flet as ft

from components.sidebar import sidebar

from database.dispensadores import (
    get_dispensadores,
    obtener_productos_disponibles,
    asignar_producto_dispensador,
    quitar_producto_dispensador,
    cambiar_estado_dispensador,
    recargar_dispensador
)
from services.autorizacion import puede_realizar


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
AMARILLO = "#FFC107"
ROJO = "#FF4FA3"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#C3C3CE"


def dispensadores_view(page: ft.Page):

    dispensadores = get_dispensadores()
    usuario_actual = getattr(page, "usuario_actual", None) or {}
    id_usuario_actual = (
        usuario_actual.get("id_usuario")
        if isinstance(usuario_actual, dict)
        else None
    )
    puede_recargar = puede_realizar(
        usuario_actual,
        "recargar_dispensador"
    )

    filtro_estado = None

    texto_total = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_disponibles = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_stock_bajo = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_fuera_servicio = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    buscador = ft.TextField(
        hint_text="Buscar dispensador o producto...",
        prefix_icon=ft.Icons.SEARCH,
        width=380,
        height=45,
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
        focused_border_color=MORADO,
        cursor_color=ROSA,
        color=TEXTO_PRINCIPAL,
        border_radius=12
    )

    lista_dispensadores = ft.Column(
        spacing=10
    )

    def abrir_cambiar_estado(dispensador):

        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=dispensador["estado"],
            options=[
                ft.DropdownOption(
                    key="Disponible",
                    text="Disponible"
                ),
                ft.DropdownOption(
                    key="Dispensando",
                    text="Dispensando"
                ),
                ft.DropdownOption(
                    key="Sin stock",
                    text="Sin stock"
                ),
                ft.DropdownOption(
                    key="Error",
                    text="Error"
                ),
                ft.DropdownOption(
                    key="Desconectado",
                    text="Desconectado"
                )
            ]
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            if estado_dropdown.value is None:
                mensaje_error.value = "Seleccione un estado"
                page.update()
                return

            exito = cambiar_estado_dispensador(
                dispensador["id_dispensador"],
                estado_dropdown.value
            )

            if exito:
                page.pop_dialog()

                mostrar_mensaje(
                    "Estado actualizado correctamente"
                )

                refrescar()

            else:
                mensaje_error.value = (
                    "No se pudo cambiar el estado"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.SETTINGS_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        f"Estado del dispensador "
                        f"{dispensador['id_dispensador']}",
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
                            f"Estado actual: {dispensador['estado']}",
                            color=TEXTO_SECUNDARIO
                        ),

                        estado_dropdown,

                        mensaje_error
                    ]
                )
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE_OUTLINED,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    def mostrar_mensaje(texto, color=VERDE):

        snack = ft.SnackBar(
            content=ft.Text(
                texto,
                color="#FFFFFF"
            ),
            bgcolor=color
        )

        page.show_dialog(snack)

    def actualizar_estadisticas():

        total = len(dispensadores)

        disponibles = sum(
            1
            for d in dispensadores
            if d.get("estado") == "Disponible"
        )

        stock_bajo = sum(
            1
            for d in dispensadores
            if 0 < int(d.get("cantidad_disponible") or 0)
            <= int(d.get("stock_minimo") or 0)
        )

        fuera_servicio = sum(
            1
            for d in dispensadores
            if d.get("estado") in {"Error", "Desconectado"}
        )

        texto_total.value = str(total)
        texto_disponibles.value = str(disponibles)
        texto_stock_bajo.value = str(stock_bajo)
        texto_fuera_servicio.value = str(fuera_servicio)

    def refrescar():

        nonlocal dispensadores

        dispensadores = get_dispensadores()

        actualizar_estadisticas()
        cargar_dispensadores()

        page.update()

    def ver_detalles(dispensador):

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
                        ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        f"Dispensador "
                        f"{dispensador['id_dispensador']}",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=430,

                content=ft.Column(
                    tight=True,
                    spacing=12,

                    controls=[
                        dato(
                            ft.Icons.COOKIE_OUTLINED,
                            "Producto",
                            dispensador.get(
                                "producto",
                                "Sin asignar"
                            )
                        ),

                        dato(
                            ft.Icons.INVENTORY_2_OUTLINED,
                            "Cantidad disponible",
                            dispensador.get(
                                "cantidad_disponible",
                                0
                            )
                        ),

                        dato(
                            ft.Icons.SETTINGS_OUTLINED,
                            "Servo",
                            dispensador.get(
                                "numero_servo",
                                "Sin configurar"
                            )
                        ),

                        dato(
                            ft.Icons.USB,
                            "Puerto Arduino",
                            dispensador.get(
                                "puerto_arduino",
                                "Sin configurar"
                            )
                        ),

                        dato(
                            ft.Icons.INFO_OUTLINE,
                            "Estado",
                            dispensador.get(
                                "estado",
                                ""
                            )
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

    def abrir_asignar_producto(dispensador):

        productos = obtener_productos_disponibles()

        producto_dropdown = ft.Dropdown(
            label="Producto",
            hint_text="Selecciona un producto",

            options=[
                ft.DropdownOption(
                    key=str(p["id_producto"]),
                    text=p["nombre"]
                )
                for p in productos
            ]
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            if producto_dropdown.value is None:

                mensaje_error.value = (
                    "Seleccione un producto"
                )

                page.update()
                return

            exito = asignar_producto_dispensador(
                dispensador["id_dispensador"],
                int(producto_dropdown.value)
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    "Producto asignado correctamente"
                )

                refrescar()

            else:

                mensaje_error.value = (
                    "No se pudo asignar el producto"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Asignar producto al dispensador "
                f"{dispensador['id_dispensador']}",
                weight=ft.FontWeight.BOLD
            ),

            content=ft.Container(
                width=400,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[
                        producto_dropdown,
                        mensaje_error
                    ]
                )
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.ElevatedButton(
                    "Asignar",
                    icon=ft.Icons.LINK,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    def quitar_producto(dispensador):

        exito = quitar_producto_dispensador(
            dispensador["id_dispensador"]
        )

        if exito:

            mostrar_mensaje(
                "Producto desvinculado del dispensador",
                AMARILLO
            )

            refrescar()

        else:

            mostrar_mensaje(
                "No se pudo quitar el producto",
                ROJO
            )

    def abrir_recargar_dispensador(dispensador):
        cantidad = ft.TextField(
            label="Unidades agregadas físicamente",
            hint_text="Ej.: 10",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.ADD_BOX_OUTLINED
        )
        mensaje_error = ft.Text("", color=ROJO, size=12)

        def guardar(e):
            valor = (cantidad.value or "").strip()
            try:
                unidades = int(valor)
                if unidades <= 0:
                    raise ValueError
            except ValueError:
                mensaje_error.value = (
                    "Ingrese una cantidad entera mayor que cero"
                )
                page.update()
                return

            resultado = recargar_dispensador(
                dispensador["id_dispensador"],
                unidades,
                id_usuario_actual
            )

            if resultado["exito"]:
                page.pop_dialog()
                mostrar_mensaje(resultado["mensaje"])
                refrescar()
            else:
                mensaje_error.value = resultado["mensaje"]
                page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Recargar dispensador"),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Text(
                            (
                                f"{dispensador.get('producto') or 'Sin producto'} · "
                                f"Carga actual: "
                                f"{dispensador.get('cantidad_disponible') or 0} · "
                                f"Stock disponible: "
                                f"{dispensador.get('stock_producto') or 0}"
                            ),
                            color=TEXTO_SECUNDARIO
                        ),
                        cantidad,
                        mensaje_error
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),
                ft.ElevatedButton(
                    "Registrar carga",
                    icon=ft.Icons.ADD,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )
        page.show_dialog(dialogo)

    def crear_fila(dispensador):

        estado = dispensador.get(
            "estado",
            "Disponible"
        )

        if estado == "Disponible":

            color_estado = VERDE
            icono_estado = (
                ft.Icons.CHECK_CIRCLE_OUTLINE
            )

        elif estado == "Dispensando":

            color_estado = MORADO
            icono_estado = ft.Icons.SYNC

        elif estado == "Sin stock":

            color_estado = AMARILLO
            icono_estado = (
                ft.Icons.WARNING_AMBER_ROUNDED
            )

        elif estado == "Error":

            color_estado = ROJO
            icono_estado = ft.Icons.ERROR_OUTLINE

        else:

            color_estado = TEXTO_SECUNDARIO
            icono_estado = ft.Icons.POWER_OFF

        producto = dispensador.get(
            "producto"
        )

        if not producto:
            producto = "Sin asignar"

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
                vertical_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[

                    ft.Container(
                        width=220,

                        content=ft.Row(
                            spacing=12,

                            controls=[
                                ft.Container(
                                    width=46,
                                    height=46,
                                    border_radius=11,
                                    bgcolor=ft.Colors.with_opacity(
                                        0.09,
                                        MORADO
                                    ),
                                    alignment=ft.Alignment.CENTER,

                                    content=ft.Icon(
                                        ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                                        color=MORADO,
                                        size=24
                                    )
                                ),

                                ft.Column(
                                    spacing=2,

                                    controls=[
                                        ft.Text(
                                            f"Dispensador "
                                            f"{dispensador['id_dispensador']}",
                                            size=14,
                                            color=TEXTO_PRINCIPAL,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            f"Servo "
                                            f"{dispensador.get('numero_servo', '-')}",
                                            size=11,
                                            color=TEXTO_SECUNDARIO
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    ft.Container(
                        width=190,

                        content=ft.Text(
                            producto,
                            size=13,
                            color=TEXTO_PRINCIPAL
                        )
                    ),

                    ft.Container(
                        width=120,

                        content=ft.Text(
                            str(
                                dispensador.get(
                                    "cantidad_disponible",
                                    0
                                )
                            ),
                            size=14,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        width=140,

                        content=ft.Text(
                            str(
                                dispensador.get(
                                    "puerto_arduino",
                                    "-"
                                )
                            ),
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    ft.Container(
                        width=160,

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

                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        tooltip="Opciones",

                        items=[

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.VISIBILITY_OUTLINED,
                                            size=18
                                        ),

                                        ft.Text(
                                            "Ver detalles"
                                        )
                                    ]
                                ),

                                on_click=lambda e, d=dispensador: (
                                    ver_detalles(d)
                                )
                            ),

                            *([ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ADD_BOX_OUTLINED,
                                            size=18,
                                            color=VERDE
                                        ),
                                        ft.Text("Recargar dispensador")
                                    ]
                                ),
                                on_click=lambda e, d=dispensador: (
                                    abrir_recargar_dispensador(d)
                                )
                            )] if puede_recargar else []),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.INVENTORY_2_OUTLINED,
                                            size=18,
                                            color=MORADO
                                        ),

                                        ft.Text(
                                            "Cambiar producto"
                                            if dispensador.get(
                                                "id_producto"
                                            )
                                            else
                                            "Asignar producto"
                                        )
                                    ]
                                ),

                                on_click=lambda e, d=dispensador: (
                                    abrir_asignar_producto(d)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.SETTINGS_OUTLINED,
                                            size=18,
                                            color=AMARILLO
                                        ),

                                        ft.Text(
                                            "Cambiar estado"
                                        )
                                    ]
                                ),

                                on_click=lambda e, d=dispensador: (
                                    abrir_cambiar_estado(d)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.LINK_OFF,
                                            size=18,
                                            color=ROJO
                                        ),

                                        ft.Text(
                                            "Quitar producto",
                                            color=ROJO
                                        )
                                    ]
                                ),

                                on_click=lambda e, d=dispensador: (
                                    quitar_producto(d)
                                )
                            )
                        ]
                    )
                ]
            )
        )

    def cargar_dispensadores():

        lista_dispensadores.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for dispensador in dispensadores:

            producto = str(
                dispensador.get(
                    "producto",
                    ""
                )
            ).lower()

            numero = str(
                dispensador.get(
                    "id_dispensador",
                    ""
                )
            )

            estado = dispensador.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in producto
                or texto in numero
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_estado
            ):

                lista_dispensadores.controls.append(
                    crear_fila(
                        dispensador
                    )
                )

                encontrados += 1

        if encontrados == 0:

            lista_dispensadores.controls.append(
                ft.Container(
                    height=180,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                        controls=[
                            ft.Icon(
                                ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron dispensadores",
                                weight=ft.FontWeight.BOLD
                            )
                        ]
                    )
                )
            )

    def mostrar_filtros(e):

        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=filtro_estado,

            options=[
                ft.DropdownOption(
                    key="Disponible",
                    text="Disponible"
                ),

                ft.DropdownOption(
                    key="Stock bajo",
                    text="Stock bajo"
                ),

                ft.DropdownOption(
                    key="Fuera de servicio",
                    text="Fuera de servicio"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_estado

            filtro_estado = estado_dropdown.value

            page.pop_dialog()

            cargar_dispensadores()
            page.update()

        def limpiar(e):

            nonlocal filtro_estado

            filtro_estado = None

            page.pop_dialog()

            cargar_dispensadores()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Filtrar dispensadores",
                weight=ft.FontWeight.BOLD
            ),

            content=ft.Container(
                width=350,
                content=estado_dropdown
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
            controls=[
                ft.Container(
                    width=220,
                    content=ft.Text(
                        "DISPENSADOR",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=190,
                    content=ft.Text(
                        "PRODUCTO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=120,
                    content=ft.Text(
                        "CARGA",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=140,
                    content=ft.Text(
                        "PUERTO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=160,
                    content=ft.Text(
                        "ESTADO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    expand=True
                )
            ]
        )
    )

    buscador.on_change = lambda e: (
        cargar_dispensadores(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_dispensadores()

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
                            "Dispensadores",
                            size=30,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Administra los módulos físicos de entrega",
                            size=14,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                ),

                ft.Row(
                    spacing=15,

                    controls=[
                        tarjeta_resumen(
                            "Dispensadores",
                            texto_total,
                            ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                            MORADO,
                            "Registrados"
                        ),

                        tarjeta_resumen(
                            "Disponibles",
                            texto_disponibles,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Funcionando"
                        ),

                        tarjeta_resumen(
                            "Stock bajo",
                            texto_stock_bajo,
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            AMARILLO,
                            "Requieren revisión"
                        ),

                        tarjeta_resumen(
                            "Fuera de servicio",
                            texto_fuera_servicio,
                            ft.Icons.ERROR_OUTLINE,
                            ROJO,
                            "No operativos"
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

                lista_dispensadores
            ]
        )
    )

    return ft.View(
        route="/dispensadores",
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
