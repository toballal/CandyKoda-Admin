from database.connection import conectar

def get_ventas():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            SELECT 
                v.id_venta,
                COALESCE(c.nombre, 'Sin cliente'),
                COALESCE(t.uid, 'Sin tarjeta'),
                v.total,
                v.estado,
                v.fecha
            FROM ventas v
            LEFT JOIN clientes c
                ON c.id_cliente = v.id_cliente
            LEFT JOIN tarjetas_nfc t
                ON t.id_tarjeta = v.id_tarjeta
            ORDER BY v.fecha DESC
        """

        cursor.execute(
            sql
        )

        ventas = cursor.fetchall()

        return ventas

    except Exception as e:
        print("No se logro:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def get_detalle_venta(id_venta):
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                d.id_detalle,
                v.id_venta,
                p.nombre AS producto,
                d.cantidad,
                d.precio_unitario,
                d.descuento,
                d.subtotal,
                d.estado_entrega
            FROM detalle_venta d
            INNER JOIN ventas v
                ON d.id_venta = v.id_venta
            INNER JOIN productos p
                ON p.id_producto = d.id_producto
            WHERE v.id_venta = %s
        """

        cursor.execute(
            sql,
            (id_venta,)
        )

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener detalle de venta:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()

def get_ventas_resumen():
    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                v.id_venta,
                COALESCE(c.nombre, 'Sin cliente') AS cliente,
                COALESCE(t.uid, 'Sin tarjeta') AS uid,
                v.total,
                v.estado,
                v.fecha
            FROM ventas v
            LEFT JOIN clientes c
                ON c.id_cliente = v.id_cliente
            LEFT JOIN tarjetas_nfc t
                ON t.id_tarjeta = v.id_tarjeta
            ORDER BY v.fecha DESC
            LIMIT 3
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener ventas:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()
