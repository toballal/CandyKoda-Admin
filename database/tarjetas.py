from database.connection import conectar
from database.logs import registrar_log
from decimal import Decimal, InvalidOperation
import hashlib
import secrets


def obtener_tarjetas_admin():

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
                t.id_tarjeta,
                t.uid,
                t.saldo,
                t.estado,
                t.fecha_activacion,
                c.nombre AS cliente,
                c.rut
            FROM tarjetas_nfc t
            LEFT JOIN clientes c
                ON c.id_cliente = t.id_cliente
            ORDER BY c.nombre
        """

        cursor.execute(sql)

        return cursor.fetchall()

    except Exception as e:
        print(
            "Error al obtener tarjetas:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        conexion.close()


def cambiar_estado_tarjeta(
    id_tarjeta,
    estado
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:

        cursor = conexion.cursor()

        sql = """
            UPDATE tarjetas_nfc
            SET estado = %s
            WHERE id_tarjeta = %s
        """

        cursor.execute(
            sql,
            (
                estado,
                id_tarjeta
            )
        )

        registrar_log(
            "Admin",
            "Cambiar estado de tarjeta",
            f"Tarjeta #{id_tarjeta} cambió a estado {estado}",
            conexion=conexion
        )

        conexion.commit()

        return cursor.rowcount > 0

    except Exception as e:

        print(
            "Error al cambiar estado:",
            e
        )

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()


def recargar_tarjeta(
    id_tarjeta,
    monto,
    descripcion,
    id_usuario=None
):

    conexion = conectar()

    if conexion is None:
        return False

    cursor = None

    try:
        try:
            monto_decimal = Decimal(str(monto))
        except (InvalidOperation, ValueError, TypeError):
            return False

        if not monto_decimal.is_finite() or monto_decimal <= 0:
            return False

        cursor = conexion.cursor(
            dictionary=True
        )

        # Obtener saldo actual
        sql = """
            SELECT saldo
            FROM tarjetas_nfc
            WHERE id_tarjeta = %s
            FOR UPDATE
        """

        cursor.execute(
            sql,
            (id_tarjeta,)
        )

        tarjeta = cursor.fetchone()

        if tarjeta is None:
            return False

        saldo_anterior = Decimal(str(tarjeta["saldo"]))

        saldo_nuevo = (
            saldo_anterior
            + monto_decimal
        )

        # Actualizar saldo
        sql = """
            UPDATE tarjetas_nfc
            SET saldo = %s
            WHERE id_tarjeta = %s
        """

        cursor.execute(
            sql,
            (
                saldo_nuevo,
                id_tarjeta
            )
        )

        # Registrar movimiento
        sql = """
            INSERT INTO movimientos_tarjeta
            (
                id_tarjeta,
                tipo,
                monto_decimal,
                saldo_anterior,
                saldo_nuevo,
                descripcion
            )
            VALUES
            (
                %s,
                'Recarga',
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            sql,
            (
                id_tarjeta,
                monto,
                saldo_anterior,
                saldo_nuevo,
                descripcion
            )
        )

        registrar_log(
            modulo="Admin",
            accion="Recargar tarjeta",
            descripcion=(
                f"Tarjeta #{id_tarjeta} recargada por {monto_decimal}; "
                f"saldo {saldo_anterior} → {saldo_nuevo}"
            ),
            nivel="Informacion",
            id_usuario=id_usuario,
            conexion=conexion
        )

        conexion.commit()

        return True

    except Exception as e:

        print(
            "Error al recargar tarjeta:",
            e
        )

        conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        conexion.close()


def eliminar_tarjeta(id_tarjeta, id_usuario):
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
            "SELECT uid FROM tarjetas_nfc WHERE id_tarjeta=%s FOR UPDATE",
            (id_tarjeta,)
        )
        tarjeta = cursor.fetchone()
        if tarjeta is None:
            return {"exito": False, "mensaje": "La tarjeta no existe"}

        cursor.execute(
            """
            SELECT
                EXISTS(SELECT 1 FROM ventas WHERE id_tarjeta=%s)
                OR EXISTS(SELECT 1 FROM movimientos_tarjeta WHERE id_tarjeta=%s)
                AS tiene_historial
            """,
            (id_tarjeta, id_tarjeta)
        )
        if cursor.fetchone()["tiene_historial"]:
            return {
                "exito": False,
                "mensaje": "La tarjeta tiene historial; debe bloquearla"
            }

        cursor.execute(
            "DELETE FROM tarjetas_nfc WHERE id_tarjeta=%s",
            (id_tarjeta,)
        )
        if not registrar_log(
            "Admin", "Eliminar tarjeta",
            f"Se eliminó físicamente la tarjeta {tarjeta['uid']}",
            id_usuario=id_usuario, conexion=conexion
        ):
            raise RuntimeError("No se pudo registrar la eliminación")
        conexion.commit()
        return {"exito": True, "mensaje": "Tarjeta eliminada"}
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar tarjeta:", error)
        return {
            "exito": False,
            "mensaje": "La tarjeta tiene relaciones y no puede eliminarse"
        }
    finally:
        if cursor:
            cursor.close()
        conexion.close()
