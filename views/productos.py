import flet as ft

from components.sidebar import sidebar

from database.productos import (
    obtener_productos,
    actualizar_producto,
    agregar_producto,
    obtener_categorias,
    eliminar_producto,
    activar_producto,
    eliminar_producto_definitivamente
)
from services.autorizacion import puede_realizar


# =========================================================
# COLORES
# =========================================================

MORADO = "#9B59FF"
ROSA = "#FF4FA3"
AMARILLO = "#FFC107"
VERDE = "#9B59FF"
ROJO = "#FF4FA3"

COLOR_FONDO = "#0D0D14"
COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"

TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#C3C3CE"


def productos_view(page: ft.Page):

    puede_eliminar_definitivamente = puede_realizar(
        getattr(page, "usuario_actual", None),
        "eliminar_producto"
    )

    # =========================================================
    # OBTENER USUARIO ACTUAL
    # =========================================================

    def obtener_id_usuario_actual():

        usuario_actual = getattr(
            page,
            "usuario_actual",
            None
        )

        if not usuario_actual:
            print("ADVERTENCIA: No hay usuario autenticado.")
            return None

        # Si autenticarUsuario devuelve un diccionario
        if isinstance(usuario_actual, dict):

            id_usuario = usuario_actual.get(
                "id_usuario"
            )

            if id_usuario is not None:
                return id_usuario

        # Por si devuelve otro tipo de objeto
        try:

            id_usuario = getattr(
                usuario_actual,
                "id_usuario",
                None
            )

            if id_usuario is not None:
                return id_usuario

        except Exception:
            pass

        print(
            "ADVERTENCIA: No se encontró id_usuario "
            "en page.usuario_actual."
        )

        return None

    # =========================================================
    # DATOS
    # =========================================================

    productos = obtener_productos()

    # ---------------------------------------------------------
    # NO MOSTRAR LOS ÚLTIMOS 3 PRODUCTOS
    # ---------------------------------------------------------

    if len(productos) > 3:
        productos = productos[:-3]

    filtro_categoria = None
    filtro_estado = "Disponible"

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

    texto_categorias = ft.Text(
        "0",
        size=27,
        weight=ft.FontWeight.BOLD,
        color=TEXTO_PRINCIPAL
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscador = ft.TextField(
        hint_text="Buscar por nombre o categoría...",
        prefix_icon=ft.Icons.SEARCH,
        width=360,
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

    lista_productos = ft.Column(
        spacing=10
    )

    # =========================================================
    # MENSAJES
    # =========================================================

    def mostrar_mensaje(
        texto,
        color=VERDE
    ):

        snack = ft.SnackBar(
            content=ft.Text(
                texto,
                color="#FFFFFF"
            ),
            bgcolor=color
        )

        page.show_dialog(snack)

    # =========================================================
    # ACTUALIZAR ESTADÍSTICAS
    # =========================================================

    def actualizar_estadisticas():

        total = len(productos)

        activos = sum(
            1
            for producto in productos
            if producto.get("estado") == "Disponible"
        )

        categorias = {
            producto.get("categoria")
            or producto.get("categoría")
            for producto in productos
            if producto.get("categoria")
            or producto.get("categoría")
        }

        texto_total.value = str(total)
        texto_activos.value = str(activos)
        texto_categorias.value = str(len(categorias))

    # =========================================================
    # RECARGAR PRODUCTOS
    # =========================================================

    def recargar_productos():

        nonlocal productos

        productos = obtener_productos()

        # -----------------------------------------------------
        # VOLVER A OCULTAR LOS ÚLTIMOS 3
        # -----------------------------------------------------

        if len(productos) > 3:
            productos = productos[:-3]

        actualizar_estadisticas()
        cargar_productos()

        page.update()

    # =========================================================
    # CERRAR DIÁLOGO
    # =========================================================

    def cerrar_dialogo():

        page.pop_dialog()

    # =========================================================
    # NUEVO PRODUCTO
    # =========================================================

    def nuevo_producto(e):

        categorias = obtener_categorias()

        nombre = ft.TextField(
            label="Nombre",
            hint_text="Ej: Frugele",
            prefix_icon=ft.Icons.COOKIE_OUTLINED
        )

        descripcion = ft.TextField(
            label="Descripción",
            hint_text="Descripción del producto",
            multiline=True,
            min_lines=2,
            max_lines=3
        )

        precio = ft.TextField(
            label="Precio",
            hint_text="Ej: 400",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.ATTACH_MONEY
        )

        categoria = ft.Dropdown(
            label="Categoría",
            hint_text="Selecciona una categoría",
            options=[
                ft.DropdownOption(
                    key=str(c["id_categoria"]),
                    text=c["nombre"]
                )
                for c in categorias
            ]
        )

        imagen = ft.TextField(
            label="Imagen",
            hint_text="Ej: images/frugele.png",
            prefix_icon=ft.Icons.IMAGE_OUTLINED
        )

        estado = ft.Dropdown(
            label="Estado",
            value="Disponible",
            options=[
                ft.DropdownOption(
                    key="Disponible",
                    text="Disponible"
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

            mensaje_error.value = ""

            nombre_valor = (
                nombre.value or ""
            ).strip()

            descripcion_valor = (
                descripcion.value or ""
            ).strip()

            precio_valor = (
                precio.value or ""
            ).strip()

            imagen_valor = (
                imagen.value or ""
            ).strip()

            if not nombre_valor:

                mensaje_error.value = (
                    "Ingrese el nombre del producto"
                )

                page.update()
                return

            if not descripcion_valor:

                mensaje_error.value = (
                    "Ingrese una descripción"
                )

                page.update()
                return

            if not precio_valor:

                mensaje_error.value = (
                    "Ingrese el precio"
                )

                page.update()
                return

            if categoria.value is None:

                mensaje_error.value = (
                    "Seleccione una categoría"
                )

                page.update()
                return

            try:

                precio_numero = float(
                    precio_valor
                )

                if precio_numero <= 0:
                    raise ValueError

            except ValueError:

                mensaje_error.value = (
                    "Ingrese un precio válido"
                )

                page.update()
                return

            # =================================================
            # OBTENER USUARIO QUE HACE EL CAMBIO
            # =================================================

            id_usuario = obtener_id_usuario_actual()

            if id_usuario is None:

                mensaje_error.value = (
                    "No se pudo identificar al usuario actual."
                )

                page.update()
                return

            # =================================================
            # AGREGAR PRODUCTO
            # =================================================

            exito = agregar_producto(
                nombre_valor,
                descripcion_valor,
                precio_numero,
                int(categoria.value),
                imagen_valor,
                estado.value,
                id_usuario=id_usuario
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    f"{nombre_valor} fue agregado correctamente"
                )

                recargar_productos()

            else:

                mensaje_error.value = (
                    "No se pudo agregar el producto"
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
                        bgcolor=ft.Colors.with_opacity(
                            0.13,
                            MORADO
                        ),
                        alignment=ft.Alignment.CENTER,

                        content=ft.Icon(
                            ft.Icons.ADD_SHOPPING_CART,
                            color=MORADO
                        )
                    ),

                    ft.Column(
                        spacing=1,

                        controls=[

                            ft.Text(
                                "Agregar producto",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Registra un producto en el catálogo",
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                ]
            ),

            content=ft.Container(
                width=460,

                content=ft.Column(
                    tight=True,
                    spacing=14,

                    controls=[

                        nombre,
                        descripcion,

                        ft.Row(
                            controls=[

                                ft.Container(
                                    expand=True,
                                    content=precio
                                ),

                                ft.Container(
                                    expand=True,
                                    content=categoria
                                )
                            ]
                        ),

                        imagen,
                        estado,
                        mensaje_error
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                        cerrar_dialogo()
                ),

                ft.ElevatedButton(
                    "Agregar producto",
                    icon=ft.Icons.ADD,
                    bgcolor=MORADO,
                    color="#FFFFFF",
                    on_click=guardar
                )
            ]
        )

        page.show_dialog(dialogo)

    def confirmar_eliminar_definitivamente(producto):
        def eliminar(e):
            id_usuario = obtener_id_usuario_actual()
            resultado = eliminar_producto_definitivamente(
                producto["id_producto"],
                id_usuario
            )
            page.pop_dialog()
            mostrar_mensaje(
                resultado["mensaje"],
                VERDE if resultado["exito"] else ROJO
            )
            if resultado["exito"]:
                recargar_productos()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar producto definitivamente"),
                content=ft.Text(
                    f"¿Eliminar {producto['nombre']}? "
                    "Solo será posible si nunca fue vendido, movido "
                    "ni asignado a un dispensador."
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
    # VER DETALLES
    # =========================================================

    def ver_detalles(producto):

        estado = producto.get(
            "estado",
            "Disponible"
        )

        color_estado = (
            VERDE
            if estado == "Disponible"
            else TEXTO_SECUNDARIO
        )

        dispensador = producto.get(
            "id_dispensador"
        )

        if dispensador is None:

            dispensador_texto = "Sin asignar"

        else:

            dispensador_texto = (
                f"Dispensador {dispensador}"
            )

        def dato(
            icono,
            titulo,
            valor
        ):

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

        categoria = (
            producto.get("categoria")
            or producto.get("categoría")
            or "Sin categoría"
        )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                producto.get(
                    "nombre",
                    "Producto"
                ),
                size=22,
                weight=ft.FontWeight.BOLD
            ),

            content=ft.Container(
                width=450,

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
                                size=12,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        ft.Text(
                            producto.get(
                                "descripcion",
                                "Sin descripción"
                            ),
                            color=TEXTO_SECUNDARIO,
                            size=13
                        ),

                        dato(
                            ft.Icons.CATEGORY_OUTLINED,
                            "Categoría",
                            categoria
                        ),

                        dato(
                            ft.Icons.ATTACH_MONEY,
                            "Precio",
                            f"${int(producto.get('precio', 0)):,}".replace(
                                ",",
                                "."
                            )
                        ),

                        dato(
                            ft.Icons.INVENTORY_2_OUTLINED,
                            "Stock actual",
                            producto.get(
                                "stock",
                                0
                            )
                        ),

                        dato(
                            ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                            "Dispensador",
                            dispensador_texto
                        )
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e:
                        cerrar_dialogo()
                ),

                ft.ElevatedButton(
                    "Editar",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=MORADO,
                    color="#FFFFFF",

                    on_click=lambda e: (
                        page.pop_dialog(),
                        editar_producto(producto)
                    )
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # EDITAR PRODUCTO
    # =========================================================

    def editar_producto(producto):

        nombre = ft.TextField(
            label="Nombre",
            value=producto.get(
                "nombre",
                ""
            )
        )

        precio = ft.TextField(
            label="Precio",
            value=str(
                producto.get(
                    "precio",
                    0
                )
            ),
            keyboard_type=ft.KeyboardType.NUMBER
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

            precio_valor = (
                precio.value or ""
            ).strip()

            if not nombre_valor:

                mensaje_error.value = (
                    "Ingrese el nombre"
                )

                page.update()
                return

            try:

                precio_numero = float(
                    precio_valor
                )

                if precio_numero <= 0:
                    raise ValueError

            except ValueError:

                mensaje_error.value = (
                    "Ingrese un precio válido"
                )

                page.update()
                return

            # =================================================
            # OBTENER USUARIO ACTUAL
            # =================================================

            id_usuario = obtener_id_usuario_actual()

            if id_usuario is None:

                mensaje_error.value = (
                    "No se pudo identificar al usuario actual."
                )

                page.update()
                return

            # =================================================
            # ACTUALIZAR PRODUCTO
            # =================================================

            exito = actualizar_producto(
                producto["id_producto"],
                nombre_valor,
                precio_numero,
                id_usuario=id_usuario
            )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    "Producto actualizado correctamente"
                )

                recargar_productos()

            else:

                mensaje_error.value = (
                    "No se pudo actualizar el producto"
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
                        "Editar producto",
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
                        precio,
                        mensaje_error
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                        cerrar_dialogo()
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
    # CAMBIAR ESTADO
    # =========================================================

    def confirmar_cambiar_estado_producto(producto):

        esta_disponible = (
            producto.get(
                "estado",
                "Disponible"
            ) == "Disponible"
        )

        accion = (
            "desactivar"
            if esta_disponible
            else "activar"
        )

        accion_titulo = accion.capitalize()

        nuevo_estado = (
            "Inactivo"
            if esta_disponible
            else "Disponible"
        )

        color_accion = (
            AMARILLO
            if esta_disponible
            else VERDE
        )

        icono_accion = (
            ft.Icons.BLOCK
            if esta_disponible
            else ft.Icons.CHECK_CIRCLE_OUTLINE
        )

        mensaje_error = ft.Text(
            "",
            color=ROJO,
            size=12
        )

        def confirmar(e):

            # =================================================
            # OBTENER USUARIO ACTUAL
            # =================================================

            id_usuario = obtener_id_usuario_actual()

            if id_usuario is None:

                mensaje_error.value = (
                    "No se pudo identificar al usuario actual."
                )

                page.update()
                return

            # =================================================
            # CAMBIAR ESTADO
            # =================================================

            if esta_disponible:

                exito = eliminar_producto(
                    producto["id_producto"],
                    id_usuario=id_usuario
                )

            else:

                exito = activar_producto(
                    producto["id_producto"],
                    id_usuario=id_usuario
                )

            if exito:

                page.pop_dialog()

                mostrar_mensaje(
                    f"{producto['nombre']} ahora está "
                    f"{nuevo_estado.lower()}",
                    color_accion
                )

                recargar_productos()

            else:

                mensaje_error.value = (
                    f"No se pudo {accion} el producto"
                )

                page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Row(
                spacing=10,

                controls=[

                    ft.Icon(
                        ft.Icons.WARNING_AMBER_ROUNDED,
                        color=AMARILLO
                    ),

                    ft.Text(
                        f"{accion_titulo} producto",
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

                        ft.Text(
                            f"¿Deseas {accion} "
                            f"{producto['nombre']}?"
                        ),

                        ft.Text(
                            (
                                "El producto dejará de estar disponible "
                                "para la venta, pero conservará su "
                                "información e historial."
                                if esta_disponible
                                else
                                "El producto volverá a estar disponible "
                                "para la venta."
                            ),
                            color=TEXTO_SECUNDARIO,
                            size=13
                        ),

                        mensaje_error
                    ]
                )
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                        cerrar_dialogo()
                ),

                ft.ElevatedButton(
                    accion_titulo,
                    icon=icono_accion,
                    bgcolor=color_accion,
                    color="#151519",
                    on_click=confirmar
                )
            ]
        )

        page.show_dialog(dialogo)

    # =========================================================
    # FILA DE PRODUCTO
    # =========================================================

    def crear_fila_producto(producto):

        nombre = producto.get(
            "nombre",
            "Sin nombre"
        )

        categoria = (
            producto.get("categoria")
            or producto.get("categoría")
            or "Sin categoría"
        )

        precio = producto.get(
            "precio",
            0
        )

        estado = producto.get(
            "estado",
            "Disponible"
        )

        dispensador = producto.get(
            "id_dispensador"
        )

        if dispensador is None:

            dispensador_texto = "Sin asignar"
            color_dispensador = TEXTO_SECUNDARIO

        else:

            dispensador_texto = (
                f"Dispensador {dispensador}"
            )

            color_dispensador = MORADO

        if estado == "Disponible":

            color_estado = VERDE
            icono_estado = (
                ft.Icons.CHECK_CIRCLE_OUTLINE
            )

        else:

            color_estado = TEXTO_SECUNDARIO
            icono_estado = ft.Icons.BLOCK

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
                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    ft.Container(
                        width=260,

                        content=ft.Row(
                            spacing=12,

                            controls=[

                                ft.Container(
                                    width=46,
                                    height=46,
                                    border_radius=11,

                                    bgcolor=ft.Colors.with_opacity(
                                        0.08,
                                        ROSA
                                    ),

                                    alignment=ft.Alignment.CENTER,

                                    content=ft.Icon(
                                        ft.Icons.COOKIE_OUTLINED,
                                        color=ROSA,
                                        size=24
                                    )
                                ),

                                ft.Column(
                                    spacing=2,

                                    controls=[

                                        ft.Text(
                                            nombre,
                                            size=14,
                                            color=TEXTO_PRINCIPAL,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            f"ID #{producto['id_producto']}",
                                            size=11,
                                            color=TEXTO_SECUNDARIO
                                        )
                                    ]
                                )
                            ]
                        )
                    ),

                    ft.Container(
                        width=160,

                        content=ft.Text(
                            categoria,
                            size=13,
                            color=TEXTO_SECUNDARIO
                        )
                    ),

                    ft.Container(
                        width=130,

                        content=ft.Text(
                            f"${int(precio):,}".replace(
                                ",",
                                "."
                            ),
                            size=14,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ),

                    ft.Container(
                        width=170,

                        content=ft.Row(
                            spacing=6,

                            controls=[

                                ft.Icon(
                                    ft.Icons.PRECISION_MANUFACTURING_OUTLINED,
                                    size=17,
                                    color=color_dispensador
                                ),

                                ft.Text(
                                    dispensador_texto,
                                    size=12,
                                    color=color_dispensador
                                )
                            ]
                        )
                    ),

                    ft.Container(
                        width=140,

                        content=ft.Row(
                            spacing=6,

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

                    ft.Container(
                        expand=True
                    ),

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

                                on_click=lambda e, p=producto:
                                    ver_detalles(p)
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

                                on_click=lambda e, p=producto:
                                    editar_producto(p)
                            ),

                            ft.PopupMenuItem(
                                content=ft.Row(
                                    spacing=10,

                                    controls=[

                                        ft.Icon(
                                            (
                                                ft.Icons.BLOCK
                                                if estado == "Disponible"
                                                else
                                                ft.Icons.CHECK_CIRCLE_OUTLINE
                                            ),
                                            size=18,

                                            color=(
                                                AMARILLO
                                                if estado == "Disponible"
                                                else VERDE
                                            )
                                        ),

                                        ft.Text(
                                            (
                                                "Desactivar"
                                                if estado == "Disponible"
                                                else "Activar"
                                            ),

                                            color=(
                                                AMARILLO
                                                if estado == "Disponible"
                                                else VERDE
                                            )
                                        )
                                    ]
                                ),

                                on_click=lambda e, p=producto:
                                    confirmar_cambiar_estado_producto(p)
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
                                on_click=lambda e, p=producto: (
                                    confirmar_eliminar_definitivamente(p)
                                )
                            )] if puede_eliminar_definitivamente else [])
                        ]
                    )
                ]
            )
        )

    # =========================================================
    # FILTROS
    # =========================================================

    def mostrar_filtros(e):

        nonlocal filtro_categoria
        nonlocal filtro_estado

        categoria_dropdown = ft.Dropdown(
            label="Categoría",

            value=filtro_categoria,

            options=[

                ft.DropdownOption(
                    key="Todas",
                    text="Todas"
                ),

                ft.DropdownOption(
                    key="Gomitas",
                    text="Gomitas"
                ),

                ft.DropdownOption(
                    key="Masticables",
                    text="Masticables"
                ),

                ft.DropdownOption(
                    key="Chicles",
                    text="Chicles"
                )
            ]
        )

        estado_dropdown = ft.Dropdown(
            label="Estado",

            value=(
                filtro_estado
                if filtro_estado is not None
                else "Todos"
            ),

            options=[

                ft.DropdownOption(
                    key="Todos",
                    text="Todos"
                ),

                ft.DropdownOption(
                    key="Disponible",
                    text="Disponible"
                ),

                ft.DropdownOption(
                    key="Inactivo",
                    text="Inactivo"
                )
            ]
        )

        def aplicar(e):

            nonlocal filtro_categoria
            nonlocal filtro_estado

            categoria_seleccionada = (
                categoria_dropdown.value
            )

            estado_seleccionado = (
                estado_dropdown.value
            )

            if (
                categoria_seleccionada is None
                or categoria_seleccionada == "Todas"
            ):

                filtro_categoria = None

            else:

                filtro_categoria = (
                    categoria_seleccionada
                )

            if (
                estado_seleccionado is None
                or estado_seleccionado == "Todos"
            ):

                filtro_estado = None

            else:

                filtro_estado = (
                    estado_seleccionado
                )

            page.pop_dialog()

            cargar_productos()
            page.update()

        def limpiar(e):

            nonlocal filtro_categoria
            nonlocal filtro_estado

            filtro_categoria = None
            filtro_estado = "Disponible"

            page.pop_dialog()

            cargar_productos()
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
                        "Filtrar productos",
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

                        categoria_dropdown,
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
                    on_click=lambda e:
                        cerrar_dialogo()
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
    # CARGAR PRODUCTOS
    # =========================================================

    def cargar_productos(e=None):

        lista_productos.controls.clear()

        texto = (
            buscador.value or ""
        ).lower().strip()

        encontrados = 0

        for producto in productos:

            nombre = (
                producto.get(
                    "nombre",
                    ""
                )
                .lower()
            )

            categoria = (
                producto.get("categoria")
                or producto.get("categoría")
                or ""
            )

            estado = producto.get(
                "estado",
                ""
            )

            coincide_busqueda = (
                texto in nombre
                or texto in categoria.lower()
            )

            coincide_categoria = (
                filtro_categoria is None
                or categoria.lower()
                == filtro_categoria.lower()
            )

            coincide_estado = (
                filtro_estado is None
                or estado == filtro_estado
            )

            if (
                coincide_busqueda
                and coincide_categoria
                and coincide_estado
            ):

                lista_productos.controls.append(
                    crear_fila_producto(
                        producto
                    )
                )

                encontrados += 1

        if encontrados == 0:

            lista_productos.controls.append(

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
                                ft.Icons.SEARCH_OFF,
                                size=42,
                                color=TEXTO_SECUNDARIO
                            ),

                            ft.Text(
                                "No se encontraron productos",
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                "Prueba con otra categoría "
                                "o término de búsqueda",
                                size=12,
                                color=TEXTO_SECUNDARIO
                            )
                        ]
                    )
                )
            )

    # =========================================================
    # BUSCADOR
    # =========================================================

    def buscar_productos(e):

        cargar_productos()
        page.update()

    buscador.on_change = buscar_productos

    # =========================================================
    # TARJETA ESTADÍSTICA
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
    # ENCABEZADO TABLA
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
                    width=260,

                    content=ft.Text(
                        "PRODUCTO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=160,

                    content=ft.Text(
                        "CATEGORÍA",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=130,

                    content=ft.Text(
                        "PRECIO",
                        size=11,
                        color=TEXTO_SECUNDARIO,
                        weight=ft.FontWeight.BOLD
                    )
                ),

                ft.Container(
                    width=170,

                    content=ft.Text(
                        "DISPENSADOR",
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
                    expand=True
                ),

                ft.Container(
                    width=40,
                    content=ft.Text("")
                )
            ]
        )
    )

    # =========================================================
    # CARGA INICIAL
    # =========================================================

    actualizar_estadisticas()
    cargar_productos()

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

                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    controls=[

                        ft.Column(
                            spacing=4,

                            controls=[

                                ft.Text(
                                    "Productos",
                                    size=30,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "Administra el catálogo de "
                                    "productos de Candy Koda",
                                    size=14,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        ft.ElevatedButton(
                            "Agregar producto",
                            icon=ft.Icons.ADD,
                            height=45,
                            bgcolor=MORADO,
                            color="#FFFFFF",
                            on_click=nuevo_producto
                        )
                    ]
                ),

                ft.Row(
                    spacing=15,

                    controls=[

                        tarjeta_resumen(
                            "Productos",
                            texto_total,
                            ft.Icons.CATEGORY_OUTLINED,
                            MORADO,
                            "Registrados"
                        ),

                        tarjeta_resumen(
                            "Productos activos",
                            texto_activos,
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            VERDE,
                            "Disponibles para venta"
                        ),

                        tarjeta_resumen(
                            "Categorías",
                            texto_categorias,
                            ft.Icons.LABEL_OUTLINE,
                            ROSA,
                            "En el catálogo"
                        )
                    ]
                ),

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

                lista_productos
            ]
        )
    )

    # =========================================================
    # VIEW
    # =========================================================

    return ft.View(
        route="/productos",
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
