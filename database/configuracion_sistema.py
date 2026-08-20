from database.connection import conectar
from database.logs import registrar_log


CONFIGURACION_PREDETERMINADA = {
    "nombre_sistema": "Candy Koda",
    "stock_minimo": "10",
    "moneda": "CLP",
    "puerto_arduino": "COM3",
    "velocidad_serial": "9600",
    "video_fondo": "1",
    "market_mantenimiento": "0",
}

DESCRIPCIONES = {
    "nombre_sistema": "Nombre mostrado por el sistema",
    "stock_minimo": "Stock mínimo predeterminado",
    "moneda": "Moneda utilizada por el sistema",
    "puerto_arduino": "Puerto de comunicación con Arduino",
    "velocidad_serial": "Velocidad de comunicación serial",
    "video_fondo": "Muestra el video decorativo de fondo",
    "market_mantenimiento": "Bloquea compras en Candy Koda Market",
}


def _preparar(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS configuracion_sistema (
            clave VARCHAR(80) PRIMARY KEY,
            valor VARCHAR(255) NOT NULL,
            descripcion VARCHAR(255) NULL,
            actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


def _es_verdadero(valor):
    return str(valor).strip().casefold() in {
        "1", "true", "activo", "si", "sí"
    }


def obtener_configuraciones():
    configuracion = CONFIGURACION_PREDETERMINADA.copy()
    db = conectar()

    if db is None:
        return configuracion

    cursor = None
    try:
        cursor = db.cursor()
        _preparar(cursor)
        cursor.execute("SELECT clave, valor FROM configuracion_sistema")

        for clave, valor in cursor.fetchall():
            if clave in configuracion:
                configuracion[clave] = str(valor)

        return configuracion

    except Exception as error:
        print("Error al obtener la configuración:", error)
        return configuracion

    finally:
        if cursor:
            cursor.close()
        db.close()


def obtener_configuracion(clave, valor_predeterminado=None):
    if valor_predeterminado is None:
        valor_predeterminado = CONFIGURACION_PREDETERMINADA.get(clave)

    return obtener_configuraciones().get(clave, valor_predeterminado)


def guardar_configuraciones(valores, id_usuario=None):
    claves_desconocidas = set(valores) - set(CONFIGURACION_PREDETERMINADA)
    if claves_desconocidas:
        return False

    db = conectar()
    if db is None:
        return False

    cursor = None
    try:
        cursor = db.cursor()
        _preparar(cursor)

        sql = """
            INSERT INTO configuracion_sistema
                (clave, valor, descripcion)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                valor = VALUES(valor),
                descripcion = VALUES(descripcion)
        """

        for clave, valor in valores.items():
            cursor.execute(
                sql,
                (clave, str(valor), DESCRIPCIONES.get(clave)),
            )

        if not registrar_log(
            modulo="Admin",
            accion="Actualizar configuración",
            descripcion=(
                "Se actualizaron las opciones: "
                + ", ".join(sorted(valores))
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=db,
        ):
            raise RuntimeError(
                "No se pudo registrar el cambio de configuración"
            )

        db.commit()
        return True

    except Exception as error:
        db.rollback()
        print("Error al guardar la configuración:", error)
        return False

    finally:
        if cursor:
            cursor.close()
        db.close()


def obtener_modo_mantenimiento():
    return _es_verdadero(
        obtener_configuracion("market_mantenimiento", "0")
    )


def establecer_modo_mantenimiento(activo, id_usuario=None):
    return guardar_configuraciones(
        {"market_mantenimiento": "1" if activo else "0"},
        id_usuario=id_usuario,
    )
