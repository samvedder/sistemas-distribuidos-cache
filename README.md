# DNS Cache Distributed System

## Introducción

Este proyecto es parte de la **Tarea 1** del curso de **Sistemas Distribuidos**. El objetivo es implementar un sistema de caché para solicitudes DNS que funcione utilizando **Redis** para almacenar en caché las respuestas DNS y **gRPC** para gestionar las solicitudes que no se encuentran en la caché. Redis es un sistema de almacenamiento en memoria de alto rendimiento utilizado comúnmente como base de datos, caché y broker de mensajes.

### ¿Por qué Redis?

Redis es ideal para este tipo de tareas porque permite almacenar datos clave-valor en memoria con tiempos de acceso muy bajos. En este proyecto, Redis se utiliza para almacenar resultados de solicitudes DNS, lo que permite que las respuestas se entreguen rápidamente si están en caché (HIT). Si una solicitud no está en caché (MISS), se resuelve a través de gRPC y el resultado se almacena en Redis para futuras consultas.

## Estructura del Proyecto

```bash
DOCKER
 |-docker-compose.api.yml
 |-docker-compose.network.yml
 |-db-init
 | |-init.sql
 |-docker-compose.redis.yml
 |-docker-compose.grpc-server.yml
 |-grpc-server
 | |-proto
 | | |-service.proto
 | |-requirements.txt
 | |-Dockerfile
 | |-main.py
 |-api
 | |-proto
 | | |-service.proto
 | |-requirements.txt
 | |-Dockerfile
 | |-main.py
 |-redis.conf
 |-docker-compose.traffic.yml
 |-docker-compose.postgres.yml
 |-traffic
 | |-requirements.txt
 | |-Dockerfile
 | |-main.py
 |-docker-compose.grpc-client.yml
```
# Requisitos

Antes de comenzar, asegúrate de tener instalados los siguientes programas:

    Docker y Docker Compose.
    Python 3.x.

Para instalarlos:
  [Docker](https://docs.docker.com/engine/install/ubuntu/)
  [Docker Compose](https://docs.docker.com/compose/install/linux/)
  [Python](https://docs.python-guide.org/starting/install3/linux/)

## Librerías Python necesarias

Las librerías necesarias están detalladas en los archivos requirements.txt de cada servicio (para esto es necesario instalar los requirements de cada directorio del proyecto). Algunas de las principales son:

    fastapi
    redis
    grpcio
    psycopg2-binary
    numpy
    matplotlib

Instala las dependencias para cada servicio ejecutando:

```bash
pip install -r requirements.txt
```

# Configuración del Proyecto

## 1. Clonar el repositorio

Primero, clona el repositorio en tu máquina local:

```bash
git clone https://github.com/samvedder/sistemas-distribuidos-cache.git
cd sistemas-distribuidos-cache
```
## 2. Descargar los datos para poder simular el trafico

Se debe de descargar de este [link](https://www.kaggle.com/datasets/domainsindex/secondlevel-domains-listzone-file) el archivo comprimido '3rd_lev_domains.csv'
el cual se debe dejar dentro de la carpeta ../db.init/ para poder levantar el proyecto, **si no esta este archivo y se levantan los contenedores, ocurrira un error.**

## 3. Levantar los contenedores con Docker Compose

El proyecto utiliza Docker Compose para orquestar varios servicios, incluidos Redis, gRPC, PostgreSQL y la API de FastAPI. Puedes levantar todos los servicios necesarios ejecutando los siguientes comandos:
```bash
sudo docker-compose -f docker-compose.network.yml -f docker-compose.postgres.yml -f docker-compose.redis.yml -f docker-compose.api.yml -f docker-compose.traffic.yml -f docker-compose.grpc-server.yml up --build
```

## 4. Verificar la API

Una vez que todos los servicios estén en funcionamiento, puedes interactuar con la API a través de las rutas proporcionadas. Por ejemplo, para agregar un dominio al caché, puedes hacer una solicitud POST:
```bash
curl -X POST "http://localhost:8000/text" -H "Content-Type: application/json" -d '{"text":"www.example.com"}'
```
## 5. Generador de Tráfico y Análisis

El generador de tráfico (traffic/main.py) puede simular consultas a la API. Este genera estadísticas sobre el rendimiento del sistema, incluyendo la tasa de HIT y MISS en Redis, además de los tiempos de respuesta.

Para ejecutar el generador de tráfico, abre un terminal dentro del contenedor:
```
sudo docker exec -it traffic bash
```
Luego dentro del contenedor ejecuta:
```
python3 main.py
```
Te pedira la cantidad de paquetes a enviar y lo que debes de limitar la db para tener una distribucion especifica.

## 5. Imagenes y resultados

El script de traffic/main.py al terminar proporciona datos relevantes para realizar un estudio, es por esto que debes de extraer las imagenes del contenedor <traffic> para poder verlas en tu directorio home (como ejemplo)
```
sudo docker cp <id_contenedor_traffic>:/app/redis_hit_response_times.png /home/
sudo docker cp <id_contenedor_traffic>:/app/redis_miss_response_times.png /home/
sudo docker cp <id_contenedor_traffic>:/app/redis_hits_misses.png /home/
```

# Pruebas y Escenarios

Como se solicita probar el sistema bajo diferentes escenarios. Para ello, puedes se modificar el número de particiones en Redis y observar el impacto en las tasas de HIT y MISS. Hay que seguir una serie de pasos para asegurar los cambios.
## -Primero
Se deben de detener los contenedores:
```
sudo docker-compose -f docker-compose.network.yml -f docker-compose.postgres.yml -f docker-compose.redis.yml -f docker-compose.api.yml -f docker-compose.traffic.yml -f docker-compose.grpc-server.yml down
```
## -Segundo
Eliminar los volumenes de redis para limpiar el cache:
```
sudo docker-compose -f docker-compose.redis.yml down -v
```
## -Tercero
Se puede volver a inciar los contenedores para observar los cambios realizados para los escenarios
```
sudo docker-compose -f docker-compose.network.yml -f docker-compose.postgres.yml -f docker-compose.redis.yml -f docker-compose.api.yml -f docker-compose.traffic.yml -f docker-compose.grpc-server.yml up --build
```

## - IMPORTANTE - Cambios a realizar en los archivos
Para realizar cambios y estudiar los casos de los escenarios, es escencial realizar cambios en los siguientes archivos:
```bash
|-api/main.py
|-docker-compose.api.yml
|-docker-compose.traffic.yml
|-docker-compose.redis.yml
```
### En api/main.py 
los cambios que se deben de hacer son para la cantidad de redis necesaria y si es con hash o por rango, para tener ejemplo el de 4 redis en hash y rango es de la siguiente manera:

api/main.py para 4 redis con hash 
```python
class TextModel(BaseModel):
    text: str

# Inicialización de clientes Redis (4 instancias)
redis_clients = [
    redis.Redis(host='redis1', port=6379, decode_responses=True),
    redis.Redis(host='redis2', port=6379, decode_responses=True),
    redis.Redis(host='redis3', port=6379, decode_responses=True),
    redis.Redis(host='redis4', port=6379, decode_responses=True)
]

def get_redis_client(key: str):
    index = hash(key) % len(redis_clients)  # Calcular el índice de Redis basado en el hash de la clave
    return redis_clients[index]

def add_text_to_redis(key: str, value: str):
    client = get_redis_client(key)
    client.set(key, value)

def get_text_from_redis(key: str):
    client = get_redis_client(key)
    return client.get(key)

```
api/main.py para 4 redis con rango
```python

class TextModel(BaseModel):
    text: str

# Inicialización de clientes Redis (4 instancias)
redis_clients = [
    redis.Redis(host='redis1', port=6379, decode_responses=True),
    redis.Redis(host='redis2', port=6379, decode_responses=True),
    redis.Redis(host='redis3', port=6379, decode_responses=True),
    redis.Redis(host='redis4', port=6379, decode_responses=True)
]

# Particionamiento por rango basado en el primer carácter de la clave
def get_redis_client(key: str):
    first_char = key[0].lower()  # Tomar el primer carácter de la clave y hacerlo minúscula

    # Asignar las instancias Redis según el rango de letras
    if 'a' <= first_char <= 'g':
        return redis_clients[0]  # Redis 1
    elif 'h' <= first_char <= 'm':
        return redis_clients[1]  # Redis 2
    elif 'n' <= first_char <= 'r':
        return redis_clients[2]  # Redis 3
    else:
        return redis_clients[3]  # Redis 4

```

Y en los otros 3 archivos solo se deben de comentar la cantidad de redis con los que se quieren trabajar.
También se implementan políticas de remoción para gestionar el uso de memoria en Redis.

Escenarios

    1-Única partición: Ejecuta Redis sin particionamiento.
    2-Particionado por hash: Utilizar 2, 4, y 8 particiones.
    3-Particionado por rango: Utilizar 2, 4 y 8 particiones.

# Conclusión

Este sistema de caché distribuido permite mejorar el rendimiento de las consultas DNS mediante el uso de Redis para almacenar en caché las respuestas más frecuentes y gRPC para la comunicación con un servidor externo cuando las respuestas no están en caché. La arquitectura modular facilita su despliegue y análisis en distintos entornos.

# Video 

[Demostracion](https://www.youtube.com/watch?v=BMgl2t5ovKs)
