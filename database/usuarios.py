from database.connection import conectar
import hashlib
import secrets
from threading import Lock
from database.logs import registrar_log


_correo_preparado = False
_correo_lock = Lock()


def _asegurar_columna_correo(conexion):
    """Actualiza instalaciones existentes para admitir correo de usuario."""
    global _correo_preparado

    if _correo_preparado:
        return

    with _correo_lock:
        if _correo_preparado:
            return

        cursor = conexion.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'correo'")
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    ALTER TABLE usuarios
                    ADD COLUMN correo VARCHAR(255) NULL AFTER nombre
                    """
                )

            cursor.execute(
                """
                SHOW INDEX FROM usuarios
                WHERE Key_name = 'uq_usuarios_correo'
                """
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    ALTER TABLE usuarios
                    ADD UNIQUE INDEX uq_usuarios_correo (correo)
                    """
                )

            conexion.commit()
            _correo_preparado = True
        finally:
            cursor.close()


def preparar_usuarios():
    conexion = conectar()
    if conexion is None:
        return False
    try:
        _asegurar_columna_correo(conexion)
        return True
    except Exception as error:
        print("Error al preparar usuarios:", error)
        return False
    finally:
        conexion.close()


# =========================================================
# OBTENER USUARIOS
# =========================================================

def obtener_usuarios():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        _asegurar_columna_correo(conexion)
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.correo,
                u.estado,
                r.id_rol,
                r.nombre AS rol
            FROM usuarios u
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            ORDER BY u.nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener usuarios:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# OBTENER ROLES
# =========================================================

def obtener_roles():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_rol,
                nombre
            FROM roles
            ORDER BY nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener roles:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# AGREGAR USUARIO
# =========================================================

def agregar_usuario(
    nombre,
    correo,
    contrasena,
    id_rol,
    estado="Activo"
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        _asegurar_columna_correo(conexion)
        cursor = conexion.cursor()

        # Encriptar contraseña con SHA-256
        contrasena_hash = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest()

        sql = """
            INSERT INTO usuarios
            (
                nombre,
                correo,
                contrasena_hash,
                id_rol,
                estado
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                nombre,
                correo,
                contrasena_hash,
                id_rol,
                estado
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al agregar usuario:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# ACTUALIZAR USUARIO
# =========================================================

def actualizar_usuario(
    id_usuario,
    nombre,
    correo,
    id_rol
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        _asegurar_columna_correo(conexion)
        cursor = conexion.cursor()

        sql = """
            UPDATE usuarios
            SET
                nombre = %s,
                correo = %s,
                id_rol = %s
            WHERE id_usuario = %s
        """

        cursor.execute(
            sql,
            (
                nombre,
                correo,
                id_rol,
                id_usuario
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al actualizar usuario:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# CAMBIAR ESTADO
# =========================================================

def cambiar_estado_usuario(
    id_usuario,
    estado
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        if estado not in ("Activo", "Inactivo"):
            return False

        sql = """
            UPDATE usuarios
            SET estado = %s
            WHERE id_usuario = %s
        """

        cursor.execute(
            sql,
            (
                estado,
                id_usuario
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print(
            "Error al cambiar estado del usuario:",
            e
        )

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# CAMBIAR CONTRASEÑA
# =========================================================

def cambiar_contrasena(
    id_usuario,
    nueva_contrasena
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        nueva_hash = hashlib.sha256(
            nueva_contrasena.encode("utf-8")
        ).hexdigest()

        sql = """
            UPDATE usuarios
            SET contrasena_hash = %s
            WHERE id_usuario = %s
        """

        cursor.execute(
            sql,
            (
                nueva_hash,
                id_usuario
            )
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print(
            "Error al cambiar contraseña:",
            e
        )

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


def eliminar_usuario(id_usuario, id_usuario_actual):
    if id_usuario == id_usuario_actual:
        return {
            "exito": False,
            "mensaje": "No puede eliminar su propia cuenta"
        }

    conexion = conectar()
    if conexion is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.nombre, r.nombre AS rol
            FROM usuarios u
            INNER JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s
            """,
            (id_usuario_actual,)
        )
        actor = cursor.fetchone()
        if str((actor or {}).get("rol") or "").strip().casefold() not in {
            "administrador", "admin"
        }:
            return {"exito": False, "mensaje": "No tiene permiso"}

        cursor.execute(
            """
            SELECT nombre FROM usuarios
            WHERE id_usuario = %s FOR UPDATE
            """,
            (id_usuario,)
        )
        objetivo = cursor.fetchone()
        if objetivo is None:
            return {"exito": False, "mensaje": "El usuario no existe"}

        cursor.execute(
            """
            SELECT
                EXISTS(SELECT 1 FROM logs WHERE id_usuario = %s)
                OR EXISTS(SELECT 1 FROM movimientos_inventario WHERE id_usuario = %s)
                OR EXISTS(SELECT 1 FROM movimientos_tarjeta WHERE id_usuario = %s)
                OR EXISTS(SELECT 1 FROM mantenimientos WHERE id_usuario = %s)
                AS tiene_historial
            """,
            (id_usuario, id_usuario, id_usuario, id_usuario)
        )
        if cursor.fetchone()["tiene_historial"]:
            return {
                "exito": False,
                "mensaje": "El usuario tiene historial; debe inactivarlo"
            }

        cursor.execute(
            "DELETE FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )
        if not registrar_log(
            "Admin",
            "Eliminar usuario",
            f"Se eliminó físicamente al usuario '{objetivo['nombre']}'",
            id_usuario=id_usuario_actual,
            conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la eliminación")
        conexion.commit()
        return {"exito": True, "mensaje": "Usuario eliminado"}
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar usuario:", error)
        return {
            "exito": False,
            "mensaje": "El usuario tiene relaciones y no puede eliminarse"
        }
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def anonimizar_usuario(id_usuario, id_usuario_actual):
    if id_usuario == id_usuario_actual:
        return {
            "exito": False,
            "mensaje": "No puede retirar su propia cuenta"
        }

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
            WHERE u.id_usuario=%s AND u.estado='Activo'
            """,
            (id_usuario_actual,)
        )
        actor = cursor.fetchone()
        if str((actor or {}).get("rol") or "").strip().casefold() not in {
            "administrador", "admin"
        }:
            return {"exito": False, "mensaje": "No tiene permiso"}

        cursor.execute(
            "SELECT nombre FROM usuarios WHERE id_usuario=%s FOR UPDATE",
            (id_usuario,)
        )
        usuario = cursor.fetchone()
        if usuario is None:
            return {"exito": False, "mensaje": "El usuario no existe"}

        nombre_anonimo = f"usuario_eliminado_{id_usuario}"
        correo_anonimo = f"eliminado_{id_usuario}@invalid.local"
        hash_aleatorio = hashlib.sha256(
            secrets.token_bytes(32)
        ).hexdigest()
        cursor.execute(
            """
            UPDATE usuarios
            SET nombre=%s, correo=%s, contrasena_hash=%s, estado='Inactivo'
            WHERE id_usuario=%s
            """,
            (
                nombre_anonimo,
                correo_anonimo,
                hash_aleatorio,
                id_usuario
            )
        )
        if not registrar_log(
            "Admin",
            "Anonimizar usuario",
            f"Se retiró y anonimizó la cuenta '{usuario['nombre']}'",
            id_usuario=id_usuario_actual,
            conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la anonimización")
        conexion.commit()
        return {
            "exito": True,
            "mensaje": "Usuario retirado y anonimizado"
        }
    except Exception as error:
        conexion.rollback()
        print("Error al anonimizar usuario:", error)
        return {"exito": False, "mensaje": "No se pudo retirar el usuario"}
    finally:
        if cursor:
            cursor.close()
        conexion.close()
