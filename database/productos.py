from database.connection import conectar
from database.logs import registrar_log


# =========================================================
# OBTENER PRODUCTOS
# =========================================================

def obtener_productos():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                p.id_producto,
                p.nombre,
                p.descripcion,
                p.precio,
                p.stock,
                p.stock_minimo,
                p.imagen,
                p.estado,
                c.nombre AS categoria,
                d.id_dispensador
            FROM productos p
            INNER JOIN categorias c
                ON p.id_categoria = c.id_categoria
            LEFT JOIN dispensadores d
                ON d.id_producto = p.id_producto
            ORDER BY p.nombre
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


# =========================================================
# ACTUALIZAR PRODUCTO
# =========================================================

def actualizar_producto(
    id_producto,
    nombre,
    precio,
    id_usuario=None
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:

        cursor = conexion.cursor()

        sql = """
            UPDATE productos
            SET
                nombre = %s,
                precio = %s
            WHERE id_producto = %s
        """

        cursor.execute(
            sql,
            (
                nombre,
                precio,
                id_producto
            )
        )

        # =================================================
        # REGISTRAR USUARIO QUE HIZO EL CAMBIO
        # =================================================

        registrar_log(
            modulo="Admin",
            accion="Actualizar producto",
            descripcion=(
                f"Producto #{id_producto} actualizado: "
                f"{nombre}, precio {precio}"
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:

        print("Error al actualizar producto:", e)

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# AGREGAR PRODUCTO
# =========================================================

def agregar_producto(
    nombre,
    descripcion,
    precio,
    id_categoria,
    imagen,
    estado="Disponible",
    id_usuario=None
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:

        cursor = conexion.cursor()

        sql = """
            INSERT INTO productos
            (
                nombre,
                descripcion,
                precio,
                id_categoria,
                imagen,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                nombre,
                descripcion,
                precio,
                id_categoria,
                imagen,
                estado
            )
        )

        id_producto = cursor.lastrowid

        # =================================================
        # REGISTRAR USUARIO QUE CREÓ EL PRODUCTO
        # =================================================

        registrar_log(
            modulo="Admin",
            accion="Crear producto",
            descripcion=(
                f"Producto #{id_producto} creado: "
                f"{nombre}"
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()

        return True

    except Exception as e:

        print("Error al agregar producto:", e)

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# OBTENER CATEGORÍAS
# =========================================================

def obtener_categorias():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:

        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_categoria,
                nombre
            FROM categorias
            ORDER BY nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:

        print("Error al obtener categorías:", e)

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# CAMBIAR ESTADO DEL PRODUCTO
# =========================================================

def cambiar_estado_producto(
    id_producto,
    estado,
    id_usuario=None
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:

        cursor = conexion.cursor()

        if estado not in (
            "Disponible",
            "Inactivo"
        ):
            return False

        sql = """
            UPDATE productos
            SET estado = %s
            WHERE id_producto = %s
        """

        cursor.execute(
            sql,
            (
                estado,
                id_producto
            )
        )

        # =================================================
        # REGISTRAR USUARIO QUE CAMBIÓ EL ESTADO
        # =================================================

        registrar_log(
            modulo="Admin",
            accion="Cambiar estado de producto",
            descripcion=(
                f"Producto #{id_producto} "
                f"cambió a estado {estado}"
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:

        print(
            "Error al cambiar estado del producto:",
            e
        )

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# DESACTIVAR PRODUCTO
# =========================================================

def eliminar_producto(
    id_producto,
    id_usuario=None
):

    return cambiar_estado_producto(
        id_producto,
        "Inactivo",
        id_usuario
    )


# =========================================================
# REACTIVAR PRODUCTO
# =========================================================

def activar_producto(
    id_producto,
    id_usuario=None
):

    return cambiar_estado_producto(
        id_producto,
        "Disponible",
        id_usuario
    )


def eliminar_producto_definitivamente(id_producto, id_usuario):
    conexion = conectar()
    if conexion is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT r.nombre AS rol
            FROM usuarios u INNER JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s AND u.estado = 'Activo'
            """,
            (id_usuario,)
        )
        actor = cursor.fetchone()
        if str((actor or {}).get("rol") or "").strip().casefold() not in {
            "administrador", "admin"
        }:
            return {"exito": False, "mensaje": "No tiene permiso"}

        cursor.execute(
            "SELECT nombre FROM productos WHERE id_producto=%s FOR UPDATE",
            (id_producto,)
        )
        producto = cursor.fetchone()
        if producto is None:
            return {"exito": False, "mensaje": "El producto no existe"}

        cursor.execute(
            """
            SELECT
                EXISTS(SELECT 1 FROM detalle_venta WHERE id_producto=%s)
                OR EXISTS(SELECT 1 FROM movimientos_inventario WHERE id_producto=%s)
                OR EXISTS(SELECT 1 FROM dispensadores WHERE id_producto=%s)
                AS tiene_historial
            """,
            (id_producto, id_producto, id_producto)
        )
        if cursor.fetchone()["tiene_historial"]:
            return {
                "exito": False,
                "mensaje": (
                    "El producto tiene historial o un dispensador; "
                    "debe desactivarlo"
                )
            }

        cursor.execute(
            "DELETE FROM productos WHERE id_producto=%s",
            (id_producto,)
        )
        if not registrar_log(
            "Admin", "Eliminar producto",
            f"Se eliminó físicamente el producto '{producto['nombre']}'",
            id_usuario=id_usuario, conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la eliminación")
        conexion.commit()
        return {"exito": True, "mensaje": "Producto eliminado"}
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar producto:", error)
        return {
            "exito": False,
            "mensaje": "El producto tiene relaciones y no puede eliminarse"
        }
    finally:
        if cursor:
            cursor.close()
        conexion.close()
