from database.connection import conectar


def obtener_movimientos_tarjeta():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                m.id_movimiento,
                m.id_tarjeta,
                m.id_usuario,
                m.tipo,
                m.monto,
                m.saldo_anterior,
                m.saldo_nuevo,
                m.descripcion,
                m.fecha,

                t.uid,

                COALESCE(c.nombre, 'Sin cliente') AS cliente,

                u.nombre AS usuario

            FROM movimientos_tarjeta m

            INNER JOIN tarjetas_nfc t
                ON t.id_tarjeta = m.id_tarjeta

            LEFT JOIN clientes c
                ON c.id_cliente = t.id_cliente

            LEFT JOIN usuarios u
                ON u.id_usuario = m.id_usuario

            ORDER BY m.fecha DESC
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener movimientos:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()
