import flet as ft

from components.sidebar import sidebar

from database.mantenimiento import (
    obtener_mantenimientos,
    obtener_dispensadores,
    obtener_usuarios,
    registrar_mantenimiento,
    iniciar_mantenimiento,
    completar_mantenimiento
)


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


def mantenimientos_view(page: ft.Page):

    mantenimientos = obtener_mantenimientos()

    filtro_estado = None

    # =========================================================
    # CONTADORES
    # =========================================================

    texto_total = ft.Text(
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

    texto_proceso = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_completados = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar dispensador, tipo o responsable...",
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

    lista_mantenimientos = ft.Column(
        spacing=10
    )

    # =========================================================
    # FECHA
    # =========================================================

    def formatear_fecha(fecha):

        if fecha is None:
            return "-"

        if hasattr(fecha, "strftime"):
            return fecha.strftime(
                "%d/%m/%Y %H:%M"
            )

        return str(fecha)

    # =========================================================
    # ESTILO DEL ESTADO
    # =========================================================

    def obtener_estilo_estado(estado):

        if estado == "Pendiente":
            return (
                AMARILLO,
                ft.Icons.SCHEDULE_ROUNDED
            )

        elif estado == "En proceso":
            return (
                AZUL,
                ft.Icons.BUILD_ROUNDED
            )

        elif estado == "Completado":
            return (
                VERDE,
                ft.Icons.CHECK_CIRCLE_OUTLINE
            )

        return (
            TEXTO_SECUNDARIO,
            ft.Icons.HELP_OUTLINE
        )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        texto_total.value = str(
            len(mantenimientos)
        )

        texto_pendientes.value = str(
            sum(
                1
                for m in mantenimientos
                if m.get("estado") == "Pendiente"
            )
        )

        texto_proceso.value = str(
            sum(
                1
                for m in mantenimientos
                if m.get("estado") == "En proceso"
            )
        )

        texto_completados.value = str(
            sum(
                1
                for m in mantenimientos
                if m.get("estado") == "Completado"
            )
        )

    # =========================================================
    # RECARGAR
    # =========================================================

    def recargar():

        nonlocal mantenimientos

        mantenimientos = (
            obtener_mantenimientos()
        )

        actualizar_estadisticas()
        cargar_mantenimientos()

        page.update()

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
    # DETALLES
    # =========================================================

    def ver_detalles(mantenimiento):

        estado = mantenimiento.get(
            "estado",
            ""
        )

        color_estado, icono_estado = (
            obtener_estilo_estado(estado)
        )

        def dato(icono, titulo, valor):

            return ft.Container(
                padding=12,
                border_radius=10,
                bgcolor=COLOR_CARD_2,

                content=ft.Row(
                    spacing=12,

                    controls=[
                        ft.Icon(
                            icono,
                            size=20,
                            color=MORADO
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
                        f"Mantenimiento #{mantenimiento['id_mantenimiento']}",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=450,

                content=ft.Column(
                    tight=True,
                    spacing=10,

                    controls=[
                        dato(
                            ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                            "Dispensador",
                            mantenimiento.get(
                                "dispensador",
                                "-"
                            )
                        ),

                        dato(
                            ft.Icons.COOKIE_OUTLINED,
                            "Producto asignado",
                            mantenimiento.get(
                                "producto"
                            ) or "Sin producto"
                        ),

                        dato(
                            ft.Icons.BUILD_OUTLINED,
                            "Tipo",
                            mantenimiento.get(
                                "tipo"
                            ) or "-"
                        ),

                        dato(
                            ft.Icons.PERSON_OUTLINE,
                            "Responsable",
                            mantenimiento.get(
                                "usuario"
                            ) or "Sin asignar"
                        ),

                        dato(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            "Descripción",
                            mantenimiento.get(
                                "descripcion"
                            ) or "Sin descripción"
                        ),

                        dato(
                            ft.Icons.PLAY_CIRCLE_OUTLINE,
                            "Fecha de inicio",
                            formatear_fecha(
                                mantenimiento.get(
                                    "fecha_inicio"
                                )
                            )
                        ),

                        dato(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            "Fecha de finalización",
                            formatear_fecha(
                                mantenimiento.get(
                                    "fecha_fin"
                                )
                            )
                        )
                    ]
                )
            ),

            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e: (
                        page.pop_dialog()
                    )
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # REGISTRAR MANTENIMIENTO
    # =========================================================

    def abrir_registrar(e):

        dispensadores = obtener_dispensadores()
        usuarios = obtener_usuarios()

        campo_dispensador = ft.Dropdown(
            label="Dispensador",

            options=[
                ft.DropdownOption(
                    key=str(
                        d["id_dispensador"]
                    ),
                    text=(
                        f'{d["nombre"]} '
                        f'- Servo {d["numero_servo"]}'
                    )
                )
                for d in dispensadores
            ]
        )

        campo_usuario = ft.Dropdown(
            label="Responsable",

            options=[
                ft.DropdownOption(
                    key=str(
                        u["id_usuario"]
                    ),
                    text=u["nombre"]
                )
                for u in usuarios
            ]
        )

        campo_tipo = ft.Dropdown(
            label="Tipo de mantenimiento",

            options=[
                ft.DropdownOption(
                    key="Limpieza",
                    text="Limpieza"
                ),

                ft.DropdownOption(
                    key="Revisión",
                    text="Revisión"
                ),

                ft.DropdownOption(
                    key="Reparación",
                    text="Reparación"
                ),

                ft.DropdownOption(
                    key="Preventivo",
                    text="Preventivo"
                ),

                ft.DropdownOption(
                    key="Correctivo",
                    text="Correctivo"
                )
            ]
        )

        campo_descripcion = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=5,

            hint_text=(
                "Describe el mantenimiento "
                "que se realizará..."
            )
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            mensaje_error.value = ""

            if not campo_dispensador.value:

                mensaje_error.value = (
                    "Seleccione un dispensador."
                )

                page.update()
                return

            if not campo_tipo.value:

                mensaje_error.value = (
                    "Seleccione el tipo de mantenimiento."
                )

                page.update()
                return

            descripcion = (
                campo_descripcion.value or ""
            ).strip()

            if not descripcion:

                mensaje_error.value = (
                    "Ingrese una descripción."
                )

                page.update()
                return

            id_usuario = None

            if campo_usuario.value:

                id_usuario = int(
                    campo_usuario.value
                )

            resultado = registrar_mantenimiento(
                int(campo_dispensador.value),
                id_usuario,
                campo_tipo.value,
                descripcion
            )

            if resultado:

                page.pop_dialog()

                recargar()

                mostrar_mensaje(
                    "Mantenimiento registrado correctamente."
                )

            else:

                mensaje_error.value = (
                    "No se pudo registrar el mantenimiento."
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[
                    ft.Icon(
                        ft.Icons.BUILD_ROUNDED,
                        color=MORADO
                    ),

                    ft.Text(
                        "Registrar mantenimiento",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=430,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[
                        campo_dispensador,
                        campo_usuario,
                        campo_tipo,
                        campo_descripcion,
                        mensaje_error
                    ]
                )
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: (
                        page.pop_dialog()
                    )
                ),

                ft.ElevatedButton(
                    "Registrar",
                    icon=ft.Icons.ADD,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # INICIAR MANTENIMIENTO
    # =========================================================

    def iniciar(mantenimiento):

        if iniciar_mantenimiento(
            mantenimiento["id_mantenimiento"]
        ):

            recargar()

            mostrar_mensaje(
                "Mantenimiento iniciado.",
                AZUL
            )

        else:

            mostrar_mensaje(
                "No se pudo iniciar el mantenimiento.",
                ROJO
            )

    # =========================================================
    # COMPLETAR MANTENIMIENTO
    # =========================================================

    def completar(mantenimiento):

        if completar_mantenimiento(
            mantenimiento["id_mantenimiento"]
        ):

            recargar()

            mostrar_mensaje(
                "Mantenimiento completado."
            )

        else:

            mostrar_mensaje(
                "No se pudo completar el mantenimiento.",
                ROJO
            )

    # =========================================================
    # FILA
    # =========================================================

    def crear_fila(mantenimiento):

        estado = mantenimiento.get(
            "estado",
            ""
        )

        color_estado, icono_estado = (
            obtener_estilo_estado(estado)
        )

        opciones = [
            ft.PopupMenuItem(
                content=ft.Text(
                    "Ver detalles"
                ),

                on_click=lambda e, m=mantenimiento: (
                    ver_detalles(m)
                )
            )
        ]

        if estado == "Pendiente":

            opciones.append(
                ft.PopupMenuItem(
                    content=ft.Text(
                        "Iniciar mantenimiento",
                        color=AZUL
                    ),

                    on_click=lambda e, m=mantenimiento: (
                        iniciar(m)
                    )
                )
            )

        elif estado == "En proceso":

            opciones.append(
                ft.PopupMenuItem(
                    content=ft.Text(
                        "Marcar como completado",
                        color=VERDE
                    ),

                    on_click=lambda e, m=mantenimiento: (
                        completar(m)
                    )
                )
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
                right=18,
                bottom=14
            ),

            content=ft.Row(
                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    # =================================================
                    # DISPENSADOR
                    # =================================================

                    ft.Container(
                        width=170,

                        content=ft.Column(
                            spacing=2,

                            controls=[
                                ft.Text(
                                    mantenimiento.get(
                                        "dispensador",
                                        "-"
                                    ),
                                    size=13,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    (
                                        mantenimiento.get(
                                            "producto"
                                        )
                                        or "Sin producto"
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

                        content=ft.Text(
                            mantenimiento.get(
                                "tipo"
                            ) or "-",
                            size=12,
                            color=TEXTO_PRINCIPAL
                        )
                    ),

                    # =================================================
                    # RESPONSABLE
                    # =================================================

                    ft.Container(
                        width=160,

                        content=ft.Text(
                            mantenimiento.get(
                                "usuario"
                            ) or "Sin asignar",
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =================================================
                    # FECHA
                    # =================================================

                    ft.Container(
                        width=160,

                        content=ft.Text(
                            formatear_fecha(
                                mantenimiento.get(
                                    "fecha_inicio"
                                )
                            ),
                            size=11,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # =================================================
                    # ESTADO
                    # =================================================

                    ft.Container(
                        width=145,

                        content=ft.Row(
                            spacing=7,

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

                    # =================================================
                    # DESCRIPCIÓN
                    # =================================================

                    ft.Container(
                        expand=True,

                        content=ft.Text(
                            mantenimiento.get(
                                "descripcion"
                            ) or "-",

                            size=11,
                            color=TEXTO_SECUNDARIO,

                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ),

                    # =================================================
                    # OPCIONES
                    # =================================================

                    ft.Container(
                        width=55,

                        alignment=ft.Alignment.CENTER,

                        content=ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="Opciones",
                            items=opciones
                        )
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR MANTENIMIENTOS
    # =========================================================

    def cargar_mantenimientos():

        lista_mantenimientos.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for mantenimiento in mantenimientos:

            dispensador = str(
                mantenimiento.get(
                    "dispensador",
                    ""
                )
            ).lower()

            tipo = str(
                mantenimiento.get(
                    "tipo",
                    ""
                ) or ""
            ).lower()

            usuario = str(
                mantenimiento.get(
                    "usuario",
                    ""
                ) or ""
            ).lower()

            descripcion = str(
                mantenimiento.get(
                    "descripcion",
                    ""
                ) or ""
            ).lower()

            estado = mantenimiento.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in dispensador
                or texto in tipo
                or texto in usuario
                or texto in descripcion
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_estado
            ):

                lista_mantenimientos.controls.append(
                    crear_fila(
                        mantenimiento
                    )
                )

                encontrados += 1

        # =====================================================
        # SIN RESULTADOS
        # =====================================================

        if encontrados == 0:

            lista_mantenimientos.controls.append(
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

                        spacing=8,

                        controls=[
                            ft.Icon(
                                ft.Icons.BUILD_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No hay mantenimientos.",
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Registra un mantenimiento para comenzar.",
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

        campo_estado = ft.Dropdown(
            label="Estado",
            value=filtro_estado,

            options=[
                ft.DropdownOption(
                    key="Pendiente",
                    text="Pendiente"
                ),

                ft.DropdownOption(
                    key="En proceso",
                    text="En proceso"
                ),

                ft.DropdownOption(
                    key="Completado",
                    text="Completado"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_estado

            filtro_estado = campo_estado.value

            page.pop_dialog()

            cargar_mantenimientos()
            page.update()

        def limpiar(e):

            nonlocal filtro_estado

            filtro_estado = None

            page.pop_dialog()

            cargar_mantenimientos()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Filtrar mantenimientos"
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
                    on_click=lambda e: (
                        page.pop_dialog()
                    )
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
    # ENCABEZADO
    # =========================================================

    def titulo_columna(
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
                titulo_columna(
                    "DISPENSADOR",
                    170
                ),

                titulo_columna(
                    "TIPO",
                    150
                ),

                titulo_columna(
                    "RESPONSABLE",
                    160
                ),

                titulo_columna(
                    "FECHA",
                    160
                ),

                titulo_columna(
                    "ESTADO",
                    145
                ),

                titulo_columna(
                    "DESCRIPCIÓN",
                    expand=True
                ),

                titulo_columna(
                    "",
                    55
                )
            ]
        )
    )

    # =========================================================
    # EVENTOS
    # =========================================================

    buscador.on_change = lambda e: (
        cargar_mantenimientos(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_mantenimientos()

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

                # =================================================
                # CABECERA
                # =================================================

                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    controls=[
                        ft.Column(
                            spacing=4,

                            controls=[
                                ft.Text(
                                    "Mantenimientos",
                                    size=30,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "Gestiona las revisiones, limpiezas y reparaciones de los dispensadores",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.ElevatedButton(
                            "Registrar mantenimiento",
                            icon=ft.Icons.ADD,
                            height=45,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            on_click=abrir_registrar
                        )
                    ]
                ),

                # =================================================
                # ESTADÍSTICAS
                # =================================================

                ft.Row(
                    spacing=15,

                    controls=[
                        tarjeta_resumen(
                            "Total",
                            texto_total,
                            ft.Icons.BUILD_OUTLINED,
                            MORADO,
                            "Mantenimientos registrados"
                        ),

                        tarjeta_resumen(
                            "Pendientes",
                            texto_pendientes,
                            ft.Icons.SCHEDULE_ROUNDED,
                            AMARILLO,
                            "Esperando para comenzar"
                        ),

                        tarjeta_resumen(
                            "En proceso",
                            texto_proceso,
                            ft.Icons.BUILD_ROUNDED,
                            AZUL,
                            "En revisión actualmente"
                        ),

                        tarjeta_resumen(
                            "Completados",
                            texto_completados,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Trabajos terminados"
                        )
                    ]
                ),

                # =================================================
                # BUSCADOR
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
                # ENCABEZADO DE TABLA
                # =================================================

                encabezado,

                # =================================================
                # LISTA
                # =================================================

                lista_mantenimientos
            ]
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/mantenimientos",
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