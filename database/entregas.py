from database.connection import conectar


def obtener_entregas():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                e.id_entrega,
                e.id_detalle,
                e.id_dispensador,
                e.cantidad_solicitada,
                e.cantidad_entregada,
                e.sensor_confirmado,
                e.estado,
                e.mensaje_error,
                e.fecha_inicio,
                e.fecha_fin,

                dv.id_venta,
                dv.id_producto,

                p.nombre AS producto,

                d.nombre AS dispensador,
                d.numero_servo

            FROM entregas e

            INNER JOIN detalle_venta dv
                ON dv.id_detalle = e.id_detalle

            INNER JOIN productos p
                ON p.id_producto = dv.id_producto

            INNER JOIN dispensadores d
                ON d.id_dispensador = e.id_dispensador

            ORDER BY e.id_entrega DESC
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener entregas:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()