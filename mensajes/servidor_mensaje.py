from concurrent import futures
import grpc
import uuid

# Proto stubs generated into paquete `mensajes`
import mensaje_pb2, mensaje_pb2_grpc
import mensajes_db
from usuarios import (
    inicializar_bd as inicializar_db_usuarios,
    registrar_usuarios,        # función real en usuarios.py
    autenticar_usuario,
)

# ------------------------------
# Utilidades de sesión en memoria
# ------------------------------

sesiones: dict[str, str] = {}

def generar_token() -> str:
    """UUID4 como token de sesión."""
    return str(uuid.uuid4())


def validar_token(token: str, usuario: str) -> bool:
    """Comprueba que el token emitido corresponde al usuario."""
    return sesiones.get(token) == usuario

# ------------------------------
#  Servicios gRPC
# ------------------------------

class Autenticador(mensaje_pb2_grpc.AutenticadorServicer):
    """RPCs de registro y autenticación de usuarios."""

    def Registrar(self, request, context):  # AuthenticationRequest → RegistroReply
        ok, msg = registrar_usuarios(request.usuario, request.contrasena)
        return mensaje_pb2.RegistroReply(status=ok, mensaje=msg)

    def Autenticar(self, request, context):  # AuthenticationRequest → AuthenticationReply
        if autenticar_usuario(request.usuario, request.contrasena):
            token = generar_token()
            sesiones[token] = request.usuario
            return mensaje_pb2.AuthenticationReply(status=True, mensaje="Autenticado", token=token)
        return mensaje_pb2.AuthenticationReply(status=False, mensaje="Credenciales inválidas", token="")


class Mensajeria(mensaje_pb2_grpc.MensajeriaServicer):
    """RPCs de mensajería (bandejas, envío, leído, eliminación)."""

    # ---------- Bandejas ----------
    def _build_bandeja_reply(self, filas):
        reply = mensaje_pb2.BandejaReply()
        for (cid, rem, dst, asu, cont, fecha, leido) in filas:
            c = reply.correos.add()
            c.idCorreo, c.remitente, c.destinatario = str(cid), rem, dst
            c.asunto, c.contenido, c.fecha = asu, cont, fecha
            c.leido = bool(leido)
        return reply

    def ObtenerBandejaEntrada(self, request, context):
        if not validar_token(request.token, request.usuario):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token inválido")
        filas = mensajes_db.get_inbox(request.usuario, limit=5)
        return self._build_bandeja_reply(filas)

    def ObtenerBandejaSalida(self, request, context):
        if not validar_token(request.token, request.usuario):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token inválido")
        filas = mensajes_db.get_outbox(request.usuario, limit=5)
        return self._build_bandeja_reply(filas)

    # ---------- Envío ----------
    def EnviarCorreo(self, request, context):
        if not validar_token(request.token, request.remitente):
            return mensaje_pb2.EnviarCorreoReply(exito=False, mensaje="Token inválido", idCorreo="")

        if len(mensajes_db.get_inbox(request.destinatario, 1000)) >= 5:
            return mensaje_pb2.EnviarCorreoReply(exito=False, mensaje="Bandeja de entrada llena", idCorreo="")
        if len(mensajes_db.get_outbox(request.remitente, 1000)) >= 5:
            return mensaje_pb2.EnviarCorreoReply(exito=False, mensaje="Bandeja de salida llena", idCorreo="")

        cid = mensajes_db.create_message(
            request.remitente,
            request.destinatario,
            request.asunto,
            request.contenido
        )                           # ahora create_message devuelve el id
        return mensaje_pb2.EnviarCorreoReply(
            exito=True, mensaje="Correo enviado", idCorreo=cid
        )

    # ---------- Leído / Eliminación ----------
    def Leido(self, request, context):
        if not validar_token(request.token, request.usuario):
            return mensaje_pb2.OperacionReply(exito=False, mensaje="Token inválido")
        mensajes_db.mark_as_read(request.idCorreo, request.usuario)
        return mensaje_pb2.OperacionReply(exito=True, mensaje="Correo marcado como leído")

    def EliminarCorreo(self, request, context):
        if not validar_token(request.token, request.usuario):
            return mensaje_pb2.OperacionReply(exito=False, mensaje="Token inválido")
        bandeja_str = "entrada" if request.Bandeja == mensaje_pb2.ENTRADA else "salida"
        mensajes_db.delete_message(request.idCorreo, request.usuario, bandeja_str)
        return mensaje_pb2.OperacionReply(exito=True, mensaje="Correo eliminado")


# ------------------------------
#  Bootstrap del servidor
# ------------------------------

def main():
    inicializar_db_usuarios()
    mensajes_db.inicializar_bd()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mensaje_pb2_grpc.add_AutenticadorServicer_to_server(Autenticador(), server)
    mensaje_pb2_grpc.add_MensajeriaServicer_to_server(Mensajeria(), server)

    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC escuchando en :50051 …")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()
