from database.connection import conectar


# =========================================================
# OBTENER MANTENIMIENTOS
# =========================================================

def obtener_mantenimientos():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                m.id_mantenimiento,
                m.id_dispensador,
                m.id_usuario,
                m.tipo,
                m.descripcion,
                m.estado,
                m.fecha_inicio,
                m.fecha_fin,

                d.nombre AS dispensador,
                d.numero_servo,

                p.nombre AS producto,

                u.nombre AS usuario

            FROM mantenimientos m

            INNER JOIN dispensadores d
                ON d.id_dispensador = m.id_dispensador

            LEFT JOIN productos p
                ON p.id_producto = d.id_producto

            LEFT JOIN usuarios u
                ON u.id_usuario = m.id_usuario

            ORDER BY m.fecha_inicio DESC
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print("Error al obtener mantenimientos:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# OBTENER DISPENSADORES
# =========================================================

def obtener_dispensadores():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_dispensador,
                nombre,
                numero_servo,
                estado
            FROM dispensadores
            ORDER BY id_dispensador
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


# =========================================================
# OBTENER USUARIOS
# =========================================================

def obtener_usuarios():

    conexion = conectar()

    if conexion is None:
        return []

    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                id_usuario,
                nombre
            FROM usuarios
            WHERE estado = 'Activo'
            ORDER BY nombre
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
# REGISTRAR MANTENIMIENTO
# =========================================================

def registrar_mantenimiento(
    id_dispensador,
    id_usuario,
    tipo,
    descripcion
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            INSERT INTO mantenimientos
            (
                id_dispensador,
                id_usuario,
                tipo,
                descripcion,
                estado
            )
            VALUES (%s, %s, %s, %s, 'Pendiente')
        """

        cursor.execute(
            sql,
            (
                id_dispensador,
                id_usuario,
                tipo,
                descripcion
            )
        )

        conexion.commit()

        return True

    except Exception as e:
        print("Error al registrar mantenimiento:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# INICIAR MANTENIMIENTO
# =========================================================

def iniciar_mantenimiento(id_mantenimiento):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE mantenimientos
            SET estado = 'En proceso'
            WHERE id_mantenimiento = %s
              AND estado = 'Pendiente'
        """

        cursor.execute(
            sql,
            (id_mantenimiento,)
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al iniciar mantenimiento:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()


# =========================================================
# COMPLETAR MANTENIMIENTO
# =========================================================

def completar_mantenimiento(id_mantenimiento):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        cursor = conexion.cursor()

        sql = """
            UPDATE mantenimientos
            SET
                estado = 'Completado',
                fecha_fin = NOW()
            WHERE id_mantenimiento = %s
              AND estado = 'En proceso'
        """

        cursor.execute(
            sql,
            (id_mantenimiento,)
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:
        print("Error al completar mantenimiento:", e)

        conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()

        conexion.close()