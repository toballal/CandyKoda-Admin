import flet as ft
import re

from components.sidebar import sidebar

from database.usuarios import (
    obtener_usuarios,
    obtener_roles,
    agregar_usuario,
    actualizar_usuario,
    cambiar_estado_usuario,
    cambiar_contrasena,
    eliminar_usuario,
    anonimizar_usuario
)
from services.autorizacion import puede_realizar


# =========================================================
# COLORES
# =========================================================

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


def correo_valido(correo):
    return bool(
        re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+",
            correo,
        )
    )


def usuarios_view(page: ft.Page):

    usuarios = obtener_usuarios()
    usuario_actual = getattr(page, "usuario_actual", None) or {}
    id_usuario_actual = usuario_actual.get("id_usuario")
    puede_eliminar = puede_realizar(usuario_actual, "eliminar_usuario")
    puede_anonimizar = puede_realizar(
        usuario_actual,
        "anonimizar_usuario"
    )

    filtro_rol = None
    filtro_estado = "Activo"

    # =========================================================
    # CONTADORES
    # =========================================================

    texto_total = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_activos = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_inactivos = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    texto_admin = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar por usuario, correo o rol...",
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

    lista_usuarios = ft.Column(
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

        total = len(usuarios)

        activos = sum(
            1
            for usuario in usuarios
            if usuario.get("estado") == "Activo"
        )

        inactivos = sum(
            1
            for usuario in usuarios
            if usuario.get("estado") == "Inactivo"
        )

        administradores = sum(
            1
            for usuario in usuarios
            if usuario.get("rol") == "administrador"
        )

        texto_total.value = str(total)
        texto_activos.value = str(activos)
        texto_inactivos.value = str(inactivos)
        texto_admin.value = str(administradores)

    # =========================================================
    # REFRESCAR
    # =========================================================

    def refrescar_usuarios():

        nonlocal usuarios

        usuarios = obtener_usuarios()

        actualizar_estadisticas()
        cargar_usuarios()

        page.update()

    # =========================================================
    # AGREGAR USUARIO
    # =========================================================

    def nuevo_usuario(e):

        roles = obtener_roles()

        nombre = ft.TextField(
            label="Usuario",
            hint_text="Ej: cristobal",
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )

        correo = ft.TextField(
            label="Correo electrónico",
            hint_text="Ej: usuario@correo.cl",
            keyboard_type=ft.KeyboardType.EMAIL,
            prefix_icon=ft.Icons.EMAIL_OUTLINED
        )

        contrasena = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE
        )

        confirmar = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_RESET
        )

        rol = ft.Dropdown(
            label="Rol",
            hint_text="Selecciona un rol",
            options=[
                ft.DropdownOption(
                    key=str(r["id_rol"]),
                    text=r["nombre"]
                )
                for r in roles
            ]
        )

        estado = ft.Dropdown(
            label="Estado",
            value="Activo",
            options=[
                ft.DropdownOption(
                    key="Activo",
                    text="Activo"
                ),
                ft.DropdownOption(
                    key="Inactivo",
                    text="Inactivo"
                )
            ]
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            nombre_valor = (
                nombre.value or ""
            ).strip()

            correo_valor = (
                correo.value or ""
            ).strip().lower()

            contrasena_valor = (
                contrasena.value or ""
            )

            confirmar_valor = (
                confirmar.value or ""
            )

            mensaje_error.value = ""

            if not nombre_valor:
                mensaje_error.value = "Ingrese el usuario"
                page.update()
                return

            if not correo_valor:
                mensaje_error.value = "Ingrese el correo electrónico"
                page.update()
                return

            if len(correo_valor) > 255 or not correo_valido(correo_valor):
                mensaje_error.value = "Ingrese un correo electrónico válido"
                page.update()
                return

            if not contrasena_valor:
                mensaje_error.value = "Ingrese una contraseña"
                page.update()
                return

            if len(contrasena_valor) < 4:
                mensaje_error.value = (
                    "La contraseña debe tener al menos 4 caracteres"
                )
                page.update()
                return

            if contrasena_valor != confirmar_valor:
                mensaje_error.value = (
                    "Las contraseñas no coinciden"
                )
                page.update()
                return

            if rol.value is None:
                mensaje_error.value = "Seleccione un rol"
                page.update()
                return

            exito = agregar_usuario(
                nombre_valor,
                correo_valor,
                contrasena_valor,
                int(rol.value),
                estado.value
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    f"Usuario {nombre_valor} creado correctamente"
                )

                refrescar_usuarios()

            else:

                mensaje_error.value = (
                    "No se pudo crear el usuario"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.13, MORADO),
                        alignment=ft.Alignment.CENTER,

                        content=ft.Icon(
                            ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                            color=MORADO
                        )
                    ),

                    ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text(
                                "Agregar usuario",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Crea una cuenta de acceso al sistema",
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                ]
            ),

            content=ft.Container(
                width=450,

                content=ft.Column(
                    tight=True,
                    spacing=14,

                    controls=[
                        nombre,
                        correo,
                        contrasena,
                        confirmar,

                        ft.Row(
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=rol
                                ),

                                ft.Container(
                                    expand=True,
                                    content=estado
                                )
                            ]
                        ),

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
                    "Crear usuario",
                    icon=ft.Icons.ADD,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # VER DETALLES
    # =========================================================

    def ver_detalles(usuario):

        estado = usuario.get(
            "estado",
            "Activo"
        )

        if estado == "Activo":
            color_estado = VERDE
        else:
            color_estado = TEXTO_SECUNDARIO

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
                        ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        usuario.get(
                            "nombre",
                            "Usuario"
                        ),
                        size=20,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=420,

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
                            ft.Icons.BADGE_OUTLINED,
                            "ID usuario",
                            usuario.get(
                                "id_usuario",
                                ""
                            )
                        ),

                        dato(
                            ft.Icons.PERSON_OUTLINE,
                            "Usuario",
                            usuario.get(
                                "nombre",
                                ""
                            )
                        ),

                        dato(
                            ft.Icons.EMAIL_OUTLINED,
                            "Correo",
                            usuario.get("correo") or "Sin correo"
                        ),

                        dato(
                            ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                            "Rol",
                            usuario.get(
                                "rol",
                                "Sin rol"
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
    # EDITAR USUARIO
    # =========================================================

    def editar_usuario(usuario):

        roles = obtener_roles()

        nombre = ft.TextField(
            label="Usuario",
            value=usuario.get(
                "nombre",
                ""
            ),
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )

        correo = ft.TextField(
            label="Correo electrónico",
            value=usuario.get("correo") or "",
            keyboard_type=ft.KeyboardType.EMAIL,
            prefix_icon=ft.Icons.EMAIL_OUTLINED
        )

        rol = ft.Dropdown(
            label="Rol",
            value=str(
                usuario.get(
                    "id_rol",
                    ""
                )
            ),

            options=[
                ft.DropdownOption(
                    key=str(r["id_rol"]),
                    text=r["nombre"]
                )
                for r in roles
            ]
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            nombre_valor = (
                nombre.value or ""
            ).strip()

            correo_valor = (
                correo.value or ""
            ).strip().lower()

            if not nombre_valor:
                mensaje_error.value = "Ingrese el usuario"
                page.update()
                return

            if not correo_valor:
                mensaje_error.value = "Ingrese el correo electrónico"
                page.update()
                return

            if len(correo_valor) > 255 or not correo_valido(correo_valor):
                mensaje_error.value = "Ingrese un correo electrónico válido"
                page.update()
                return

            if rol.value is None:
                mensaje_error.value = "Seleccione un rol"
                page.update()
                return

            exito = actualizar_usuario(
                usuario["id_usuario"],
                nombre_valor,
                correo_valor,
                int(rol.value)
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    "Usuario actualizado correctamente"
                )

                refrescar_usuarios()

            else:

                mensaje_error.value = (
                    "No se pudo actualizar el usuario"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[
                    ft.Icon(
                        ft.Icons.EDIT_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        "Editar usuario",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=400,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[
                        nombre,
                        correo,
                        rol,
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
                    "Guardar cambios",
                    icon=ft.Icons.SAVE_OUTLINED,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # CAMBIAR CONTRASEÑA
    # =========================================================

    def abrir_cambiar_contrasena(usuario):

        nueva = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE
        )

        confirmar = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_RESET
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def guardar(e):

            nueva_valor = (
                nueva.value or ""
            )

            confirmar_valor = (
                confirmar.value or ""
            )

            if not nueva_valor:
                mensaje_error.value = (
                    "Ingrese la nueva contraseña"
                )
                page.update()
                return

            if len(nueva_valor) < 4:
                mensaje_error.value = (
                    "La contraseña debe tener al menos 4 caracteres"
                )
                page.update()
                return

            if nueva_valor != confirmar_valor:
                mensaje_error.value = (
                    "Las contraseñas no coinciden"
                )
                page.update()
                return

            exito = cambiar_contrasena(
                usuario["id_usuario"],
                nueva_valor
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    "Contraseña actualizada correctamente"
                )

            else:

                mensaje_error.value = (
                    "No se pudo cambiar la contraseña"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[
                    ft.Icon(
                        ft.Icons.PASSWORD_OUTLINED,
                        color=MORADO
                    ),

                    ft.Text(
                        "Cambiar contraseña",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=400,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[
                        ft.Text(
                            usuario["nombre"],
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),

                        nueva,
                        confirmar,
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
                    "Cambiar contraseña",
                    icon=ft.Icons.LOCK_RESET,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # CAMBIAR ESTADO
    # =========================================================

    def alternar_estado(usuario):

        if usuario["estado"] == "Activo":
            nuevo_estado = "Inactivo"
        else:
            nuevo_estado = "Activo"

        exito = cambiar_estado_usuario(
            usuario["id_usuario"],
            nuevo_estado
        )

        if exito:

            mostrar_mensaje(
                f"{usuario['nombre']} ahora está {nuevo_estado}",
                VERDE if nuevo_estado == "Activo" else AMARILLO
            )

            refrescar_usuarios()

        else:

            mostrar_mensaje(
                "No se pudo cambiar el estado del usuario",
                ROJO
            )

    def confirmar_eliminar_usuario(usuario):
        def eliminar(e):
            resultado = eliminar_usuario(
                usuario["id_usuario"],
                id_usuario_actual
            )
            page.pop_dialog()
            mostrar_mensaje(
                resultado["mensaje"],
                VERDE if resultado["exito"] else ROJO
            )
            if resultado["exito"]:
                refrescar_usuarios()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar usuario definitivamente"),
                content=ft.Text(
                    f"¿Eliminar a {usuario['nombre']}? "
                    "Solo será posible si no tiene historial."
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

    def confirmar_anonimizar_usuario(usuario):
        def anonimizar(e):
            resultado = anonimizar_usuario(
                usuario["id_usuario"],
                id_usuario_actual
            )
            page.pop_dialog()
            mostrar_mensaje(
                resultado["mensaje"],
                VERDE if resultado["exito"] else ROJO
            )
            if resultado["exito"]:
                refrescar_usuarios()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Retirar y anonimizar usuario"),
                content=ft.Text(
                    f"Se reemplazarán el nombre, correo y contraseña de "
                    f"{usuario['nombre']}. El historial se conservará."
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: page.pop_dialog()
                    ),
                    ft.ElevatedButton(
                        "Retirar y anonimizar",
                        bgcolor=AMARILLO,
                        color="#151519",
                        on_click=anonimizar
                    )
                ]
            )
        )

    # =========================================================
    # FILA
    # =========================================================

    def crear_fila(usuario):

        estado = usuario.get(
            "estado",
            "Activo"
        )

        rol = usuario.get(
            "rol",
            "Sin rol"
        )

        if estado == "Activo":

            color_estado = VERDE
            icono_estado = ft.Icons.CHECK_CIRCLE_OUTLINE

            texto_accion = "Desactivar"
            icono_accion = ft.Icons.BLOCK
            color_accion = AMARILLO

        else:

            color_estado = TEXTO_SECUNDARIO
            icono_estado = ft.Icons.BLOCK

            texto_accion = "Activar"
            icono_accion = ft.Icons.CHECK_CIRCLE_OUTLINE
            color_accion = VERDE

        if rol == "Administrador":
            color_rol = MORADO
            icono_rol = ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED

        else:
            color_rol = ROSA
            icono_rol = ft.Icons.PERSON_OUTLINE

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
                    # USUARIO
                    ft.Container(
                        width=300,

                        content=ft.Row(
                            spacing=12,

                            controls=[
                                ft.Container(
                                    width=46,
                                    height=46,
                                    border_radius=23,
                                    bgcolor=ft.Colors.with_opacity(
                                        0.09,
                                        MORADO
                                    ),
                                    alignment=ft.Alignment.CENTER,

                                    content=ft.Icon(
                                        ft.Icons.PERSON,
                                        color=MORADO,
                                        size=24
                                    )
                                ),

                                ft.Column(
                                    spacing=2,

                                    controls=[
                                        ft.Text(
                                            usuario.get(
                                                "nombre",
                                                "Sin nombre"
                                            ),
                                            size=14,
                                            color=TEXTO_PRINCIPAL,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            usuario.get("correo")
                                            or f"ID #{usuario['id_usuario']}",
                                            size=11,
                                            color=TEXTO_SECUNDARIO
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    # ROL
                    ft.Container(
                        width=220,

                        content=ft.Row(
                            spacing=7,

                            controls=[
                                ft.Icon(
                                    icono_rol,
                                    size=18,
                                    color=color_rol
                                ),

                                ft.Text(
                                    rol,
                                    size=13,
                                    color=color_rol,
                                    weight=ft.FontWeight.W_500
                                )
                            ]
                        )
                    ),

                    # ESTADO
                    ft.Container(
                        width=180,

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

                                on_click=lambda e, u=usuario: (
                                    ver_detalles(u)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,

                                    controls=[
                                        ft.Icon(
                                            ft.Icons.EDIT_OUTLINED,
                                            size=18
                                        ),

                                        ft.Text(
                                            "Editar"
                                        )
                                    ]
                                ),

                                on_click=lambda e, u=usuario: (
                                    editar_usuario(u)
                                )
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,

                                    controls=[
                                        ft.Icon(
                                            ft.Icons.PASSWORD_OUTLINED,
                                            size=18,
                                            color=MORADO
                                        ),

                                        ft.Text(
                                            "Cambiar contraseña"
                                        )
                                    ]
                                ),

                                on_click=lambda e, u=usuario: (
                                    abrir_cambiar_contrasena(u)
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

                                on_click=lambda e, u=usuario: (
                                    alternar_estado(u)
                                )
                            ),

                            *([ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.DELETE_FOREVER,
                                            color=ROJO,
                                            size=18
                                        ),
                                        ft.Text(
                                            "Eliminar definitivamente",
                                            color=ROJO
                                        )
                                    ]
                                ),
                                on_click=lambda e, u=usuario: (
                                    confirmar_eliminar_usuario(u)
                                )
                            )] if puede_eliminar else []),
                            *([ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.BLOCK,
                                            color=AMARILLO,
                                            size=18
                                        ),
                                        ft.Text("Retirar y anonimizar")
                                    ]
                                ),
                                on_click=lambda e, u=usuario: (
                                    confirmar_anonimizar_usuario(u)
                                )
                            )] if puede_anonimizar else [])
                        ]
                    )
                ]
            )
        )

    # =========================================================
    # CARGAR USUARIOS
    # =========================================================

    def cargar_usuarios():

        lista_usuarios.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for usuario in usuarios:

            nombre = (
                usuario.get(
                    "nombre",
                    ""
                )
                .lower()
            )

            correo = (
                usuario.get("correo") or ""
            ).lower()

            rol = usuario.get(
                "rol",
                ""
            )

            estado = usuario.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in nombre
                or texto in correo
                or texto in rol.lower()
            )

            coincide_rol = (
                filtro_rol is None
                or rol == filtro_rol
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_rol
                and coincide_estado
            ):

                lista_usuarios.controls.append(
                    crear_fila(usuario)
                )

                encontrados += 1

        if encontrados == 0:

            lista_usuarios.controls.append(
                ft.Container(
                    height=180,
                    alignment=ft.Alignment.CENTER,

                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,

                        controls=[
                            ft.Icon(
                                ft.Icons.PERSON_SEARCH_OUTLINED,
                                size=45,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron usuarios",
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Prueba con otros filtros o términos",
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

        roles = obtener_roles()

        rol_dropdown = ft.Dropdown(
            label="Rol",
            value=filtro_rol,

            options=[
                ft.DropdownOption(
                    key=r["nombre"],
                    text=r["nombre"]
                )
                for r in roles
            ]
        )

        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=filtro_estado,

            options=[
                ft.DropdownOption(
                    key="Activo",
                    text="Activo"
                ),

                ft.DropdownOption(
                    key="Inactivo",
                    text="Inactivo"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_rol
            nonlocal filtro_estado

            filtro_rol = rol_dropdown.value
            filtro_estado = estado_dropdown.value

            page.pop_dialog()

            cargar_usuarios()
            page.update()

        def limpiar(e):

            nonlocal filtro_rol
            nonlocal filtro_estado

            filtro_rol = None
            filtro_estado = "Activo"

            page.pop_dialog()

            cargar_usuarios()
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
                        "Filtrar usuarios",
                        weight=ft.FontWeight.BOLD
                    )
                ]
            ),

            content=ft.Container(
                width=400,

                content=ft.Column(
                    tight=True,
                    spacing=15,

                    controls=[
                        rol_dropdown,
                        estado_dropdown
                    ]
                )
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
    # TARJETA DE RESUMEN
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
                    width=300,

                    content=ft.Text(
                        "USUARIO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=220,

                    content=ft.Text(
                        "ROL",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=180,

                    content=ft.Text(
                        "ESTADO",
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
        cargar_usuarios(),
        page.update()
    )

    actualizar_estadisticas()
    cargar_usuarios()

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
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

                    controls=[
                        ft.Column(
                            spacing=4,

                            controls=[
                                ft.Text(
                                    "Usuarios",
                                    size=30,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "Administra las cuentas con acceso a Candy Koda Admin",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.ElevatedButton(
                            "Agregar usuario",
                            icon=ft.Icons.PERSON_ADD_ALT_1,
                            height=45,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            on_click=nuevo_usuario
                        )
                    ]
                ),

                # ESTADÍSTICAS
                ft.Row(
                    spacing=15,

                    controls=[
                        tarjeta_resumen(
                            "Usuarios",
                            texto_total,
                            ft.Icons.GROUP_OUTLINED,
                            MORADO,
                            "Registrados"
                        ),

                        tarjeta_resumen(
                            "Activos",
                            texto_activos,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Con acceso"
                        ),

                        tarjeta_resumen(
                            "Inactivos",
                            texto_inactivos,
                            ft.Icons.BLOCK,
                            AMARILLO,
                            "Sin acceso"
                        ),

                        tarjeta_resumen(
                            "Administradores",
                            texto_admin,
                            ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                            ROSA,
                            "Con permisos administrativos"
                        )
                    ]
                ),

                # BUSCADOR / FILTROS
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

                lista_usuarios
            ]
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/usuarios",
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
