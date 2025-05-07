from concurrent import futures
import mensaje_pb2
import mensaje_pb2_grpc
from usuarios import inicializar_bd, registrar_usuarios, autenticar_usuario
import uuid

sesiones = {}

def generar_token():
    return str(uuid.uuid4())

class Autenticador(mensaje_pb2_grpc.AutenticadorServicer):

    def Registrar(self, request, context):
        stat, msj = registrar_usuarios(request.nombre, request.contrasena)
        return mensaje_pb2.RegistroReply(status=stat, mensaje=msj)

    def Autenticar(self, request, context):
        stat = autenticar_usuario(request.nombre, request.contrasena)
        if stat:
            token = generar_token()
            sesiones[token] = request.nombre
            msj = "Hola " + request.nombre
        else:
            token = ""
            msj = "Credenciales incorrectas"
        return mensaje_pb2.AuthenticationReply(mensaje=msj, status=stat, token=token)