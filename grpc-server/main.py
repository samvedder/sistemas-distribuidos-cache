import grpc
from concurrent import futures
import time
import socket  # Para la resolución DNS

import service_pb2_grpc
import service_pb2

# Implementación del servicio
class MyServiceServicer(service_pb2_grpc.MyServiceServicer):
    def Ping(self, request, context):
        domain = request.message
        try:
            ip_address = socket.gethostbyname(domain)
        except socket.gaierror:
            ip_address = "0.0.0.0"
        
        response = service_pb2.PingResponse()
        response.response = ip_address
        return response

# Configuración del servidor gRPC
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MyServiceServicer_to_server(MyServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC corriendo en el puerto 50051...")
    try:
        while True:
            time.sleep(86400)  # Mantiene el servidor vivo
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()