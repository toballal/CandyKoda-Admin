from database.connection import conectar


# =========================================================
# REGISTRAR LOG
# =========================================================

def registrar_log(
    modulo,
    accion,
    descripcion=None,
    nivel="Informacion",
    id_usuario=None,
    conexion=None
):

    """
    Registra una actividad en la tabla logs.

    id_usuario:
        ID del usuario que realizó la acción.

    conexion:
        Si se entrega una conexión existente,
        el log utiliza la misma transacción.
    """

    conexion_propia = conexion is None

    db = conexion or conectar()

    if db is None:
        return False

    cursor = None

    try:

        # Validar módulo
        if modulo not in (
            "Admin",
            "Market",
            "Pay",
            "Arduino",
            "Servidor"
        ):
            return False

        # Validar nivel
        if nivel not in (
            "Informacion",
            "Advertencia",
            "Error"
        ):
            return False

        cursor = db.cursor()

        sql = """
            INSERT INTO logs
            (
                id_usuario,
                modulo,
                nivel,
                accion,
                descripcion
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                id_usuario,
                modulo,
                nivel,
                accion,
                descripcion
            )
        )

        # Si la conexión fue creada aquí,
        # hacemos commit directamente.
        if conexion_propia:
            db.commit()

        return cursor.rowcount > 0

    except Exception as e:

        print(
            "Error al registrar log:",
            e
        )

        if conexion_propia:
            db.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion_propia:
            db.close()


# =========================================================
# OBTENER LOGS
# =========================================================

def obtener_logs():

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
                l.id_log,
                l.id_usuario,
                l.modulo,
                l.nivel,
                l.accion,
                l.descripcion,
                l.fecha,
                COALESCE(u.nombre, 'Sistema') AS usuario
            FROM logs l
            LEFT JOIN usuarios u
                ON u.id_usuario = l.id_usuario
            ORDER BY l.fecha DESC
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:

        print(
            "Error al obtener logs:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# OBTENER LOGS RECIENTES
# =========================================================

def obtener_logs_recientes(
    limite=5
):

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
                l.id_log,
                l.id_usuario,
                l.modulo,
                l.nivel,
                l.accion,
                l.descripcion,
                l.fecha,
                COALESCE(u.nombre, 'Sistema') AS usuario
            FROM logs l
            LEFT JOIN usuarios u
                ON u.id_usuario = l.id_usuario
            ORDER BY l.fecha DESC
            LIMIT %s
        """

        cursor.execute(
            sql,
            (int(limite),)
        )

        return cursor.fetchall()

    except Exception as e:

        print(
            "Error al obtener logs recientes:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# RESUMEN DE LOGS
# =========================================================

def obtener_resumen_logs():

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
                nivel,
                COUNT(*) AS cantidad
            FROM logs
            GROUP BY nivel
            ORDER BY FIELD(
                nivel,
                'Error',
                'Advertencia',
                'Informacion'
            )
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:

        print(
            "Error al obtener resumen de logs:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()