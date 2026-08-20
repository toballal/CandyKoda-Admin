import flet as ft

from components.sidebar import sidebar
from database.categorias import (
    obtener_categorias_admin,
    agregar_categoria,
    actualizar_categoria,
    eliminar_categoria,
)


MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"
TEXTO_SECUNDARIO = "#C3C3CE"


def categorias_view(page: ft.Page):
    categorias = obtener_categorias_admin()
    usuario = getattr(page, "usuario_actual", None) or {}
    id_usuario = usuario.get("id_usuario")
    lista = ft.Column(spacing=10)
    buscador = ft.TextField(
        hint_text="Buscar categoría...",
        prefix_icon=ft.Icons.SEARCH,
        width=360,
        height=45,
        bgcolor=COLOR_CARD,
        border_color=COLOR_BORDE,
    )

    def mensaje(texto, color=VERDE):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto, color="#FFFFFF"),
                bgcolor=color,
            )
        )

    def refrescar():
        nonlocal categorias
        categorias = obtener_categorias_admin()
        cargar()
        page.update()

    def abrir_formulario(categoria=None):
        categoria = categoria or {}
        nombre = ft.TextField(
            label="Nombre",
            value=categoria.get("nombre") or "",
            prefix_icon=ft.Icons.CATEGORY_OUTLINED,
        )
        descripcion = ft.TextField(
            label="Descripción",
            value=categoria.get("descripcion") or "",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        estado = ft.Dropdown(
            label="Estado",
            value=categoria.get("estado") or "Activa",
            options=[
                ft.DropdownOption(key="Activa", text="Activa"),
                ft.DropdownOption(key="Inactiva", text="Inactiva"),
            ],
        )
        error = ft.Text("", color=ROSA, size=12)

        def guardar(e):
            nombre_valor = (nombre.value or "").strip()
            descripcion_valor = (descripcion.value or "").strip()
            if not nombre_valor:
                error.value = "Ingrese el nombre de la categoría"
                page.update()
                return
            if len(nombre_valor) > 80:
                error.value = "El nombre admite hasta 80 caracteres"
                page.update()
                return
            if len(descripcion_valor) > 200:
                error.value = "La descripción admite hasta 200 caracteres"
                page.update()
                return

            if categoria:
                resultado = actualizar_categoria(
                    categoria["id_categoria"],
                    nombre_valor,
                    descripcion_valor,
                    estado.value,
                    id_usuario,
                )
            else:
                resultado = agregar_categoria(
                    nombre_valor,
                    descripcion_valor,
                    estado.value,
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
                title=ft.Text(
                    "Editar categoría" if categoria else "Nueva categoría"
                ),
                content=ft.Container(
                    width=440,
                    content=ft.Column(
                        tight=True,
                        spacing=14,
                        controls=[nombre, descripcion, estado, error],
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

    def confirmar_eliminar(categoria):
        def eliminar(e):
            resultado = eliminar_categoria(
                categoria["id_categoria"],
                id_usuario,
            )
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
                title=ft.Text("Eliminar categoría definitivamente"),
                content=ft.Text(
                    f"¿Eliminar '{categoria['nombre']}'? "
                    "Solo se borrará si no contiene productos."
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.ElevatedButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_FOREVER,
                        bgcolor=ROSA,
                        color="#FFFFFF",
                        on_click=eliminar,
                    ),
                ],
            )
        )

    def fila(categoria):
        activa = categoria.get("estado") == "Activa"
        return ft.Container(
            padding=18,
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, COLOR_BORDE),
            border_radius=12,
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CATEGORY_OUTLINED, color=MORADO),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                categoria["nombre"],
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                categoria.get("descripcion")
                                or "Sin descripción",
                                color=TEXTO_SECUNDARIO,
                                size=12,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{categoria.get('productos', 0)} productos",
                        color=TEXTO_SECUNDARIO,
                    ),
                    ft.Container(
                        padding=ft.Padding.symmetric(
                            horizontal=10, vertical=5
                        ),
                        border_radius=15,
                        bgcolor=ft.Colors.with_opacity(
                            0.14, VERDE if activa else ROSA
                        ),
                        content=ft.Text(
                            categoria["estado"],
                            color=VERDE if activa else ROSA,
                        ),
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text("Editar"),
                                on_click=lambda e, c=categoria: (
                                    abrir_formulario(c)
                                ),
                            ),
                            ft.PopupMenuItem(
                                content=ft.Text(
                                    "Eliminar definitivamente",
                                    color=ROSA,
                                ),
                                on_click=lambda e, c=categoria: (
                                    confirmar_eliminar(c)
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
            categoria
            for categoria in categorias
            if texto in categoria["nombre"].casefold()
            or texto in str(categoria.get("descripcion") or "").casefold()
        ]
        lista.controls.extend(fila(categoria) for categoria in resultados)
        if not resultados:
            lista.controls.append(
                ft.Container(
                    height=150,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "No se encontraron categorías",
                        color=TEXTO_SECUNDARIO,
                    ),
                )
            )

    buscador.on_change = lambda e: (cargar(), page.update())
    cargar()

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=ft.Colors.with_opacity(0.85, COLOR_FONDO),
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
                                    "Categorías",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "CRUD del catálogo de productos",
                                    color=TEXTO_SECUNDARIO,
                                ),
                            ],
                        ),
                        ft.ElevatedButton(
                            "Nueva categoría",
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
        route="/categorias",
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
