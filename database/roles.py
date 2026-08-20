from database.connection import conectar
from database.logs import registrar_log


MODULOS = {
    "/dashboard": "Dashboard",
    "/ventas": "Ventas",
    "/productos": "Productos",
    "/categorias": "Categorías",
    "/inventario": "Inventario",
    "/tarjetas": "Tarjetas NFC",
    "/dispensadores": "Dispensadores",
    "/usuarios": "Usuarios",
    "/roles": "Roles",
    "/movimientos": "Movimientos",
    "/logs": "Logs",
    "/configuracion": "Configuración",
    "/mantenimientos": "Mantenimientos",
    "/entregas": "Entregas",
}

PERMISOS_INICIALES = {
    "operador": {
        "/dashboard", "/ventas", "/tarjetas", "/movimientos", "/entregas"
    },
    "inventario": {
        "/dashboard", "/productos", "/categorias",
        "/inventario", "/dispensadores"
    },
    "soporte": {"/dashboard", "/dispensadores", "/mantenimientos"},
    "supervisor": {"/dashboard", "/ventas", "/movimientos", "/logs"},
}


def preparar_permisos():
    db = conectar()
    if db is None:
        return False
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS permisos (
                id_permiso INT AUTO_INCREMENT PRIMARY KEY,
                ruta VARCHAR(100) NOT NULL UNIQUE,
                nombre VARCHAR(80) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rol_permisos (
                id_rol INT NOT NULL,
                id_permiso INT NOT NULL,
                PRIMARY KEY (id_rol, id_permiso),
                CONSTRAINT fk_rol_permisos_rol
                    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
                    ON DELETE CASCADE,
                CONSTRAINT fk_rol_permisos_permiso
                    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        for ruta, nombre in MODULOS.items():
            cursor.execute(
                """
                INSERT INTO permisos (ruta, nombre) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre)
                """,
                (ruta, nombre)
            )

        cursor.execute("SELECT id_rol, nombre FROM roles")
        for rol in cursor.fetchall():
            nombre_rol = str(rol["nombre"]).strip().casefold()
            cursor.execute(
                "SELECT COUNT(*) AS total FROM rol_permisos WHERE id_rol=%s",
                (rol["id_rol"],)
            )
            if int(cursor.fetchone()["total"]) > 0:
                continue
            rutas = (
                set(MODULOS)
                if nombre_rol in {"administrador", "admin"}
                else PERMISOS_INICIALES.get(nombre_rol, {"/dashboard"})
            )
            _reemplazar_permisos(cursor, rol["id_rol"], rutas)
        db.commit()
        return True
    except Exception as error:
        db.rollback()
        print("Error al preparar permisos:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        db.close()


def _reemplazar_permisos(cursor, id_rol, rutas):
    rutas = set(rutas) & set(MODULOS)
    rutas.add("/dashboard")
    cursor.execute("DELETE FROM rol_permisos WHERE id_rol=%s", (id_rol,))
    for ruta in rutas:
        cursor.execute(
            """
            INSERT INTO rol_permisos (id_rol, id_permiso)
            SELECT %s, id_permiso FROM permisos WHERE ruta=%s
            """,
            (id_rol, ruta)
        )


def obtener_permisos_rol(conexion, id_rol):
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.ruta
            FROM rol_permisos rp
            INNER JOIN permisos p ON p.id_permiso=rp.id_permiso
            WHERE rp.id_rol=%s
            """,
            (id_rol,)
        )
        return [fila["ruta"] for fila in cursor.fetchall()]
    finally:
        cursor.close()


def obtener_roles_admin():
    preparar_permisos()
    db = conectar()
    if db is None:
        return []
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT r.id_rol, r.nombre, r.descripcion,
                   COUNT(DISTINCT u.id_usuario) AS usuarios
            FROM roles r
            LEFT JOIN usuarios u ON u.id_rol=r.id_rol
            GROUP BY r.id_rol, r.nombre, r.descripcion
            ORDER BY r.nombre
            """
        )
        roles = cursor.fetchall()
        for rol in roles:
            rol["permisos"] = obtener_permisos_rol(db, rol["id_rol"])
        return roles
    except Exception as error:
        print("Error al obtener roles:", error)
        return []
    finally:
        if cursor:
            cursor.close()
        db.close()


def guardar_rol(id_rol, nombre, descripcion, rutas, id_usuario):
    nombre = str(nombre or "").strip()
    descripcion = str(descripcion or "").strip() or None
    if not nombre or len(nombre) > 50:
        return {"exito": False, "mensaje": "Nombre de rol no válido"}
    if descripcion and len(descripcion) > 200:
        return {"exito": False, "mensaje": "La descripción es muy larga"}

    db = conectar()
    if db is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        if id_rol is None:
            cursor.execute(
                "INSERT INTO roles (nombre, descripcion) VALUES (%s, %s)",
                (nombre, descripcion)
            )
            id_rol = cursor.lastrowid
            accion = "Crear rol"
        else:
            cursor.execute(
                "SELECT nombre FROM roles WHERE id_rol=%s FOR UPDATE",
                (id_rol,)
            )
            rol_actual = cursor.fetchone()
            if rol_actual is None:
                return {"exito": False, "mensaje": "El rol no existe"}
            if str(rol_actual["nombre"]).strip().casefold() in {
                "administrador", "admin"
            }:
                nombre = rol_actual["nombre"]
            cursor.execute(
                """
                UPDATE roles SET nombre=%s, descripcion=%s WHERE id_rol=%s
                """,
                (nombre, descripcion, id_rol)
            )
            accion = "Actualizar rol"

        rutas_finales = (
            set(MODULOS)
            if nombre.casefold() in {"administrador", "admin"}
            else set(rutas)
        )
        _reemplazar_permisos(cursor, id_rol, rutas_finales)
        if not registrar_log(
            "Admin", accion, f"Rol '{nombre}'",
            id_usuario=id_usuario, conexion=db
        ):
            raise RuntimeError("No se pudo registrar el cambio")
        db.commit()
        return {"exito": True, "mensaje": "Rol guardado correctamente"}
    except Exception as error:
        db.rollback()
        print("Error al guardar rol:", error)
        return {"exito": False, "mensaje": "El nombre ya existe o no se pudo guardar"}
    finally:
        if cursor:
            cursor.close()
        db.close()


def eliminar_rol(id_rol, id_usuario):
    db = conectar()
    if db is None:
        return {"exito": False, "mensaje": "Base de datos no disponible"}
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT nombre FROM roles WHERE id_rol=%s FOR UPDATE", (id_rol,)
        )
        rol = cursor.fetchone()
        if rol is None:
            return {"exito": False, "mensaje": "El rol no existe"}
        if str(rol["nombre"]).strip().casefold() in {"administrador", "admin"}:
            return {"exito": False, "mensaje": "No puede eliminar el rol administrador"}
        cursor.execute(
            "SELECT COUNT(*) AS total FROM usuarios WHERE id_rol=%s", (id_rol,)
        )
        if int(cursor.fetchone()["total"]) > 0:
            return {"exito": False, "mensaje": "El rol tiene usuarios asignados"}
        cursor.execute("DELETE FROM roles WHERE id_rol=%s", (id_rol,))
        if not registrar_log(
            "Admin", "Eliminar rol", f"Se eliminó el rol '{rol['nombre']}'",
            id_usuario=id_usuario, conexion=db
        ):
            raise RuntimeError("No se pudo registrar la eliminación")
        db.commit()
        return {"exito": True, "mensaje": "Rol eliminado"}
    except Exception as error:
        db.rollback()
        print("Error al eliminar rol:", error)
        return {"exito": False, "mensaje": "No se pudo eliminar el rol"}
    finally:
        if cursor:
            cursor.close()
        db.close()
