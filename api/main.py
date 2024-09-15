import grpc
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import service_pb2_grpc
import service_pb2

app = FastAPI()

# Conectarse al servidor gRPC con timeout de 2 segundos
channel = grpc.insecure_channel('grpc-server:50051')
stub = service_pb2_grpc.MyServiceStub(channel)

class TextModel(BaseModel):
    text: str

# Inicialización de clientes Redis
redis_clients = [
    redis.Redis(host='redis1', port=6379, decode_responses=True),
    redis.Redis(host='redis2', port=6379, decode_responses=True),
    redis.Redis(host='redis3', port=6379, decode_responses=True),
    redis.Redis(host='redis4', port=6379, decode_responses=True),
    redis.Redis(host='redis5', port=6379, decode_responses=True),
    redis.Redis(host='redis6', port=6379, decode_responses=True),
    redis.Redis(host='redis7', port=6379, decode_responses=True),
    redis.Redis(host='redis8', port=6379, decode_responses=True),
]

def get_redis_client(key: str):
    index = hash(key) % len(redis_clients)
    return redis_clients[index]

def add_text_to_redis(key: str, value: str):
    client = get_redis_client(key)
    client.set(key, value)

def get_text_from_redis(key: str):
    client = get_redis_client(key)
    return client.get(key)

def fetch_domain_from_grpc(domain: str):
    request = service_pb2.PingRequest(message=domain)
    
    try:
        # Intentar hacer la llamada gRPC con un timeout de 2 segundos
        response = stub.Ping(request, timeout=2)
        return response.response
    except grpc.RpcError as e:
        # Si hay timeout o cualquier error, devolver el valor por defecto
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            return "0.0.0.0"
        else:
            raise HTTPException(status_code=500, detail="Error en la resolución gRPC")

@app.post('/text')
def add_text(text_model: TextModel):
    domain = text_model.text
    result = get_text_from_redis(domain)

    if result:
        return {"status": "HIT", "domain": domain, "ip": result}
    else:
        # Si el dominio no está en Redis, consulta a gRPC
        resolved_ip = fetch_domain_from_grpc(domain)
        add_text_to_redis(domain, resolved_ip)
        return {"status": "MISS", "domain": domain, "ip": resolved_ip}

@app.get('/consulta')
def consulta(domain: str):
    ip = get_text_from_redis(domain)
    if ip:
        return {"status": "HIT", "domain": domain, "ip": ip, "redis": hash(domain) % len(redis_clients)}
    else:
        # El dominio no está en Redis, consulta al cliente gRPC
        ip = fetch_domain_from_grpc(domain)
        # Agregar el dominio con la IP obtenida a Redis
        add_text_to_redis(domain, ip)
        return {"status": "MISS", "domain": domain, "ip": ip, "redis": hash(domain) % len(redis_clients)}
