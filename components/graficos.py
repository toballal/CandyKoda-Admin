import flet as ft
import flet_charts as fch


COLOR_CARD = "#171722"
TEXTO_SECUNDARIO = "#C3C3CE"

MORADO = "#9B59FF"
ROSA = "#FF4FA3"
ROJO = "#FF4FA3"
AMARILLO = "#FFC107"
AZUL = "#9B59FF"


# ============================================================
# GRÁFICO VENTAS ÚLTIMOS 7 DÍAS
# ============================================================

def grafico_ventas(datos):

    if not datos:
        return ft.Container(
            expand=True,
            height=350,
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, "#34344A"),
            border_radius=18,
            padding=22,
            alignment=ft.Alignment.CENTER,

            content=ft.Text(
                "No hay ventas registradas",
                color=TEXTO_SECUNDARIO
            )
        )

    puntos = []
    etiquetas = []

    for i, dato in enumerate(datos):

        cantidad = int(dato["cantidad"])
        fecha = dato["fecha"]

        puntos.append(
            fch.LineChartDataPoint(
                x=i,
                y=cantidad
            )
        )

        if hasattr(fecha, "strftime"):
            fecha_texto = fecha.strftime("%d/%m")
        else:
            fecha_texto = str(fecha)

        etiquetas.append(
            fch.ChartAxisLabel(
                value=i,

                label=ft.Text(
                    fecha_texto,
                    size=11,
                    color=TEXTO_SECUNDARIO
                )
            )
        )

    max_ventas = max(
        int(dato["cantidad"])
        for dato in datos
    )

    chart = fch.LineChart(
        expand=True,

        min_x=0,
        max_x=max(len(datos) - 1, 1),

        min_y=0,
        max_y=max(max_ventas + 2, 5),

        interactive=True,

        horizontal_grid_lines=fch.ChartGridLines(
            color="#292930",
            width=1,
            dash_pattern=[3, 3]
        ),

        left_axis=fch.ChartAxis(
            label_size=35,
        ),

        bottom_axis=fch.ChartAxis(
            label_size=35,
            labels=etiquetas
        ),

        data_series=[
            fch.LineChartData(
                points=puntos,
                color=TEXTO_SECUNDARIO,
                stroke_width=4,
                curved=True,
                point=True
            )
        ]
    )

    return ft.Container(
        expand=True,
        height=350,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, "#34344A"),
        border_radius=18,
        padding=22,

        content=ft.Column(
            controls=[
                ft.Text(
                    "Ventas últimos 7 días",
                    size=18,
                    color="#FFFFFF",
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    "Cantidad de ventas completadas por día",
                    size=12,
                    color=TEXTO_SECUNDARIO
                ),

                ft.Container(
                    height=10
                ),

                ft.Container(
                    expand=True,
                    content=chart
                )
            ]
        )
    )


# ============================================================
# GRÁFICO PRODUCTOS MÁS VENDIDOS
# ============================================================

def grafico_productos(datos):

    if not datos:
        return ft.Container(
            expand=True,
            height=350,
            bgcolor=COLOR_CARD,
            border=ft.Border.all(1, "#34344A"),
            border_radius=18,
            padding=22,
            alignment=ft.Alignment.CENTER,

            content=ft.Text(
                "No hay productos vendidos",
                color=TEXTO_SECUNDARIO
            )
        )

    grupos = []
    etiquetas = []

    for i, dato in enumerate(datos):

        producto = dato["producto"]
        cantidad = int(dato["cantidad"])

        grupos.append(
            fch.BarChartGroup(
                x=i,

                rods=[
                    fch.BarChartRod(
                        from_y=0,
                        to_y=cantidad,
                        width=25,
                        color=ROSA,
                        border_radius=6
                    )
                ]
            )
        )

        etiquetas.append(
            fch.ChartAxisLabel(
                value=i,

                label=ft.Text(
                    producto,
                    size=11,
                    color=TEXTO_SECUNDARIO
                )
            )
        )

    max_cantidad = max(
        int(dato["cantidad"])
        for dato in datos
    )

    chart = fch.BarChart(
        expand=True,
        interactive=True,

        min_y=0,
        max_y=max(max_cantidad + 2, 5),

        groups=grupos,

        horizontal_grid_lines=fch.ChartGridLines(
            color="#292930",
            width=1,
            dash_pattern=[3, 3]
        ),

        left_axis=fch.ChartAxis(
            label_size=35,
        ),
        

        bottom_axis=fch.ChartAxis(
            label_size=55,
            labels=etiquetas
        )
    )

    return ft.Container(
        expand=True,
        height=350,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, "#34344A"),
        border_radius=18,
        padding=22,

        content=ft.Column(
            controls=[
                ft.Text(
                    "Productos más vendidos",
                    size=18,
                    color="#FFFFFF",
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    "Cantidad vendida por producto",
                    size=12,
                    color=TEXTO_SECUNDARIO
                ),

                ft.Container(
                    height=10
                ),

                ft.Container(
                    expand=True,
                    content=chart
                )
            ]
        )
    )


# ============================================================
# GRÁFICO CIRCULAR DE ACTIVIDAD DEL SISTEMA
# ============================================================

def grafico_logs(datos, on_ver_logs=None):
    colores = {
        "Error": ROJO,
        "Advertencia": AMARILLO,
        "Informacion": AZUL,
    }
    etiquetas = {
        "Error": "Errores",
        "Advertencia": "Advertencias",
        "Informacion": "Información",
    }

    cantidades = {
        dato["nivel"]: int(dato["cantidad"])
        for dato in datos
    }
    total = sum(cantidades.values())

    if total == 0:
        contenido_grafico = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.DONUT_LARGE_OUTLINED,
                        size=42,
                        color=TEXTO_SECUNDARIO
                    ),
                    ft.Text(
                        "Sin actividad registrada",
                        color=TEXTO_SECUNDARIO
                    )
                ]
            )
        )
    else:
        secciones = []

        for nivel in ("Error", "Advertencia", "Informacion"):
            cantidad = cantidades.get(nivel, 0)
            if cantidad:
                secciones.append(
                    fch.PieChartSection(
                        value=cantidad,
                        color=colores[nivel],
                        radius=58,
                        title=str(cantidad),
                        title_style=ft.TextStyle(
                            size=12,
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD
                        )
                    )
                )

        leyenda = ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=9,
                            height=9,
                            border_radius=10,
                            bgcolor=colores[nivel]
                        ),
                        ft.Text(
                            etiquetas[nivel],
                            size=12,
                            color=TEXTO_SECUNDARIO,
                            expand=True
                        ),
                        ft.Text(
                            str(cantidades.get(nivel, 0)),
                            size=12,
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                )
                for nivel in ("Error", "Advertencia", "Informacion")
            ]
        )

        contenido_grafico = ft.Row(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    content=fch.PieChart(
                        sections=secciones,
                        center_space_radius=34,
                        center_space_color=COLOR_CARD,
                        sections_space=3
                    )
                ),
                ft.Container(width=130, content=leyenda)
            ]
        )

    return ft.Container(
        expand=True,
        height=300,
        bgcolor=COLOR_CARD,
        border=ft.Border.all(1, "#34344A"),
        border_radius=18,
        padding=22,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    "Actividad del sistema",
                                    size=18,
                                    color="#FFFFFF",
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    f"{total} eventos registrados",
                                    size=12,
                                    color=TEXTO_SECUNDARIO
                                )
                            ]
                        ),
                        ft.Container(expand=True),
                        ft.TextButton(
                            "Ver logs",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=on_ver_logs
                        )
                    ]
                ),
                contenido_grafico
            ]
        )
    )
