from concurrent import futures
import mensaje_pb2
import mensaje_pb2_grpc

class Autenticador(mensaje_pb2_grpc.AutenticadorServicer):

    def Autenticar(self, request, context):
        msj = "Hola" + request.nombre
        