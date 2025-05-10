import sqlite3
import hashlib
import os

DB_NAME = "usuarios.db"

def inicializar_bd():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("""
                        CREATE TABLE usuarios (
                            nombre TEXT PRIMARY KEY,
                            contrasena_hash TEXT NOT NULL
                        )
                        """)
            conn.commit()
            print("Base de datos creada")
    else:
        print("Base de datos ya existe")

def registrar_usuarios(nombre, contrasena):
    hash_pass = hashlib.sha256(contrasena.encode()).hexdigest()
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO usuarios (nombre, contrasena_hash) VALUES (?, ?)", (nombre, hash_pass))
            conn.commit()
            return True, "Usuario registrado correctamente"
        except sqlite3.IntegrityError:
            return False, "El usuario ya existe"

def autenticar_usuario(nombre, contrasena):
    hash_pass = hashlib.sha256(contrasena.encode()).hexdigest()
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE nombre = ? AND contrasena_hash = ?", (nombre, hash_pass))
        if cur.fetchone():
            return True
        else:
            return False
        
def usuario_existe(nombre):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE nombre = ?", (nombre,))
        return cur.fetchone() is not None