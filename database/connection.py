import mysql.connector
from mysql.connector import pooling
from threading import Lock


_pool = None
_pool_lock = Lock()


def _obtener_pool():
    """Crea una sola reserva de conexiones para toda la aplicación."""
    global _pool

    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = pooling.MySQLConnectionPool(
                    pool_name="candy_koda_admin_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    host="localhost",
                    user="admin",
                    password="candykoda1234",
                    database="candy_koda"
                )

    return _pool

def conectar():
    try:
        # Al cerrar esta conexión, mysql-connector la devuelve al pool en vez
        # de destruirla. Las funciones existentes no necesitan modificarse.
        return _obtener_pool().get_connection()
    except Exception as e:
        print("No se pudo conectar a la base de datos:", e)
        return None

def verificar_conexion():
    conexion = conectar()

    if conexion is None:
        return  False

    try:
        return conexion.is_connected()

    except Exception as e:
        print("Error al verificar la base de datos:", e)
        return False

    finally:
        conexion.close()



