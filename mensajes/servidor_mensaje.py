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
    
class Mensajeria(mensaje_pb2_grpc.MensajeriaServicer):

    #rpc ObtenerBandejaEntrada(UserRequest) returns (BandejaReply){};
    def ObtenerBandejaEntrada(self, request, context):
        return super().ObtenerBandejaEntrada(request, context)
    
    #rpc ObtenerBandejaSalida(UserRequest) returns (BandejaReply){};
    def ObtenerBandejaSalida(self, request, context):
        return super().ObtenerBandejaSalida(request, context)
    
    #rpc EnviarCorreo(CorreoNuevo) returns (EnviarCorreoReply){};
    def EnviarCorreo(self, request, context):
        return super().EnviarCorreo(request, context)
    
    #rpc EliminarCorreo(EliminarRequest) returns (OperacionReply){};
    def EliminarCorreo(self, request, context):
        return super().EliminarCorreo(request, context)
    
    #rpc Leido(LeidoRequest) returns (OperacionReply){};
    def Leido(self, request, context):
        return super().Leido(request, context)
    