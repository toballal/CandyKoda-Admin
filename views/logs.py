import flet as ft

from components.sidebar import sidebar
from database.logs import obtener_logs


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


def logs_view(page: ft.Page):

    logs = obtener_logs()

    filtro_tipo = None
    pagina_actual = 0
    por_pagina = 8
    orden_descendente = True

    # =========================================================
    # CONTADORES
    # =========================================================

    texto_total = ft.Text(
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

    texto_advertencias = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_info = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar por mensaje, usuario o acción...",
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

    lista_logs = ft.Column(
        spacing=10
    )

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
    # ESTILO SEGÚN TIPO
    # =========================================================

    def obtener_estilo(nivel):

        if nivel == "Error":
            return (
                ROJO,
                ft.Icons.ERROR_OUTLINE
            )

        elif nivel == "Advertencia":
            return (
                AMARILLO,
                ft.Icons.WARNING_AMBER_ROUNDED
            )

        else:
            return (
                AZUL,
                ft.Icons.INFO_OUTLINE
            )

    # =========================================================
    # ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        total = len(logs)

        errores = sum(
            1
            for log in logs
            if log.get("nivel") == "Error"
        )

        advertencias = sum(
            1
            for log in logs
            if log.get("nivel") == "Advertencia"
        )

        informacion = sum(
            1
            for log in logs
            if log.get("nivel") == "Informacion"
        )

        texto_total.value = str(total)
        texto_errores.value = str(errores)
        texto_advertencias.value = str(advertencias)
        texto_info.value = str(informacion)

    # =========================================================
    # VER DETALLES
    # =========================================================

    def ver_detalles(log):

        nivel = log.get(
            "nivel",
            "Informacion"
        )

        color_nivel, icono_nivel = obtener_estilo(
            nivel
        )

        fecha = log.get("fecha")

        if hasattr(fecha, "strftime"):
            fecha_texto = fecha.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        else:
            fecha_texto = str(fecha or "")

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
                        icono_nivel,
                        color=color_nivel
                    ),

                    ft.Text(
                        f"Log #{log['id_log']}",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=460,

                content=ft.Column(
                    tight=True,
                    spacing=12,

                    controls=[
                        ft.Container(
                            padding=ft.Padding(
                                left=12,
                                top=6,
                                right=12,
                                bottom=6
                            ),

                            border_radius=20,
                            bgcolor=ft.Colors.with_opacity(0.13, color_nivel),

                            content=ft.Text(
                                nivel,
                                color=color_nivel,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        dato(
                            ft.Icons.SCHEDULE_OUTLINED,
                            "Fecha",
                            fecha_texto
                        ),

                        dato(
                            ft.Icons.PERSON_OUTLINE,
                            "Usuario",
                            log.get("usuario") or "Sistema"
                        ),

                        dato(
                            ft.Icons.APPS_OUTLINED,
                            "Módulo",
                            log.get("modulo", "-")
                        ),

                        dato(
                            ft.Icons.BOLT_OUTLINED,
                            "Acción",
                            log.get("accion", "-")
                        ),

                        dato(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            "Descripción",
                            log.get("descripcion")
                            or "Sin descripción"
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

    def crear_fila(log):

        nivel = log.get(
            "nivel",
            "Informacion"
        )

        color_nivel, icono_nivel = obtener_estilo(
            nivel
        )

        modulo = log.get(
            "modulo",
            "-"
        )

        descripcion = (
            log.get("descripcion")
            or "-"
        )

        fecha = log.get("fecha")

        if hasattr(fecha, "strftime"):
            fecha_texto = fecha.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        else:
            fecha_texto = str(fecha or "")

        usuario = str(
            log.get("usuario") or "Sistema"
        )

        accion = str(
            log.get("accion") or "-"
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
                vertical_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[
                    # FECHA
                    ft.Container(
                        width=155,
                        content=ft.Text(
                            fecha_texto,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # TIPO
                    ft.Container(
                        width=145,

                        content=ft.Row(
                            spacing=7,

                            controls=[
                                ft.Icon(
                                    icono_nivel,
                                    size=17,
                                    color=color_nivel
                                ),

                                ft.Text(
                                    nivel,
                                    size=12,
                                    color=color_nivel,
                                    weight=ft.FontWeight.W_600
                                )
                            ]
                        )
                    ),

                    # USUARIO
                    ft.Container(
                        width=160,

                        content=ft.Text(
                            usuario,
                            size=13,
                            color=TEXTO_PRINCIPAL
                        )
                    ),

                    # ACCIÓN
                    ft.Container(
                        width=180,

                        content=ft.Text(
                            accion,
                            size=12,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    # MENSAJE
                    ft.Container(
                        expand=True,

                        content=ft.Text(
                            descripcion,
                            size=12,
                            color=TEXTO_SECUNDARIO,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ),

                    # ACCIONES
                    # Ancho fijo para que el ojo NO se corte
                    ft.Container(
                        width=60,
                        alignment=ft.Alignment.CENTER,

                        content=ft.IconButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            icon_color=MORADO,
                            icon_size=20,
                            tooltip="Ver detalles",

                            on_click=lambda e, l=log: (
                                ver_detalles(l)
                            )
                        )
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR LOGS
    # =========================================================

    def cargar_logs():

        nonlocal pagina_actual

        lista_logs.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        resultados = []

        for log in logs:

            descripcion = str(
                log.get(
                    "descripcion",
                    ""
                ) or ""
            ).lower()

            usuario = str(
                log.get(
                    "usuario",
                    ""
                ) or ""
            ).lower()

            accion = str(
                log.get(
                    "accion",
                    ""
                ) or ""
            ).lower()

            nivel = log.get(
                "nivel",
                ""
            )

            coincide_busqueda = (
                texto in descripcion
                or texto in usuario
                or texto in accion
            )

            coincide_tipo = (
                filtro_tipo is None
                or nivel == filtro_tipo
            )

            if (
                coincide_busqueda
                and coincide_tipo
            ):

                resultados.append(log)

        resultados.sort(
            key=lambda item: str(item.get("fecha", "")),
            reverse=orden_descendente
        )

        total_paginas = max(1, (len(resultados) + por_pagina - 1) // por_pagina)
        pagina_actual = min(pagina_actual, total_paginas - 1)
        inicio = pagina_actual * por_pagina

        for log in resultados[inicio:inicio + por_pagina]:
            lista_logs.controls.append(crear_fila(log))

        texto_pagina.value = f"Página {pagina_actual + 1} de {total_paginas} · {len(resultados)} registros"
        boton_anterior.disabled = pagina_actual == 0
        boton_siguiente.disabled = pagina_actual >= total_paginas - 1

        if len(resultados) == 0:

            lista_logs.controls.append(
                ft.Container(
                    height=190,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),

                        spacing=8,

                        controls=[
                            ft.Icon(
                                ft.Icons.HISTORY_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron registros",
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

    def cambiar_pagina(delta):
        nonlocal pagina_actual
        pagina_actual = max(0, pagina_actual + delta)
        cargar_logs()
        page.update()

    def cambiar_orden(e):
        nonlocal orden_descendente, pagina_actual
        orden_descendente = e.control.value == "recientes"
        pagina_actual = 0
        cargar_logs()
        page.update()

    boton_anterior.on_click = lambda e: cambiar_pagina(-1)
    boton_siguiente.on_click = lambda e: cambiar_pagina(1)

    # =========================================================
    # FILTROS
    # =========================================================

    def mostrar_filtros(e):

        tipo_dropdown = ft.Dropdown(
            label="Tipo",
            value=filtro_tipo,

            options=[
                ft.DropdownOption(
                    key="Informacion",
                    text="Información"
                ),

                ft.DropdownOption(
                    key="Advertencia",
                    text="Advertencia"
                ),

                ft.DropdownOption(
                    key="Error",
                    text="Error"
                ),

            ]
        )

        def aplicar(e):

            nonlocal filtro_tipo, pagina_actual

            filtro_tipo = (
                tipo_dropdown.value
            )
            pagina_actual = 0

            page.pop_dialog()

            cargar_logs()
            page.update()

        def limpiar(e):

            nonlocal filtro_tipo, pagina_actual

            filtro_tipo = None
            pagina_actual = 0

            page.pop_dialog()

            cargar_logs()
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
                        "Filtrar actividad",
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
    # ENCABEZADO TABLA
    # =========================================================

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
                ft.Container(
                    width=155,

                    content=ft.Text(
                        "FECHA",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=145,

                    content=ft.Text(
                        "NIVEL",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=160,

                    content=ft.Text(
                        "USUARIO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=180,

                    content=ft.Text(
                        "ACCIÓN",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    expand=True,

                    content=ft.Text(
                        "DESCRIPCIÓN",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                # Reserva espacio para el ojo
                ft.Container(
                    width=60,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Text(
                        "ACCIONES",
                        size=10,
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

    def buscar_logs(e):
        nonlocal pagina_actual
        pagina_actual = 0
        cargar_logs()
        page.update()

    buscador.on_change = buscar_logs

    actualizar_estadisticas()
    cargar_logs()

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
                            "Actividad del sistema",
                            size=30,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Consulta eventos, advertencias y errores registrados",
                            size=14,
                            color=TEXTO_SECUNDARIO
                        )
                    ]
                ),

                # RESUMEN
                ft.Row(
                    spacing=15,

                    controls=[
                        tarjeta_resumen(
                            "Registros",
                            texto_total,
                            ft.Icons.HISTORY_OUTLINED,
                            MORADO,
                            "Eventos registrados"
                        ),

                        tarjeta_resumen(
                            "Errores",
                            texto_errores,
                            ft.Icons.ERROR_OUTLINE,
                            ROJO,
                            "Requieren atención"
                        ),

                        tarjeta_resumen(
                            "Advertencias",
                            texto_advertencias,
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            AMARILLO,
                            "Revisar sistema"
                        ),

                        tarjeta_resumen(
                            "Información",
                            texto_info,
                            ft.Icons.INFO_OUTLINE,
                            AZUL,
                            "Actividad normal"
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
                        ),

                        ft.Dropdown(
                            value="recientes",
                            width=175,
                            height=45,
                            text_size=12,
                            bgcolor=COLOR_CARD,
                            border_color=COLOR_BORDE,
                            on_select=cambiar_orden,
                            options=[
                                ft.DropdownOption(key="recientes", text="Más recientes"),
                                ft.DropdownOption(key="antiguos", text="Más antiguos")
                            ]
                        )
                    ]
                ),

                encabezado,

                lista_logs,

                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[boton_anterior, texto_pagina, boton_siguiente]
                )
            ]
        )
    )

    return ft.View(
        route="/logs",
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
