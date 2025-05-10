import sys, getpass, grpc
from typing import Optional

import mensaje_pb2, mensaje_pb2_grpc

API: Optional[mensaje_pb2_grpc.MensajeriaStub] = None
AUTH: Optional[mensaje_pb2_grpc.AutenticadorStub] = None
TOKEN: str = ""
USER: str = ""

# ------------------------------
#  Inicialización del canal
# ------------------------------

def init_channel() -> None:
    global API, AUTH
    chan = grpc.insecure_channel("localhost:50051")
    AUTH = mensaje_pb2_grpc.AutenticadorStub(chan)
    API = mensaje_pb2_grpc.MensajeriaStub(chan)

# ------------------------------
#  Comandos del CLI
# ------------------------------

def cmd_register() -> None:
    u = input("Nuevo usuario: ")
    p = getpass.getpass("Contraseña: ")
    rsp = AUTH.Registrar(mensaje_pb2.AuthenticationRequest(usuario=u, contrasena=p))
    icon = "✅" if rsp.status else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_login() -> None:
    global TOKEN, USER
    u = input("Usuario: ")
    p = getpass.getpass("Contraseña: ")
    rsp = AUTH.Autenticar(mensaje_pb2.AuthenticationRequest(usuario=u, contrasena=p))
    if rsp.status:
        TOKEN, USER = rsp.token, u
        print("🔓  Sesión iniciada.")
    else:
        print("❌  ", rsp.mensaje)


def cmd_inbox() -> None:
    rsp = API.ObtenerBandejaEntrada(mensaje_pb2.UserRequest(usuario=USER, token=TOKEN))
    if not rsp.correos:
        print("(bandeja vacía)")
        return
    for c in rsp.correos:
        flag = "✓" if c.leido else "•"
        print(f"{flag} {c.idCorreo[:8]}  {c.remitente:<10}  {c.asunto}")


def cmd_send() -> None:
    dst = input("Para:    ")
    subj = input("Asunto:  ")
    body = input("Mensaje: ")
    rsp = API.EnviarCorreo(mensaje_pb2.CorreoNuevo(
        remitente=USER, destinatario=dst, asunto=subj, contenido=body, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_mark_read() -> None:
    mid = input("ID del correo a marcar leído: ")
    rsp = API.Leido(mensaje_pb2.LeidoRequest(idCorreo=mid, usuario=USER, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")


def cmd_delete() -> None:
    mid = input("ID del correo a eliminar: ")
    rsp = API.EliminarCorreo(mensaje_pb2.EliminarRequest(
        idCorreo=mid, usuario=USER, Bandeja=mensaje_pb2.ENTRADA, token=TOKEN))
    icon = "✅" if rsp.exito else "❌"
    print(f"{icon} {rsp.mensaje}")

# ------------------------------
#  Tabla de comandos
# ------------------------------

MENU = {
    "r": cmd_register,
    "l": cmd_login,
    "i": cmd_inbox,
    "s": cmd_send,
    "m": cmd_mark_read,
    "d": cmd_delete,
    "q": lambda: sys.exit(0),
}

# ------------------------------
#  Bucle interactivo
# ------------------------------

def main() -> None:
    init_channel()
    print("Comandos: r egistrar · l ogin · i nbox · s end · m ark read · d elete · q uit")
    while True:
        cmd = input("> ").strip().lower()
        MENU.get(cmd, lambda: print("¿? comando desconocido"))()


if __name__ == "__main__":
    main()
