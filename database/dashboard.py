from database.connection import conectar


def get_resumen_dashboard(
    incluir_ventas=True,
    incluir_productos=True,
    incluir_stock=True,
):
    conexion = conectar()

    if conexion is None:
        return {
            "ventas_hoy": 0,
            "ingresos_hoy": 0,
            "productos": 0,
            "stock_bajo": 0
        }

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        ventas_hoy = (
            """
            (
                SELECT COUNT(*)
                FROM ventas
                WHERE fecha >= CURDATE()
                AND fecha < CURDATE() + INTERVAL 1 DAY
                AND estado = 'Completada'
            )
            """
            if incluir_ventas
            else "0"
        )
        ingresos_hoy = (
            """
            (
                SELECT COALESCE(SUM(total), 0)
                FROM ventas
                WHERE fecha >= CURDATE()
                AND fecha < CURDATE() + INTERVAL 1 DAY
                AND estado = 'Completada'
            )
            """
            if incluir_ventas
            else "0"
        )
        productos = (
            """
            (
                SELECT COUNT(*)
                FROM productos
                WHERE estado = 'Disponible'
            )
            """
            if incluir_productos
            else "0"
        )
        stock_bajo = (
            """
            (
                SELECT COUNT(*)
                FROM productos
                WHERE stock <= stock_minimo
            )
            """
            if incluir_stock
            else "0"
        )

        sql = f"""
            SELECT
                {ventas_hoy} AS ventas_hoy,
                {ingresos_hoy} AS ingresos_hoy,
                {productos} AS productos,
                {stock_bajo} AS stock_bajo
        """

        cursor.execute(sql)

        return cursor.fetchone()

    except Exception as e:
        print("Error al obtener resumen del dashboard:", e)

        return {
            "ventas_hoy": 0,
            "ingresos_hoy": 0,
            "productos": 0,
            "stock_bajo": 0
        }

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def get_productos_mas_vendidos():
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                p.nombre AS producto,
                SUM(d.cantidad) AS cantidad
            FROM detalle_venta d
            INNER JOIN productos p
                ON p.id_producto = d.id_producto
            INNER JOIN ventas v
                ON v.id_venta = d.id_venta
            WHERE v.estado = 'Completada'
            GROUP BY
                p.id_producto,
                p.nombre
            ORDER BY cantidad DESC
            LIMIT 5
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print(
            "Error obteniendo productos más vendidos:",
            e
        )

        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def get_ventas_ultimos_7_dias():
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                DATE(fecha) AS fecha,
                COUNT(*) AS cantidad
            FROM ventas
            WHERE fecha >= CURDATE() - INTERVAL 6 DAY
            AND estado = 'Completada'
            GROUP BY DATE(fecha)
            ORDER BY fecha ASC
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print(
            "Error obteniendo ventas:",
            e
        )

        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def get_alertas_stock(limite=3):
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
                SELECT id_producto, nombre, stock, stock_minimo
                FROM productos
                WHERE stock <= stock_minimo
                  AND estado <> 'Inactivo'
                ORDER BY stock ASC, nombre ASC
                LIMIT %s
            """,
            (int(limite),)
        )
        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener alertas de stock:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        conexion.close()
