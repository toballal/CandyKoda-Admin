from database.connection import conectar
from database.logs import registrar_log


# =========================================================
# OBTENER INVENTARIO
# =========================================================

def obtener_inventario():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:

        cursor = conexion.cursor(
            dictionary=True
        )

        sql = """
            SELECT
                p.id_producto,
                p.nombre,
                p.stock,
                p.stock_minimo,
                d.id_dispensador,
                d.nombre AS dispensador
            FROM productos p
            LEFT JOIN dispensadores d
                ON d.id_producto = p.id_producto
            ORDER BY p.nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:

        print(
            "Error al obtener inventario:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# AGREGAR STOCK
# =========================================================

def agregar_stock(
    id_producto,
    cantidad,
    id_usuario=None
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT nombre, stock FROM productos WHERE id_producto = %s FOR UPDATE",
            (id_producto,)
        )
        producto = cursor.fetchone()

        if producto is None:
            return False

        stock_anterior = int(producto["stock"] or 0)
        stock_nuevo = stock_anterior + int(cantidad)

        cursor.execute(
            "UPDATE productos SET stock = %s WHERE id_producto = %s",
            (stock_nuevo, id_producto)
        )

        cursor.execute(
            """
                INSERT INTO movimientos_inventario
                    (id_producto, id_usuario, tipo, cantidad, stock_anterior, stock_nuevo, descripcion)
                VALUES (%s, %s, 'Entrada', %s, %s, %s, %s)
            """,
            (
                id_producto,
                id_usuario,
                cantidad,
                stock_anterior,
                stock_nuevo,
                "Stock agregado desde administración"
            )
        )

        registrar_log(
            "Admin",
            "Agregar stock",
            f"Se agregaron {cantidad} unidades a {producto['nombre']} "
            f"({stock_anterior} → {stock_nuevo})",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()
        return True

    except Exception as e:

        print(
            "Error al agregar stock:",
            e
        )

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()

def quitar_stock(id_producto, cantidad, id_usuario=None):
    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT nombre, stock FROM productos WHERE id_producto = %s FOR UPDATE",
            (id_producto,)
        )
        producto = cursor.fetchone()

        if producto is None:
            return False

        stock_anterior = int(producto["stock"] or 0)

        if stock_anterior < int(cantidad):
            return False

        stock_nuevo = stock_anterior - int(cantidad)

        cursor.execute(
            "UPDATE productos SET stock = %s WHERE id_producto = %s",
            (stock_nuevo, id_producto)
        )

        cursor.execute(
            """
                INSERT INTO movimientos_inventario
                    (id_producto, id_usuario, tipo, cantidad, stock_anterior, stock_nuevo, descripcion)
                VALUES (%s, %s, 'Salida', %s, %s, %s, %s)
            """,
            (
                id_producto,
                id_usuario,
                cantidad,
                stock_anterior,
                stock_nuevo,
                "Stock retirado desde administración"
            )
        )

        registrar_log(
            "Admin",
            "Quitar stock",
            f"Se retiraron {cantidad} unidades de {producto['nombre']} "
            f"({stock_anterior} → {stock_nuevo})",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()
        return True

    except Exception as e:
        print("Error al quitar stock:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()
