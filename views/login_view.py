import flet as ft

from database.auth import autenticarUsuario
from database.logs import registrar_log


def login_view(page: ft.Page):

    # =========================================================
    # CAMPOS
    # =========================================================

    usuario = ft.TextField(
        label="Usuario",
        hint_text="Ingresa tu nombre de usuario",
        width=340,
        height=54,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        bgcolor="#171722",
        border_color="#34344A",
        focused_border_color="#9B59FF",
        cursor_color="#FF4FA3",
        border_radius=12
    )

    contraseña = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        hint_text="Ingresa tu contraseña",
        width=340,
        height=54,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        bgcolor="#171722",
        border_color="#34344A",
        focused_border_color="#9B59FF",
        cursor_color="#FF4FA3",
        border_radius=12
    )

    mensaje = ft.Text(
        color="#FF4FA3",
        size=12,
        text_align=ft.TextAlign.CENTER
    )

    # =========================================================
    # INICIAR SESIÓN
    # =========================================================

    def iniciar_sesion(e):

        nombre = (usuario.value or "").strip()
        # Los espacios pueden formar parte de una contraseña válida.
        contra = contraseña.value or ""

        usuario.error = None
        contraseña.error = None
        mensaje.value = ""

        # =====================================================
        # VALIDAR CAMPOS VACÍOS
        # =====================================================

        if nombre == "":
            usuario.error = "Ingrese el usuario"

        if contra == "":
            contraseña.error = "Ingrese la contraseña"

        if usuario.error or contraseña.error:
            page.update()
            return

        # =====================================================
        # AUTENTICAR USUARIO
        # =====================================================

        usuario_autenticado = autenticarUsuario(
            contra,
            nombre
        )

        if usuario_autenticado:

            # =================================================
            # GUARDAR USUARIO ACTUAL
            # =================================================

            page.usuario_actual = usuario_autenticado

            # Obtener ID del usuario
            id_usuario = usuario_autenticado.get(
                "id_usuario"
            )

            # Obtener nombre real desde la base de datos
            nombre_usuario = usuario_autenticado.get(
                "nombre"
            )

            print(
                "Usuario conectado:",
                usuario_autenticado
            )

            # =================================================
            # REGISTRAR INICIO DE SESIÓN
            # =================================================

            registrar_log(
                modulo="Admin",
                accion="Inicio de sesión",
                descripcion=(
                    f"El usuario '{nombre_usuario}' "
                    "inició sesión correctamente."
                ),
                nivel="Informacion",
                id_usuario=id_usuario
            )

            print(
                f"Inicio de sesión correcto: "
                f"{nombre_usuario} "
                f"(ID: {id_usuario})"
            )

            # =================================================
            # IR AL DASHBOARD
            # =================================================

            page.go("/dashboard")

        else:

            mensaje.value = (
                "Usuario o contraseña incorrectos"
            )

        page.update()

    # =========================================================
    # BOTÓN
    # =========================================================

    boton = ft.ElevatedButton(
        "Ingresar al panel",
        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
        width=340,
        height=52,
        on_click=iniciar_sesion,
        bgcolor="#9B59FF",
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(
                radius=12
            ),
            padding=10,
        )
    )

    contraseña.on_submit = iniciar_sesion

    # =========================================================
    # CONTENIDO
    # =========================================================

    contenido = ft.Container(
        width=420,
        padding=38,
        bgcolor=ft.Colors.with_opacity(
            0.94,
            "#0F0F18"
        ),
        border=ft.Border.all(
            1,
            "#3B3152"
        ),
        border_radius=24,
        shadow=ft.BoxShadow(
            blur_radius=45,
            spread_radius=2,
            color=ft.Colors.with_opacity(
                0.50,
                "#000000"
            )
        ),
        content=ft.Column(
            [
                # =================================================
                # LOGO
                # =================================================

                ft.Container(
                    width=210,
                    height=125,
                    border_radius=20,
                    bgcolor="#151522",
                    border=ft.Border.all(
                        1,
                        "#5D3599"
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src="LogoCanyKodaSimplify.svg",
                        width=185,
                        height=110,
                        fit=ft.BoxFit.CONTAIN
                    )
                ),

                # =================================================
                # TÍTULO
                # =================================================

                ft.Text(
                    "Bienvenido",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF"
                ),

                ft.Text(
                    "Accede al centro de administración de Candy Koda",
                    size=14,
                    color="#C3C3CE",
                    text_align=ft.TextAlign.CENTER
                ),

                ft.Divider(
                    color="#34344A",
                    height=24
                ),

                # =================================================
                # CAMPOS
                # =================================================

                usuario,
                contraseña,

                ft.Container(
                    height=4
                ),

                # =================================================
                # BOTÓN
                # =================================================

                boton,

                # =================================================
                # MENSAJE
                # =================================================

                mensaje
            ],

            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            tight=True,
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/",
        padding=0,

        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        controls=[
            contenido
        ]
    )
