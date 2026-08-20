import hashlib

from database.connection import conectar
from database.logs import registrar_log


def actualizar_perfil(
    id_usuario,
    nombre,
    correo,
    contrasena_actual,
    contrasena_nueva=None,
):
    nombre = str(nombre or "").strip()
    correo = str(correo or "").strip().lower()
    if not nombre or len(nombre) > 80:
        return {"exito": False, "mensaje": "Nombre de usuario no válido"}
    if not correo or len(correo) > 255:
        return {"exito": False, "mensaje": "Correo electrónico no válido"}
    if not contrasena_actual:
        return {"exito": False, "mensaje": "Ingrese su contraseña actual"}

    conexion = conectar()
    if conexion is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT nombre, correo, contrasena_hash
            FROM usuarios
            WHERE id_usuario=%s AND estado='Activo'
            FOR UPDATE
            """,
            (id_usuario,)
        )
        usuario = cursor.fetchone()
        if usuario is None:
            return {"exito": False, "mensaje": "La cuenta no está activa"}

        hash_actual = hashlib.sha256(
            contrasena_actual.encode("utf-8")
        ).hexdigest()
        if hash_actual != usuario["contrasena_hash"]:
            return {"exito": False, "mensaje": "La contraseña actual es incorrecta"}

        cursor.execute(
            """
            SELECT id_usuario FROM usuarios
            WHERE BINARY nombre=BINARY %s AND id_usuario<>%s
            """,
            (nombre, id_usuario)
        )
        if cursor.fetchone():
            return {"exito": False, "mensaje": "El nombre de usuario ya existe"}

        cursor.execute(
            """
            SELECT id_usuario FROM usuarios
            WHERE LOWER(correo)=LOWER(%s) AND id_usuario<>%s
            """,
            (correo, id_usuario)
        )
        if cursor.fetchone():
            return {"exito": False, "mensaje": "El correo ya está registrado"}

        nuevo_hash = usuario["contrasena_hash"]
        cambio_contrasena = bool(contrasena_nueva)
        if cambio_contrasena:
            nuevo_hash = hashlib.sha256(
                contrasena_nueva.encode("utf-8")
            ).hexdigest()

        cursor.execute(
            """
            UPDATE usuarios
            SET nombre=%s, correo=%s, contrasena_hash=%s
            WHERE id_usuario=%s
            """,
            (nombre, correo, nuevo_hash, id_usuario)
        )
        cambios = ["nombre/correo"]
        if cambio_contrasena:
            cambios.append("contraseña")
        if not registrar_log(
            "Admin",
            "Actualizar perfil",
            "El usuario actualizó " + " y ".join(cambios),
            id_usuario=id_usuario,
            conexion=conexion,
        ):
            raise RuntimeError("No se pudo registrar el cambio")
        conexion.commit()
        return {
            "exito": True,
            "mensaje": "Perfil actualizado correctamente",
            "nombre": nombre,
            "correo": correo,
        }
    except Exception as error:
        conexion.rollback()
        print("Error al actualizar perfil:", error)
        return {"exito": False, "mensaje": "No se pudo actualizar el perfil"}
    finally:
        if cursor:
            cursor.close()
        conexion.close()
