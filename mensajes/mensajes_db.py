# mensajes_db.py
import sqlite3, os
from datetime import datetime

DB_NAME = "mensajes.db"

# mensajes_db.py  (nueva versión)
def inicializar_bd():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
              CREATE TABLE correos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,   -- ← INTEGER PK = id único
                remitente   TEXT NOT NULL,
                destinatario TEXT NOT NULL,
                asunto      TEXT,
                contenido   TEXT,
                fecha       TEXT,
                leido       INTEGER DEFAULT 0
              )
            """)
            conn.commit()


def create_message(remitente, destinatario, asunto, contenido):
    fecha = datetime.utcnow().isoformat()
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
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, remitente, destinatario, asunto, contenido, fecha, leido "
            "FROM correos WHERE destinatario=? ORDER BY fecha DESC LIMIT ?",
            (usuario, limit)
        )
        return cur.fetchall()

def get_outbox(usuario, limit=10):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, remitente, destinatario, asunto, contenido, fecha, leido "
            "FROM correos WHERE remitente=? ORDER BY fecha DESC LIMIT ?",
            (usuario, limit)
        )
        return cur.fetchall()

def mark_as_read(id_, usuario):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE correos SET leido=1 WHERE id=? AND destinatario=?",
            (id_, usuario)
        )
        conn.commit()

def delete_message(id_, usuario, bandeja):
    """
    bandeja: 'entrada' or 'salida'
    """
    col = "destinatario" if bandeja == "entrada" else "remitente"
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            f"DELETE FROM correos WHERE id=? AND {col}=?",
            (id_, usuario)
        )
        conn.commit()
