# mensajes_db.py
import sqlite3, os
from threading import Lock
from datetime import datetime

DB_NAME = "mensajes.db"

db_lock = Lock()

# mensajes_db.py  (nueva versión)
def inicializar_bd():
    is_new = not os.path.exists(DB_NAME)

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        if is_new:
            conn.execute("""
              CREATE TABLE correos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente TEXT NOT NULL,
                destinatario TEXT NOT NULL,
                asunto TEXT,
                contenido TEXT,
                fecha TEXT,
                leido INTEGER DEFAULT 0
              )
            """)
            conn.commit()


def create_message(remitente, destinatario, asunto, contenido):
    fecha = datetime.utcnow().isoformat()
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute(
            "INSERT INTO correos (remitente, destinatario, asunto, contenido, fecha)"
            " VALUES (?,?,?,?,?)",
            (remitente, destinatario, asunto, contenido, fecha)
            )
            conn.commit()
            return str(cur.lastrowid)   # ← id generado (str para el proto)


def get_inbox(usuario, limit=10):
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, remitente, destinatario, asunto, contenido, fecha, leido "
                "FROM correos WHERE destinatario=? AND eliminado_entrada=0 ORDER BY fecha DESC LIMIT ?",
                (usuario, limit)
            )
            return cur.fetchall()

def get_outbox(usuario, limit=10):
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, remitente, destinatario, asunto, contenido, fecha, leido "
                "FROM correos WHERE remitente=? AND eliminado_salida=0 ORDER BY fecha DESC LIMIT ?",
                (usuario, limit)
            )
            return cur.fetchall()

def mark_as_read(id_, usuario):
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "UPDATE correos SET leido=1 WHERE id=? AND destinatario=?",
                (id_, usuario)
            )
            conn.commit()

def marcar_eliminado(id_, usuario, campo):
    """
    Marca un correo como eliminado lógicamente en la columna correspondiente.
    campo: 'eliminado_entrada' o 'eliminado_salida'
    """
    if campo not in ("eliminado_entrada", "eliminado_salida"):
        return
    columna = "destinatario" if campo == "eliminado_entrada" else "remitente"
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                f"UPDATE correos SET {campo}=1 WHERE id=? AND {columna}=?",
                (id_, usuario)
            )
            conn.commit()


# Borra físicamente el mensaje si ambos lo eliminaron
def borrar_si_ambos_eliminaron(id_):
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "DELETE FROM correos WHERE id=? AND eliminado_entrada=1 AND eliminado_salida=1",
                (id_,)
            )
            conn.commit()
"""
def delete_message(id_, usuario, bandeja):
    #bandeja: 'entrada' or 'salida'
    col = "destinatario" if bandeja == "entrada" else "remitente"
    with db_lock:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                f"DELETE FROM correos WHERE id=? AND {col}=?",
                (id_, usuario)
            )
            conn.commit()
"""