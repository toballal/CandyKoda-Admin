import flet as ft

MORADO = "#9B59FF"
ROSA = "#FF4FA3"
VERDE = "#9B59FF"
AMARILLO = "#FFC107"

COLOR_CARD = "#171722"
COLOR_CARD_2 = "#202031"
COLOR_BORDE = "#34344A"
TEXTO_PRINCIPAL = "#FFFFFF"
TEXTO_SECUNDARIO = "#CACAD4"


def detalle_venta(venta, detalles):

    # =========================
    # FECHA
    # =========================

    fecha = venta["fecha"]

    if hasattr(fecha, "strftime"):
        fecha_texto = fecha.strftime("%d/%m/%Y %H:%M")
    else:
        fecha_texto = str(fecha)

    # =========================
    # ESTADO VENTA
    # =========================

    if venta["estado"] == "Completada":
        color_estado = VERDE
        icono_estado = ft.Icons.CHECK_CIRCLE
    else:
        color_estado = ROSA
        icono_estado = ft.Icons.CANCEL

    # =========================
    # PRODUCTOS
    # =========================

    productos = []

    for detalle in detalles:

        estado_entrega = detalle["estado_entrega"]

        if estado_entrega == "Entregado":
            color_entrega = VERDE
        else:
            color_entrega = AMARILLO

        productos.append(
            ft.Container(
                padding=15,
                bgcolor=COLOR_CARD_2,
                border=ft.Border.all(1, COLOR_BORDE),
                border_radius=12,

                content=ft.Row(
                    controls=[
                        # PRODUCTO
                        ft.Column(
                            expand=True,
                            spacing=3,
                            controls=[
                                ft.Text(
                                    detalle["producto"],
                                    size=15,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    f'{detalle["cantidad"]} x '
                                    f'${detalle["precio_unitario"]:,.0f}',
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),

                        # ESTADO ENTREGA
                        ft.Container(
                            padding=ft.Padding.symmetric(
                                horizontal=10,
                                vertical=5
                            ),
                            bgcolor=ft.Colors.with_opacity(0.13, color_entrega),
                            border_radius=10,

                            content=ft.Text(
                                estado_entrega,
                                size=11,
                                color=color_entrega,
                                weight=ft.FontWeight.BOLD
                            )
                        ),

                        # SUBTOTAL
                        ft.Container(
                            width=100,
                            alignment=ft.Alignment.CENTER_RIGHT,

                            content=ft.Text(
                                f'${detalle["subtotal"]:,.0f}',
                                size=15,
                                color=TEXTO_PRINCIPAL,
                                weight=ft.FontWeight.BOLD
                            )
                        )
                    ]
                )
            )
        )

    # =========================
    # CONTENIDO
    # =========================

    return ft.Container(
        width=650,
        padding=25,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, COLOR_BORDE),
        border_radius=18,

        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[

                # TÍTULO
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            color=MORADO,
                            size=28
                        ),

                        ft.Text(
                            f'Detalle de venta #{venta["id"]}',
                            size=24,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                ),

                ft.Divider(
                    color=COLOR_BORDE
                ),

                # =========================
                # INFORMACIÓN
                # =========================

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "CLIENTE",
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    venta["cliente"],
                                    size=15,
                                    color=TEXTO_PRINCIPAL,
                                    weight=ft.FontWeight.BOLD
                                )
                            ]
                        ),

                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text(
                                    "FECHA",
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    fecha_texto,
                                    size=14,
                                    color=TEXTO_PRINCIPAL
                                )
                            ]
                        )
                    ]
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "TARJETA NFC",
                                    size=11,
                                    color=TEXTO_SECUNDARIO
                                ),

                                ft.Text(
                                    venta["uid"],
                                    size=14,
                                    color=TEXTO_PRINCIPAL
                                )
                            ]
                        ),

                        ft.Container(
                            padding=ft.Padding.symmetric(
                                horizontal=12,
                                vertical=7
                            ),
                            bgcolor=ft.Colors.with_opacity(0.13, color_estado),
                            border_radius=10,

                            content=ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Icon(
                                        icono_estado,
                                        size=16,
                                        color=color_estado
                                    ),

                                    ft.Text(
                                        venta["estado"],
                                        size=12,
                                        color=color_estado,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ]
                            )
                        )
                    ]
                ),

                ft.Divider(
                    color=COLOR_BORDE
                ),

                # =========================
                # PRODUCTOS
                # =========================

                ft.Text(
                    "Productos",
                    size=18,
                    color=TEXTO_PRINCIPAL,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Column(
                    controls=productos,
                    spacing=8
                ),

                ft.Divider(
                    color=COLOR_BORDE
                ),

                # =========================
                # TOTAL
                # =========================

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Total",
                            size=18,
                            color=TEXTO_PRINCIPAL,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            f'${venta["total"]:,.0f}',
                            size=24,
                            color=ROSA,
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                )
            ]
        )
    )
