from database.connection import conectar
from database.logs import registrar_log


def get_dispensadores():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                d.id_dispensador,
                d.id_producto,
                d.nombre AS dispensador,
                d.numero_servo,
                d.puerto_arduino,
                d.cantidad_disponible,
                d.estado,
                d.ultima_actualizacion,
                p.nombre AS producto,
                p.stock AS stock_producto,
                p.stock_minimo
            FROM dispensadores d
            LEFT JOIN productos p
                ON p.id_producto = d.id_producto
            ORDER BY d.id_dispensador
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener dispensadores:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def obtener_productos_disponibles():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_producto,
                nombre
            FROM productos
            WHERE estado = 'Disponible'
            ORDER BY nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener productos:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def asignar_producto_dispensador(
    id_dispensador,
    id_producto
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE dispensadores
            SET id_producto = %s
            WHERE id_dispensador = %s
        """

        cursor.execute(
            sql,
            (
                id_producto,
                id_dispensador
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al asignar producto:", e)
        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def quitar_producto_dispensador(
    id_dispensador
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE dispensadores
            SET id_producto = NULL
            WHERE id_dispensador = %s
        """

        cursor.execute(
            sql,
            (id_dispensador,)
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al quitar producto:", e)
        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def cambiar_estado_dispensador(
    id_dispensador,
    estado
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE dispensadores
            SET estado = %s
            WHERE id_dispensador = %s
        """

        cursor.execute(
            sql,
            (
                estado,
                id_dispensador
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al cambiar estado del dispensador:", e)
        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def recargar_dispensador(
    id_dispensador,
    cantidad,
    id_usuario
):
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return {"exito": False, "mensaje": "La cantidad no es válida"}

    if cantidad <= 0:
        return {
            "exito": False,
            "mensaje": "La cantidad debe ser mayor que cero"
        }

    conexion = conectar()
    if conexion is None:
        return {
            "exito": False,
            "mensaje": "No se pudo conectar a la base de datos"
        }

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT r.nombre AS rol
            FROM usuarios u
            INNER JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s
              AND u.estado = 'Activo'
            """,
            (id_usuario,)
        )
        usuario = cursor.fetchone()
        rol = str((usuario or {}).get("rol") or "").strip().casefold()

        if rol not in {"administrador", "admin", "inventario"}:
            return {
                "exito": False,
                "mensaje": "No tiene permiso para recargar dispensadores"
            }

        cursor.execute(
            """
            SELECT
                d.cantidad_disponible,
                d.id_producto,
                p.nombre AS producto,
                p.stock
            FROM dispensadores d
            LEFT JOIN productos p ON p.id_producto = d.id_producto
            WHERE d.id_dispensador = %s
            FOR UPDATE
            """,
            (id_dispensador,)
        )
        dispensador = cursor.fetchone()

        if dispensador is None:
            return {
                "exito": False,
                "mensaje": "El dispensador no existe"
            }

        if dispensador["id_producto"] is None:
            return {
                "exito": False,
                "mensaje": "Asigne un producto antes de recargar"
            }

        cantidad_anterior = int(
            dispensador["cantidad_disponible"] or 0
        )
        stock_producto = int(dispensador["stock"] or 0)
        cantidad_nueva = cantidad_anterior + cantidad

        if cantidad_nueva > stock_producto:
            return {
                "exito": False,
                "mensaje": (
                    f"La carga no puede superar el stock disponible "
                    f"del producto ({stock_producto})"
                )
            }

        cursor.execute(
            """
            UPDATE dispensadores
            SET cantidad_disponible = %s,
                estado = 'Disponible',
                ultima_actualizacion = NOW()
            WHERE id_dispensador = %s
            """,
            (cantidad_nueva, id_dispensador)
        )

        if not registrar_log(
            modulo="Admin",
            accion="Recargar dispensador",
            descripcion=(
                f"Dispensador #{id_dispensador}, "
                f"{dispensador['producto']}: "
                f"{cantidad_anterior} → {cantidad_nueva} unidades"
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la recarga")

        conexion.commit()
        return {
            "exito": True,
            "mensaje": "Dispensador recargado correctamente",
            "cantidad_anterior": cantidad_anterior,
            "cantidad_nueva": cantidad_nueva
        }

    except Exception as error:
        conexion.rollback()
        print("Error al recargar dispensador:", error)
        return {
            "exito": False,
            "mensaje": "No se pudo recargar el dispensador"
        }

    finally:
        if cursor:
            cursor.close()
        conexion.close()
        
