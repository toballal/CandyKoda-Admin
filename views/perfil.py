import re

import flet as ft

from components.sidebar import sidebar
from database.perfil import actualizar_perfil


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
FONDO = "#0D0D14"
CARD = "#171722"
BORDE = "#34344A"
SECUNDARIO = "#C3C3CE"


def perfil_view(page: ft.Page):
    usuario = getattr(page, "usuario_actual", None) or {}
    nombre = ft.TextField(
        label="Nombre de usuario",
        value=usuario.get("nombre") or "",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_color=BORDE,
        focused_border_color=MORADO,
    )
    correo = ft.TextField(
        label="Correo electrónico",
        value=usuario.get("correo") or "",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_color=BORDE,
        focused_border_color=MORADO,
    )
    rol = ft.TextField(
        label="Rol",
        value=usuario.get("rol") or "Sin rol",
        read_only=True,
        prefix_icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
    )
    actual = ft.TextField(
        label="Contraseña actual",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )
    nueva = ft.TextField(
        label="Nueva contraseña (opcional)",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_RESET,
    )
    confirmar = ft.TextField(
        label="Confirmar nueva contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_RESET,
    )
    error = ft.Text("", color=ROSA, size=12)

    def guardar(e):
        nombre_valor = (nombre.value or "").strip()
        correo_valor = (correo.value or "").strip().lower()
        nueva_valor = nueva.value or ""
        confirmar_valor = confirmar.value or ""
        error.value = ""

        if not nombre_valor:
            error.value = "Ingrese el nombre de usuario"
        elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo_valor):
            error.value = "Ingrese un correo electrónico válido"
        elif nueva_valor and len(nueva_valor) < 8:
            error.value = "La nueva contraseña debe tener al menos 8 caracteres"
        elif nueva_valor != confirmar_valor:
            error.value = "Las nuevas contraseñas no coinciden"
        elif not (actual.value or ""):
            error.value = "Ingrese su contraseña actual para confirmar"

        if error.value:
            page.update()
            return

        resultado = actualizar_perfil(
            usuario["id_usuario"],
            nombre_valor,
            correo_valor,
            actual.value or "",
            nueva_valor or None,
        )
        if not resultado["exito"]:
            error.value = resultado["mensaje"]
            page.update()
            return

        page.usuario_actual["nombre"] = resultado["nombre"]
        page.usuario_actual["correo"] = resultado["correo"]
        actual.value = ""
        nueva.value = ""
        confirmar.value = ""
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(
                    resultado["mensaje"],
                    color="#FFFFFF",
                ),
                bgcolor=MORADO,
            )
        )
        page.update()

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=ft.Colors.with_opacity(0.85, FONDO),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=22,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Mi perfil",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            "Administra los datos de tu cuenta",
                            color=SECUNDARIO,
                        ),
                    ],
                ),
                ft.Container(
                    width=680,
                    padding=24,
                    bgcolor=CARD,
                    border=ft.Border.all(1, BORDE),
                    border_radius=16,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text(
                                "Información personal",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            nombre,
                            correo,
                            rol,
                            ft.Divider(color=BORDE),
                            ft.Text(
                                "Seguridad",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            actual,
                            nueva,
                            confirmar,
                            error,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    ft.ElevatedButton(
                                        "Guardar cambios",
                                        icon=ft.Icons.SAVE_OUTLINED,
                                        bgcolor=MORADO,
                                        color="#FFFFFF",
                                        on_click=guardar,
                                    )
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )
    return ft.View(
        route="/perfil",
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
