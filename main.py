import flet as ft
import flet_video as fv
import asyncio
from time import monotonic

from views.login_view import login_view
from views.dashboard import dashboard_view
from views.ventas import historial_ventas_view
from views.productos import productos_view
from views.inventario import inventario_view
from views.tarjetas_nfc import tarjetas_view
from views.dispensadores import dispensadores_view
from views.usuarios import usuarios_view
from views.movimientos import movimientos_view
from views.logs import logs_view
from views.configuracion import configuracion_view
from views.mantenimiento import mantenimientos_view
from views.entregas import entregas_view
from views.categorias import categorias_view
from views.roles import roles_view
from views.perfil import perfil_view
from services.autorizacion import RUTAS_PROTEGIDAS, puede_acceder
from database.configuracion_sistema import obtener_configuraciones
from database.roles import preparar_permisos
from database.usuarios import preparar_usuarios

async def main(page: ft.Page):
    preparar_usuarios()
    preparar_permisos()
    page.configuracion_sistema = obtener_configuraciones()
    nombre_sistema = page.configuracion_sistema["nombre_sistema"]
    page.title = f"{nombre_sistema} Admin"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed="#9B59FF",
        font_family="Segoe UI",
        visual_density=ft.VisualDensity.COMFORTABLE,
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.FADE_FORWARDS,
            linux=ft.PageTransitionTheme.FADE_FORWARDS,
            macos=ft.PageTransitionTheme.CUPERTINO,
            android=ft.PageTransitionTheme.FADE_UPWARDS,
            ios=ft.PageTransitionTheme.CUPERTINO
        )
    )
    page.bgcolor = "#09090F"
    page.window.full_screen = True
    page.padding = 0
    page.spacing = 0
    page.usuario_actual = None
    page.ultima_carga_dashboard = 0.0

    preferencias = ft.SharedPreferences()
    page.services.append(preferencias)
    page.update()
    page.preferencias = preferencias
    page.sidebar_colapsado = bool(
        await preferencias.get("candy_koda.sidebar_colapsado")
        or False
    )

    def crear_video_fondo():
        mostrar_video = str(
            page.configuracion_sistema.get("video_fondo", "1")
        ).strip().casefold() in {"1", "true", "si", "sí"}

        if not mostrar_video:
            return ft.Container(
                expand=True,
                bgcolor="#09090F",
            )

        return fv.Video(
            playlist=[
                fv.VideoMedia("Fondo.mp4")
            ],
            autoplay=True,
            muted=True,
            controls=None,
            fit=ft.BoxFit.COVER,
            expand=True,
            playlist_mode=fv.PlaylistMode.LOOP
        )

    def route_change(e):
        if (
            page.route in RUTAS_PROTEGIDAS
            and page.usuario_actual is None
        ):
            page.route = "/"

        if (
            page.route in RUTAS_PROTEGIDAS
            and page.usuario_actual is not None
            and not puede_acceder(page.usuario_actual, page.route)
        ):
            page.route = "/dashboard"

        page.views.clear()

        if page.route != "/":
            page.views.append(
                ft.View(
                    route=page.route,
                    padding=0,
                    bgcolor="#0D0D14",
                    controls=[
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                tight=True,
                                spacing=14,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.ProgressRing(
                                        width=38,
                                        height=38,
                                        stroke_width=3,
                                        color="#9B59FF"
                                    ),
                                    ft.Text(
                                        "Cargando contenido...",
                                        size=12,
                                        color="#C3C3CE"
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
            page.update()

        if page.route == "/":
            view = login_view(page)

        elif page.route == "/dashboard":
            view = dashboard_view(page)
            page.ultima_carga_dashboard = monotonic()

        elif page.route == "/ventas":
            view = historial_ventas_view(page)

        elif page.route == "/productos":
            view = productos_view(page)

        elif page.route == "/categorias":
            view = categorias_view(page)

        elif page.route == "/inventario":
            view = inventario_view(page)

        elif page.route == "/tarjetas":
            view = tarjetas_view(page)

        elif page.route == "/dispensadores":
            view = dispensadores_view(page)

        elif page.route == "/usuarios":
            view = usuarios_view(page)

        elif page.route == "/roles":
            view = roles_view(page)

        elif page.route == "/perfil":
            view = perfil_view(page)

        elif page.route == "/movimientos":
            view = movimientos_view(page)

        elif page.route == "/logs":
            view = logs_view(page)

        elif page.route == "/configuracion":
            view = configuracion_view(page)

        elif page.route == "/mantenimientos":
            view = mantenimientos_view(page)

        elif page.route == "/entregas":
            view = entregas_view(page)
        else:
            return

        contenido = view.controls[0]

        view.padding = 0
        view.spacing = 0

        if page.route == "/":
            view.bgcolor = ft.Colors.TRANSPARENT
            view.controls = [
                ft.Stack(
                    expand=True,
                    controls=[
                        crear_video_fondo(),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=ft.Colors.with_opacity(0.75, "#09090F"),
                            content=contenido
                        )
                    ]
                )
            ]
        else:
            view.controls = [
                ft.Stack(
                    expand=True,
                    controls=[
                        crear_video_fondo(),
                        contenido,
                    ],
                )
            ]

        page.views.clear()
        page.views.append(view)
        page.update()

    page.on_route_change = route_change
    page.refrescar_vista_actual = lambda: route_change(None)

    def atajos_teclado(e: ft.KeyboardEvent):
        if e.ctrl and e.key.lower() == "r":
            route_change(None)
        elif e.ctrl and e.key.lower() == "d":
            page.go("/dashboard")
        elif e.ctrl and e.key.lower() == "l":
            page.go("/logs")
        elif e.ctrl and e.key.lower() == "i":
            page.go("/inventario")
        elif e.ctrl and e.key.lower() == "p":
            page.go("/perfil")

    page.on_keyboard_event = atajos_teclado

    async def refresco_automatico():
        while True:
            await asyncio.sleep(30)
            try:
                if page.route == "/dashboard" and page.usuario_actual is not None:
                    if monotonic() - page.ultima_carga_dashboard >= 30:
                        route_change(None)
            except RuntimeError as error:

                if "destroyed session" in str(error).lower():
                    return
                raise

    page.run_task(refresco_automatico)

    page.route = "/"
    route_change(None)


ft.run(
    main,
    assets_dir="assets"
)


"""
===========================
Agregar imagenes a los productos de forma sencialla.

===========================
"""
