RUTAS_PROTEGIDAS = {
    "/dashboard",
    "/ventas",
    "/productos",
    "/categorias",
    "/inventario",
    "/tarjetas",
    "/dispensadores",
    "/usuarios",
    "/roles",
    "/movimientos",
    "/logs",
    "/configuracion",
    "/mantenimientos",
    "/entregas",
    "/perfil",
}

PERMISOS_POR_ROL = {
    "administrador": RUTAS_PROTEGIDAS,
    "admin": RUTAS_PROTEGIDAS,
    "operador": {
        "/dashboard",
        "/ventas",
        "/tarjetas",
        "/movimientos",
        "/entregas",
    },
    "inventario": {
        "/dashboard",
        "/productos",
        "/categorias",
        "/inventario",
        "/dispensadores",
    },
    "soporte": {
        "/dashboard",
        "/dispensadores",
        "/mantenimientos",
    },
    "supervisor": {
        "/dashboard",
        "/ventas",
        "/movimientos",
        "/logs",
    },
}

ACCIONES_POR_ROL = {
    "administrador": {
        "recargar_dispensador",
        "eliminar_usuario",
        "anonimizar_usuario",
        "eliminar_tarjeta",
        "retirar_tarjeta",
        "eliminar_producto",
    },
    "admin": {
        "recargar_dispensador",
        "eliminar_usuario",
        "anonimizar_usuario",
        "eliminar_tarjeta",
        "retirar_tarjeta",
        "eliminar_producto",
    },
    "inventario": {"recargar_dispensador"},
}


def normalizar_rol(usuario):
    if not isinstance(usuario, dict):
        return ""

    return str(usuario.get("rol") or "").strip().casefold()


def es_usuario_administrador(usuario):
    return normalizar_rol(usuario) in {"administrador", "admin"}


def puede_acceder(usuario, ruta):
    if ruta == "/perfil":
        return isinstance(usuario, dict) and bool(usuario.get("id_usuario"))

    if isinstance(usuario, dict) and "permisos" in usuario:
        return ruta in set(usuario.get("permisos") or [])

    rol = normalizar_rol(usuario)
    permisos = PERMISOS_POR_ROL.get(rol, {"/dashboard"})
    return ruta in permisos


def puede_realizar(usuario, accion):
    rol = normalizar_rol(usuario)
    return accion in ACCIONES_POR_ROL.get(rol, set())
