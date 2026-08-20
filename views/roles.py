import flet as ft

from components.sidebar import sidebar
from database.roles import (
    MODULOS,
    obtener_roles_admin,
    guardar_rol,
    eliminar_rol,
)


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
FONDO = "#0D0D14"
CARD = "#171722"
CARD_2 = "#202031"
BORDE = "#34344A"
SECUNDARIO = "#C3C3CE"


def roles_view(page: ft.Page):
    roles = obtener_roles_admin()
    usuario = getattr(page, "usuario_actual", None) or {}
    id_usuario = usuario.get("id_usuario")
    lista = ft.Column(spacing=10)
    buscador = ft.TextField(
        hint_text="Buscar rol...",
        prefix_icon=ft.Icons.SEARCH,
        width=360,
        height=45,
        bgcolor=CARD,
        border_color=BORDE,
    )

    def mensaje(texto, color=VERDE):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto, color="#FFFFFF"),
                bgcolor=color,
            )
        )

    def refrescar():
        nonlocal roles
        roles = obtener_roles_admin()
        cargar()
        page.update()

    def abrir_formulario(rol=None):
        rol = rol or {}
        nombre = ft.TextField(
            label="Nombre",
            value=rol.get("nombre") or "",
            prefix_icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
            disabled=str(rol.get("nombre") or "").strip().casefold()
            in {"administrador", "admin"},
        )
        descripcion = ft.TextField(
            label="Descripción",
            value=rol.get("descripcion") or "",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        es_admin = str(rol.get("nombre") or "").strip().casefold() in {
            "administrador", "admin"
        }
        actuales = set(rol.get("permisos") or [])
        checks = {
            ruta: ft.Checkbox(
                label=nombre_modulo,
                value=True if es_admin else ruta in actuales,
                disabled=es_admin or ruta == "/dashboard",
            )
            for ruta, nombre_modulo in MODULOS.items()
        }
        checks["/dashboard"].value = True
        error = ft.Text("", color=ROSA, size=12)

        def guardar(e):
            nombre_valor = (nombre.value or "").strip()
            descripcion_valor = (descripcion.value or "").strip()
            if not nombre_valor:
                error.value = "Ingrese el nombre del rol"
                page.update()
                return
            rutas = {
                ruta for ruta, check in checks.items() if check.value
            }
            resultado = guardar_rol(
                rol.get("id_rol"),
                nombre_valor,
                descripcion_valor,
                rutas,
                id_usuario,
            )
            if resultado["exito"]:
                page.pop_dialog()
                mensaje(resultado["mensaje"])
                refrescar()
            else:
                error.value = resultado["mensaje"]
                page.update()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar rol" if rol else "Nuevo rol"),
                content=ft.Container(
                    width=620,
                    content=ft.Column(
                        tight=True,
                        spacing=14,
                        controls=[
                            nombre,
                            descripcion,
                            ft.Text(
                                "Módulos permitidos",
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(
                                height=260,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=list(checks.values()),
                                ),
                            ),
                            error,
                        ],
                    ),
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.ElevatedButton(
                        "Guardar",
                        icon=ft.Icons.SAVE_OUTLINED,
                        bgcolor=MORADO,
                        color="#FFFFFF",
                        on_click=guardar,
                    ),
                ],
            )
        )

    def confirmar_eliminar(rol):
        def eliminar(e):
            resultado = eliminar_rol(rol["id_rol"], id_usuario)
            page.pop_dialog()
            mensaje(
                resultado["mensaje"],
                VERDE if resultado["exito"] else ROSA,
            )
            if resultado["exito"]:
                refrescar()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar rol definitivamente"),
                content=ft.Text(
                    f"¿Eliminar '{rol['nombre']}'? Solo será posible "
                    "si no tiene usuarios asignados."
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.ElevatedButton(
                        "Eliminar",
                        bgcolor=ROSA,
                        color="#FFFFFF",
                        on_click=eliminar,
                    ),
                ],
            )
        )

    def fila(rol):
        permisos = rol.get("permisos") or []
        return ft.Container(
            padding=18,
            bgcolor=CARD,
            border=ft.Border.all(1, BORDE),
            border_radius=12,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                        color=MORADO,
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                rol["nombre"],
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                rol.get("descripcion") or "Sin descripción",
                                color=SECUNDARIO,
                                size=12,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{rol.get('usuarios', 0)} usuarios",
                        color=SECUNDARIO,
                    ),
                    ft.Text(
                        f"{len(permisos)} módulos",
                        color=SECUNDARIO,
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text("Editar permisos"),
                                on_click=lambda e, r=rol: abrir_formulario(r),
                            ),
                            ft.PopupMenuItem(
                                content=ft.Text(
                                    "Eliminar definitivamente",
                                    color=ROSA,
                                ),
                                on_click=lambda e, r=rol: (
                                    confirmar_eliminar(r)
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def cargar():
        texto = (buscador.value or "").strip().casefold()
        lista.controls.clear()
        resultados = [
            rol for rol in roles
            if texto in rol["nombre"].casefold()
            or texto in str(rol.get("descripcion") or "").casefold()
        ]
        lista.controls.extend(fila(rol) for rol in resultados)
        if not resultados:
            lista.controls.append(
                ft.Container(
                    height=150,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "No se encontraron roles",
                        color=SECUNDARIO,
                    ),
                )
            )

    buscador.on_change = lambda e: (cargar(), page.update())
    cargar()

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=ft.Colors.with_opacity(0.85, FONDO),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=22,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Roles y permisos",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "Administra el acceso a cada módulo",
                                    color=SECUNDARIO,
                                ),
                            ],
                        ),
                        ft.ElevatedButton(
                            "Nuevo rol",
                            icon=ft.Icons.ADD,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            on_click=lambda e: abrir_formulario(),
                        ),
                    ],
                ),
                buscador,
                lista,
            ],
        ),
    )
    return ft.View(
        route="/roles",
        padding=0,
        spacing=0,
        bgcolor=ft.Colors.TRANSPARENT,
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[sidebar(page), contenido],
            )
        ],
    )
