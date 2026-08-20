import flet as ft
from services.autorizacion import puede_acceder


def sidebar(page: ft.Page):

    ROSA = "#FF4FA3"
    MORADO = "#9B59FF"
    ROJO = "#FF4FA3"

    COLOR_FONDO = "#0F0F18"
    COLOR_CARD = "#171722"
    COLOR_BORDE = "#2E2E42"
    colapsado = bool(getattr(page, "sidebar_colapsado", False))

    # =========================
    # NAVEGACIÓN
    # =========================

    def navegar(ruta):
        if page.route != ruta:
            page.go(ruta)

    def cerrar_sesion(e):
        page.usuario_actual = None
        page.go("/")

    async def guardar_preferencia_sidebar(valor):
        preferencias = getattr(page, "preferencias", None)
        if preferencias:
            await preferencias.set(
                "candy_koda.sidebar_colapsado",
                valor
            )

    def alternar_sidebar(e):
        page.sidebar_colapsado = not colapsado
        page.run_task(
            guardar_preferencia_sidebar,
            page.sidebar_colapsado
        )
        refrescar = getattr(page, "refrescar_vista_actual", None)
        if refrescar:
            refrescar()

    # =========================
    # OPCIÓN DEL MENÚ
    # =========================

    def opcion_menu(icono, texto, ruta):

        if not puede_acceder(page.usuario_actual, ruta):
            return ft.Container(visible=False)

        seleccionado = page.route == ruta

        def al_pasar(e):
            if not seleccionado:
                e.control.bgcolor = (
                    ft.Colors.with_opacity(0.08, MORADO)
                    if e.data == "true"
                    else ft.Colors.TRANSPARENT
                )
                e.control.update()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        border_radius=9,
                        bgcolor=(
                            ft.Colors.with_opacity(0.14, MORADO)
                            if seleccionado
                            else "#1D1D29"
                        ),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icono,
                            size=18,
                            color=MORADO if seleccionado else "#B9B9C9"
                        )
                    ),

                    ft.Text(
                        texto,
                        size=13,
                        color="#FFFFFF" if seleccionado else "#C7C7D4",
                        weight=(
                            ft.FontWeight.W_600
                            if seleccionado
                            else ft.FontWeight.W_500
                        )
                    ) if not colapsado else ft.Container()
                ],
                spacing=12
            ),

            padding=ft.Padding(
                left=10,
                top=7,
                right=12,
                bottom=7
            ),

            gradient=(
                ft.LinearGradient(
                    colors=[ft.Colors.with_opacity(0.16, MORADO), ft.Colors.with_opacity(0.07, ROSA)]
                )
                if seleccionado else None
            ),

            border=ft.Border(
                left=ft.BorderSide(
                    3,
                    MORADO if seleccionado else ft.Colors.TRANSPARENT
                )
            ),
            border_radius=11,
            ink=True,
            tooltip=texto if colapsado else None,
            on_hover=al_pasar,

            on_click=lambda e: navegar(ruta)
        )

    # =========================
    # TÍTULO DE SECCIÓN
    # =========================

    def titulo_seccion(texto, rutas):

        if not any(
            puede_acceder(page.usuario_actual, ruta)
            for ruta in rutas
        ):
            return ft.Container(visible=False)

        if colapsado:
            return ft.Container(height=8)

        return ft.Container(
            margin=ft.Margin(
                left=8,
                top=12,
                bottom=5
            ),

            content=ft.Text(
                texto,
                size=10,
                color="#85859A",
                weight=ft.FontWeight.BOLD
            )
        )

    # =========================
    # SIDEBAR
    # =========================

    return ft.Container(
        width=88 if colapsado else 270,
        animate=ft.Animation(240, ft.AnimationCurve.EASE_OUT),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#141421", COLOR_FONDO]
        ),
        border=ft.Border(
            right=ft.BorderSide(1, COLOR_BORDE)
        ),
        padding=ft.Padding(left=16, top=18, right=16, bottom=16),

        content=ft.Column(
            controls=[

                # =====================
                # LOGO
                # =====================

                ft.Container(
                    padding=10,
                    bgcolor=COLOR_CARD,
                    border=ft.Border.all(1, COLOR_BORDE),
                    border_radius=15,
                    content=ft.Row(
                        controls=[
                            ft.Image(
                                src="LogoCandyKodaVerySimple.svg",
                                width=40,
                                height=40
                            ),

                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Candy Koda",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF"
                                    ),

                                    ft.Text(
                                        "ADMIN",
                                        size=11,
                                        color=ROSA,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ],
                                spacing=0
                            ) if not colapsado else ft.Container()
                        ]
                    ),

                    margin=ft.Margin(bottom=12)
                ),

                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.IconButton(
                        icon=(
                            ft.Icons.CHEVRON_RIGHT_ROUNDED
                            if colapsado
                            else ft.Icons.CHEVRON_LEFT_ROUNDED
                        ),
                        icon_color=MORADO,
                        tooltip=(
                            "Expandir menú"
                            if colapsado
                            else "Contraer menú"
                        ),
                        on_click=alternar_sidebar
                    )
                ),

                # =====================
                # GENERAL
                # =====================

                titulo_seccion(
                    "GENERAL",
                    {"/dashboard", "/ventas"}
                ),

                opcion_menu(
                    ft.Icons.DASHBOARD_ROUNDED,
                    "Dashboard",
                    "/dashboard"
                ),

                opcion_menu(
                    ft.Icons.RECEIPT_LONG_ROUNDED,
                    "Ventas",
                    "/ventas"
                ),

                # =====================
                # GESTIÓN
                # =====================

                titulo_seccion(
                    "GESTIÓN",
                    {
                        "/productos",
                        "/categorias",
                        "/inventario",
                        "/dispensadores",
                    }
                ),

                opcion_menu(
                    ft.Icons.COOKIE_ROUNDED,
                    "Productos",
                    "/productos"
                ),

                opcion_menu(
                    ft.Icons.CATEGORY_OUTLINED,
                    "Categorías",
                    "/categorias"
                ),

                opcion_menu(
                    ft.Icons.INVENTORY_2_ROUNDED,
                    "Inventario",
                    "/inventario"
                ),

                opcion_menu(
                    ft.Icons.PRECISION_MANUFACTURING_ROUNDED,
                    "Dispensadores",
                    "/dispensadores"
                ),

                # =====================
                # TARJETAS
                # =====================

                titulo_seccion(
                    "TARJETAS",
                    {"/tarjetas", "/movimientos"}
                ),

                opcion_menu(
                    ft.Icons.CREDIT_CARD_ROUNDED,
                    "Tarjetas NFC",
                    "/tarjetas"
                ),

                opcion_menu(
                    ft.Icons.SWAP_HORIZ_ROUNDED,
                    "Movimientos",
                    "/movimientos"
                ),

                # =====================
                # SISTEMA
                # =====================

                titulo_seccion(
                    "SISTEMA",
                    {
                        "/usuarios",
                        "/roles",
                        "/logs",
                        "/configuracion",
                        "/mantenimientos",
                        "/entregas",
                    }
                ),

                opcion_menu(
                    ft.Icons.PEOPLE_ALT_ROUNDED,
                    "Usuarios",
                    "/usuarios"
                ),

                opcion_menu(
                    ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                    "Roles",
                    "/roles"
                ),

                opcion_menu(
                    ft.Icons.HISTORY_ROUNDED,
                    "Logs",
                    "/logs"
                ),

                opcion_menu(
                    ft.Icons.SETTINGS_ROUNDED,
                    "Configuración",
                    "/configuracion"
                ),

                opcion_menu(
                    ft.Icons.BUILD_ROUNDED,
                    "Mantenimientos",
                    "/mantenimientos"
                ),

                opcion_menu(
                    ft.Icons.LOCAL_SHIPPING_ROUNDED,
                    "Entregas",
                    "/entregas"
                ),

                # Empuja cerrar sesión hacia abajo
                ft.Container(
                    expand=True
                ),

                opcion_menu(
                    ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                    "Mi perfil",
                    "/perfil"
                ),

                ft.Divider(
                    color=COLOR_BORDE
                ),

                # =====================
                # CERRAR SESIÓN
                # =====================

                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.06, ROJO),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.19, ROJO)),
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.LOGOUT_ROUNDED,
                                color=ROJO
                            ),

                            ft.Text(
                                "Cerrar sesión",
                                color=ROJO,
                                weight=ft.FontWeight.W_500
                            ) if not colapsado else ft.Container()
                        ],

                        spacing=15
                    ),

                    padding=ft.Padding.symmetric(horizontal=13, vertical=11),
                    border_radius=11,
                    ink=True,

                    on_click=cerrar_sesion
                )
            ],

            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
    )
