from database.connection import conectar
import hashlib
from database.roles import obtener_permisos_rol


def autenticarUsuario(contrasena, nombre):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        contrasena_hash = hashlib.sha256(
            contrasena.encode("utf-8")
        ).hexdigest()

        sql = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.correo,
                u.id_rol,
                r.nombre AS rol,
                u.estado
            FROM usuarios u
            INNER JOIN roles r
                ON r.id_rol = u.id_rol
            WHERE BINARY u.nombre = BINARY %s
              AND u.contrasena_hash = %s
              AND u.estado = 'Activo'
        """

        cursor.execute(
            sql,
            (
                nombre,
                contrasena_hash
            )
        )

        usuario = cursor.fetchone()

        if usuario:
            usuario["permisos"] = obtener_permisos_rol(
                conexion,
                usuario["id_rol"]
            )

        return usuario

    except Exception as e:
        print("Error al iniciar sesión:", e)
        return None

    finally:
        if cursor:
            cursor.close()

        conexion.close()

