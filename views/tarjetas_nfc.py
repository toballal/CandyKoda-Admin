import flet as ft
from decimal import Decimal, InvalidOperation

from components.sidebar import sidebar

from database.tarjetas import (
    obtener_tarjetas_admin,
    cambiar_estado_tarjeta,
    recargar_tarjeta,
    eliminar_tarjeta,
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


def tarjetas_view(page: ft.Page):

    tarjetas = obtener_tarjetas_admin()
    usuario_actual = getattr(page, "usuario_actual", None) or {}
    id_usuario_actual = usuario_actual.get("id_usuario")
    puede_eliminar = puede_realizar(usuario_actual, "eliminar_tarjeta")
    puede_retirar = puede_realizar(usuario_actual, "retirar_tarjeta")

    filtro_estado = "Activa"

    # =========================================================
    # CONTADORES
    # =========================================================

    texto_total = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_activas = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_bloqueadas = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_saldo_total = ft.Text(
        "$0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar por cliente o UID...",
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

    # =========================================================
    # LISTA
    # =========================================================

    lista_tarjetas = ft.Column(
        spacing=10
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
    # ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        total = len(tarjetas)

        activas = sum(
            1
            for tarjeta in tarjetas
            if tarjeta.get("estado") == "Activa"
        )

        bloqueadas = sum(
            1
            for tarjeta in tarjetas
            if tarjeta.get("estado") == "Bloqueada"
        )

        saldo_total = sum(
            float(tarjeta.get("saldo") or 0)
            for tarjeta in tarjetas
        )

        texto_total.value = str(total)
        texto_activas.value = str(activas)
        texto_bloqueadas.value = str(bloqueadas)

        texto_saldo_total.value = (
            f"${saldo_total:,.0f}".replace(",", ".")
        )

    # =========================================================
    # RECARGAR DATOS
    # =========================================================

    def refrescar_tarjetas():

        nonlocal tarjetas

        tarjetas = obtener_tarjetas_admin()

        actualizar_estadisticas()
        cargar_tarjetas()

        page.update()

    # =========================================================
    # VER DETALLES
    # =========================================================

    def ver_detalles(tarjeta):

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

        estado = tarjeta.get(
            "estado",
            "Activa"
        )

        if estado == "Activa":
            color_estado = VERDE
        else:
            color_estado = ROJO

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.CONTACTLESS_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        "Detalle de tarjeta",
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
                        ft.Text(
                            tarjeta.get(
                                "cliente",
                                "Sin cliente"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),

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
                            ft.Icons.NFC,
                            "UID",
                            tarjeta.get("uid", "")
                        ),

                        dato(
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            "Saldo",
                            f"${float(tarjeta.get('saldo', 0)):,.0f}".replace(
                                ",",
                                "."
                            )
                        ),

                        dato(
                            ft.Icons.BADGE_OUTLINED,
                            "RUT",
                            tarjeta.get(
                                "rut",
                                "Sin información"
                            )
                        ),

                        dato(
                            ft.Icons.CALENDAR_MONTH_OUTLINED,
                            "Fecha de registro",
                            tarjeta.get(
                                "fecha_activacion",
                                "Sin información"
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

    # =========================================================
    # RECARGAR SALDO
    # =========================================================

    def abrir_recarga(tarjeta):

        monto = ft.TextField(
            label="Monto a recargar",
            hint_text="Ej: 5000",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        descripcion = ft.TextField(
            label="Descripción",
            value="Recarga realizada por administrador"
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def confirmar(e):

            valor = (monto.value or "").strip()

            if valor == "":
                mensaje_error.value = "Ingrese un monto"
                page.update()
                return

            try:
                cantidad = Decimal(valor)

                if not cantidad.is_finite() or cantidad <= 0:
                    raise ValueError

            except (InvalidOperation, ValueError):

                mensaje_error.value = (
                    "Ingrese un monto válido"
                )

                page.update()
                return

            exito = recargar_tarjeta(
                tarjeta["id_tarjeta"],
                cantidad,
                descripcion.value,
                id_usuario=id_usuario_actual
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    f"Se recargaron "
                    f"${cantidad:,.0f}".replace(",", ".")
                )

                refrescar_tarjetas()

            else:

                mensaje_error.value = (
                    "No se pudo realizar la recarga"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.ADD_CARD,
                        color=VERDE
                    ),

                    ft.Text(
                        "Recargar tarjeta",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=420,
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Text(
                            tarjeta["cliente"],
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            (
                                "Saldo actual: "
                                f"${float(tarjeta['saldo']):,.0f}"
                            ).replace(",", "."),
                            color=TEXTO_SECUNDARIO
                        ),

                        monto,
                        descripcion,
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
                    "Recargar",
                    icon=ft.Icons.ADD,
                    bgcolor=VERDE,
                    color="#FFFFFF",
                    on_click=confirmar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # CAMBIAR ESTADO
    # =========================================================

    def alternar_estado(tarjeta):

        if tarjeta["estado"] == "Activa":
            nuevo_estado = "Bloqueada"
        else:
            nuevo_estado = "Activa"

        exito = cambiar_estado_tarjeta(
            tarjeta["id_tarjeta"],
            nuevo_estado
        )

        if exito:

            mostrar_mensaje(
                f"La tarjeta ahora está {nuevo_estado}"
            )

            refrescar_tarjetas()

        else:

            mostrar_mensaje(
                "No se pudo cambiar el estado",
                ROJO
            )

    def confirmar_eliminar_tarjeta(tarjeta):
        def eliminar(e):
            resultado = eliminar_tarjeta(
                tarjeta["id_tarjeta"],
                id_usuario_actual
            )
            page.pop_dialog()
            mostrar_mensaje(
                resultado["mensaje"],
                VERDE if resultado["exito"] else ROJO
            )
            if resultado["exito"]:
                refrescar_tarjetas()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar tarjeta definitivamente"),
                content=ft.Text(
                    f"¿Eliminar la tarjeta {tarjeta['uid']}? "
                    "Solo será posible si no tiene movimientos ni ventas."
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: page.pop_dialog()
                    ),
                    ft.ElevatedButton(
                        "Eliminar",
                        bgcolor=ROJO,
                        color="#FFFFFF",
                        on_click=eliminar
                    )
                ]
            )
        )

    # =========================================================
    # FILA TARJETA
    # =========================================================

    def crear_fila(tarjeta):

        estado = tarjeta.get(
            "estado",
            "Activa"
        )

        if estado == "Activa":
            color_estado = VERDE
            icono_estado = ft.Icons.CHECK_CIRCLE_OUTLINE
            texto_accion = "Bloquear"
            icono_accion = ft.Icons.LOCK_OUTLINE
            color_accion = ROJO

        else:
            color_estado = ROJO
            icono_estado = ft.Icons.LOCK_OUTLINE
            texto_accion = "Desbloquear"
            icono_accion = ft.Icons.LOCK_OPEN_OUTLINED
            color_accion = VERDE

        fecha = tarjeta.get(
            "fecha_activacion"
        )

        if hasattr(fecha, "strftime"):
            fecha_texto = fecha.strftime("%d/%m/%Y")
        else:
            fecha_texto = str(fecha or "")

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
                    # CLIENTE
                    ft.Container(
                        width=240,
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
                                        ft.Icons.CONTACTLESS_OUTLINED,
                                        color=MORADO,
                                        size=24
                                    )
                                ),

                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            tarjeta.get(
                                                "cliente",
                                                "Sin cliente"
                                            ),
                                            size=14,
                                            color=TEXTO_PRINCIPAL,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            f"ID tarjeta #{tarjeta['id_tarjeta']}",
                                            size=11,
                                            color=TEXTO_SECUNDARIO
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    # UID
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            tarjeta.get("uid", ""),
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # SALDO
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            f"${float(tarjeta.get('saldo', 0)):,.0f}".replace(
                                ",",
                                "."
                            ),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO_PRINCIPAL
                        )
                    ),

                    # ESTADO
                    ft.Container(
                        width=140,
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    icono_estado,
                                    color=color_estado,
                                    size=17
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

                    # FECHA
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            fecha_texto,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    ft.Container(expand=True),

                    # ACCIONES
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
                                on_click=lambda e, t=tarjeta: (
                                    ver_detalles(t)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ADD_CARD,
                                            size=18,
                                            color=VERDE
                                        ),

                                        ft.Text(
                                            "Recargar saldo",
                                            color=VERDE
                                        )
                                    ]
                                ),
                                on_click=lambda e, t=tarjeta: (
                                    abrir_recarga(t)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            icono_accion,
                                            size=18,
                                            color=color_accion
                                        ),

                                        ft.Text(
                                            texto_accion,
                                            color=color_accion
                                        )
                                    ]
                                ),
                                on_click=lambda e, t=tarjeta: (
                                    alternar_estado(t)
                                )
                            ),

                            *([ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.DELETE_FOREVER,
                                            size=18,
                                            color=ROJO
                                        ),
                                        ft.Text(
                                            "Eliminar definitivamente",
                                            color=ROJO
                                        )
                                    ]
                                ),
                                on_click=lambda e, t=tarjeta: (
                                    confirmar_eliminar_tarjeta(t)
                                )
                            )] if puede_eliminar else []),

                        ]
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR TARJETAS
    # =========================================================

    def cargar_tarjetas():

        lista_tarjetas.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for tarjeta in tarjetas:

            cliente = (
                tarjeta.get(
                    "cliente",
                    ""
                )
                .lower()
            )

            uid = (
                tarjeta.get(
                    "uid",
                    ""
                )
                .lower()
            )

            estado = tarjeta.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in cliente
                or texto in uid
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_estado
            ):

                lista_tarjetas.controls.append(
                    crear_fila(tarjeta)
                )

                encontrados += 1

        if encontrados == 0:

            lista_tarjetas.controls.append(
                ft.Container(
                    height=180,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,

                        controls=[
                            ft.Icon(
                                ft.Icons.CONTACTLESS_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron tarjetas",
                                size=15,
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

        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=filtro_estado,

            options=[
                ft.DropdownOption(
                    key="Activa",
                    text="Activas"
                ),

                ft.DropdownOption(
                    key="Bloqueada",
                    text="Bloqueadas"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_estado

            filtro_estado = estado_dropdown.value

            page.pop_dialog()

            cargar_tarjetas()
            page.update()

        def limpiar(e):

            nonlocal filtro_estado

            filtro_estado = "Activa"

            page.pop_dialog()

            cargar_tarjetas()
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
                        "Filtrar tarjetas",
                        weight=ft.FontWeight.BOLD
                    )
                ]
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
                    icon=ft.Icons.FILTER_ALT,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=aplicar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # TARJETA RESUMEN
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
                        bgcolor=ft.Colors.with_opacity(0.13, color),
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

    # =========================================================
    # ENCABEZADO
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
                    width=240,
                    content=ft.Text(
                        "CLIENTE",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=150,
                    content=ft.Text(
                        "UID",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,
                    content=ft.Text(
                        "SALDO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=140,
                    content=ft.Text(
                        "ESTADO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=120,
                    content=ft.Text(
                        "REGISTRO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(expand=True)
            ]
        )
    )

    # =========================================================
    # EVENTOS
    # =========================================================

    buscador.on_change = lambda e: (
        cargar_tarjetas(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_tarjetas()

    # =========================================================
    # CONTENIDO
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
                # CABECERA
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Tarjetas NFC",
                            size=30,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Administra las tarjetas y los saldos de los clientes",
                            size=14,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                ),

                # ESTADÍSTICAS
                ft.Row(
                    spacing=15,
                    controls=[
                        tarjeta_resumen(
                            "Tarjetas",
                            texto_total,
                            ft.Icons.CONTACTLESS_OUTLINED,
                            MORADO,
                            "Registradas"
                        ),

                        tarjeta_resumen(
                            "Activas",
                            texto_activas,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Disponibles para uso"
                        ),

                        tarjeta_resumen(
                            "Bloqueadas",
                            texto_bloqueadas,
                            ft.Icons.LOCK_OUTLINE,
                            ROJO,
                            "No pueden pagar"
                        ),

                        tarjeta_resumen(
                            "Saldo total",
                            texto_saldo_total,
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            ROSA,
                            "Entre todas las tarjetas"
                        )
                    ]
                ),

                # BUSCADOR
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

                encabezado_tabla,

                lista_tarjetas
            ]
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/tarjetas",
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
