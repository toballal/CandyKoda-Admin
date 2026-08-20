from database.connection import conectar
from database.logs import registrar_log


ROLES_GESTION = {"administrador", "admin", "inventario"}


def _rol_autorizado(cursor, id_usuario):
    cursor.execute(
        """
        SELECT r.nombre AS rol
        FROM usuarios u
        INNER JOIN roles r ON r.id_rol = u.id_rol
        WHERE u.id_usuario=%s AND u.estado='Activo'
        """,
        (id_usuario,)
    )
    usuario = cursor.fetchone()
    rol = str((usuario or {}).get("rol") or "").strip().casefold()
    return rol in ROLES_GESTION


def obtener_categorias_admin():
    conexion = conectar()
    if conexion is None:
        return []
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                c.id_categoria,
                c.nombre,
                c.descripcion,
                c.estado,
                COUNT(p.id_producto) AS productos
            FROM categorias c
            LEFT JOIN productos p ON p.id_categoria = c.id_categoria
            GROUP BY
                c.id_categoria, c.nombre, c.descripcion, c.estado
            ORDER BY c.nombre
            """
        )
        return cursor.fetchall()
    except Exception as error:
        print("Error al obtener categorías:", error)
        return []
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def agregar_categoria(nombre, descripcion, estado, id_usuario):
    return _guardar_categoria(
        None, nombre, descripcion, estado, id_usuario
    )


def actualizar_categoria(
    id_categoria,
    nombre,
    descripcion,
    estado,
    id_usuario
):
    return _guardar_categoria(
        id_categoria, nombre, descripcion, estado, id_usuario
    )


def _guardar_categoria(
    id_categoria,
    nombre,
    descripcion,
    estado,
    id_usuario
):
    nombre = str(nombre or "").strip()
    descripcion = str(descripcion or "").strip() or None
    if not nombre or len(nombre) > 80:
        return {"exito": False, "mensaje": "Nombre de categoría no válido"}
    if descripcion and len(descripcion) > 200:
        return {"exito": False, "mensaje": "La descripción es muy larga"}
    if estado not in {"Activa", "Inactiva"}:
        return {"exito": False, "mensaje": "Estado no válido"}

    conexion = conectar()
    if conexion is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not _rol_autorizado(cursor, id_usuario):
            return {"exito": False, "mensaje": "No tiene permiso"}

        if id_categoria is None:
            cursor.execute(
                """
                INSERT INTO categorias (nombre, descripcion, estado)
                VALUES (%s, %s, %s)
                """,
                (nombre, descripcion, estado)
            )
            accion = "Crear categoría"
        else:
            cursor.execute(
                """
                UPDATE categorias
                SET nombre=%s, descripcion=%s, estado=%s
                WHERE id_categoria=%s
                """,
                (nombre, descripcion, estado, id_categoria)
            )
            accion = "Actualizar categoría"

        if not registrar_log(
            "Admin",
            accion,
            f"Categoría '{nombre}'",
            id_usuario=id_usuario,
            conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar el cambio")
        conexion.commit()
        return {"exito": True, "mensaje": "Categoría guardada correctamente"}
    except Exception as error:
        conexion.rollback()
        print("Error al guardar categoría:", error)
        return {
            "exito": False,
            "mensaje": "El nombre ya existe o no se pudo guardar"
        }
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def eliminar_categoria(id_categoria, id_usuario):
    conexion = conectar()
    if conexion is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not _rol_autorizado(cursor, id_usuario):
            return {"exito": False, "mensaje": "No tiene permiso"}

        cursor.execute(
            """
            SELECT nombre FROM categorias
            WHERE id_categoria=%s FOR UPDATE
            """,
            (id_categoria,)
        )
        categoria = cursor.fetchone()
        if categoria is None:
            return {"exito": False, "mensaje": "La categoría no existe"}

        cursor.execute(
            "SELECT COUNT(*) AS total FROM productos WHERE id_categoria=%s",
            (id_categoria,)
        )
        if int(cursor.fetchone()["total"] or 0) > 0:
            return {
                "exito": False,
                "mensaje": (
                    "No puede eliminarse porque contiene productos"
                )
            }

        cursor.execute(
            "DELETE FROM categorias WHERE id_categoria=%s",
            (id_categoria,)
        )
        if not registrar_log(
            "Admin",
            "Eliminar categoría",
            f"Se eliminó definitivamente '{categoria['nombre']}'",
            id_usuario=id_usuario,
            conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la eliminación")
        conexion.commit()
        return {"exito": True, "mensaje": "Categoría eliminada"}
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar categoría:", error)
        return {"exito": False, "mensaje": "No se pudo eliminar la categoría"}
    finally:
        if cursor:
            cursor.close()
        conexion.close()
