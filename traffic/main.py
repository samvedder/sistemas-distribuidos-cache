import psycopg2
import requests
import numpy as np
import time
import matplotlib.pyplot as plt

# Configuración de conexión a la base de datos
DB_HOST = 'postgresql'
DB_PORT = '5432'
DB_NAME = 'domains'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Base URL de la API
API_BASE_URL = 'http://api:8000/consulta'

def connect_to_db():
    try:
        # Establecer la conexión a la base de datos
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Conexión a la base de datos exitosa")
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def fetch_domain_by_id(cursor, domain_id):
    start_time = time.time()
    try:
        # Ejecutar la consulta para obtener un dominio por ID
        query = "SELECT predeterminado FROM \"3rd_lev_domains\" WHERE id = %s;"
        cursor.execute(query, (domain_id,))
        result = cursor.fetchone()
        
        if result:
            domain_text = result[0]  # Devuelve el texto del dominio
        else:
            domain_text = None
    except Exception as e:
        print(f"Error al ejecutar la consulta con ID {domain_id}: {e}")
        domain_text = None
    end_time = time.time()
    
    print(f"Tiempo de respuesta de la base de datos para ID {domain_id}: {end_time - start_time:.4f} segundos")
    return domain_text

def send_data_to_api(domain_id, domain_text):
    api_url = f"{API_BASE_URL}?domain={domain_text}"
    start_time = time.time()
    
    try:
        response = requests.get(api_url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            response_json = response.json()
            status = response_json.get("status", "UNKNOWN")
            redis_id = response_json.get("redis", -1)
            
            if status == "HIT":
                hit_count[0] += 1
                redis_hits[redis_id] += 1
                hit_times[redis_id].append(response_time)
            elif status == "MISS":
                miss_count[0] += 1
                redis_misses[redis_id] += 1
                miss_times[redis_id].append(response_time)
            else:
                print(f"Estado desconocido recibido: {status}")
            
            print(f"Datos enviados correctamente a la API: {domain_text}")
            print(f"{domain_id}--> Respuesta de la API:", response_json)
        else:
            print(f"Error al enviar datos a la API. Código de estado: {response.status_code}")
            print("Respuesta:", response.text)
        
        print(f"Tiempo de respuesta de la API para el dominio {domain_text}: {response_time:.4f} segundos")
    
    except Exception as e:
        print(f"Error al hacer la solicitud a la API: {e}")

def main(number_of_queries, range_of_queries):
    start_time = time.time()
    
    global hit_count
    global miss_count
    global redis_hits
    global redis_misses
    global hit_times
    global miss_times
    
    hit_count = [0]
    miss_count = [0]
    redis_hits = [0] * 8
    redis_misses = [0] * 8
    hit_times = [[] for _ in range(8)]
    miss_times = [[] for _ in range(8)]
    
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()

    for domain_id in range(1, number_of_queries + 1):
        querie_aleatoria = np.random.randint(1, range_of_queries)

        domain_text = fetch_domain_by_id(cursor, querie_aleatoria)

        if domain_text:
            send_data_to_api(domain_id, domain_text)
        else:
            print(f"Dominio no encontrado para el ID {domain_id}")

    cursor.close()
    connection.close()
    
    end_time = time.time()
    print("Conexión a la base de datos cerrada")
    print(f"Tiempo total de ejecución: {end_time - start_time:.4f} segundos")
    print(f"Cantidad total de HIT: {hit_count[0]}")
    print(f"Cantidad total de MISS: {miss_count[0]}")

    # Mostrar cantidad total de HIT y MISS por cada Redis
    for i in range(8):
        hit_mean = np.mean(hit_times[i]) if hit_times[i] else 0
        hit_std = np.std(hit_times[i]) if hit_times[i] else 0
        miss_mean = np.mean(miss_times[i]) if miss_times[i] else 0
        miss_std = np.std(miss_times[i]) if miss_times[i] else 0

        print(f"Redis {i+1}: HIT={redis_hits[i]}, MISS={redis_misses[i]}")
        print(f"Redis {i+1}: Tiempo medio de HIT={hit_mean:.4f} segundos, Desviación estándar={hit_std:.4f} segundos")
        print(f"Redis {i+1}: Tiempo medio de MISS={miss_mean:.4f} segundos, Desviación estándar={miss_std:.4f} segundos")

    # Crear gráfico (histograma) para visualizar los hits y misses por Redis
    fig, ax = plt.subplots()
    index = np.arange(8)
    bar_width = 0.35

    rects1 = ax.bar(index, redis_hits, bar_width, label='HIT')
    rects2 = ax.bar(index + bar_width, redis_misses, bar_width, label='MISS')

    ax.set_xlabel('Redis ID')
    ax.set_ylabel('Cantidad')
    ax.set_title('Distribución de HIT y MISS por Redis')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(index)
    ax.legend()

    plt.tight_layout()
    plt.savefig('/app/redis_hits_misses.png')
    plt.show()

    # Crear gráfico para visualizar el tiempo medio de respuesta y desviación estándar para HIT
    fig, ax = plt.subplots()
    index = np.arange(8)
    bar_width = 0.35

    hit_means = [np.mean(hit_times[i]) if hit_times[i] else 0 for i in range(8)]
    hit_stds = [np.std(hit_times[i]) if hit_times[i] else 0 for i in range(8)]

    rects1 = ax.bar(index, hit_means, bar_width, yerr=hit_stds, label='HIT', capsize=5)

    ax.set_xlabel('Redis ID')
    ax.set_ylabel('Tiempo de Respuesta (segundos)')
    ax.set_title('Tiempo Medio de Respuesta de HIT por Redis')
    ax.set_xticks(index)
    ax.set_xticklabels(index)
    ax.legend()

    plt.tight_layout()
    plt.savefig('/app/redis_hit_response_times.png')
    plt.show()

    # Crear gráfico para visualizar el tiempo medio de respuesta y desviación estándar para MISS
    fig, ax = plt.subplots()
    index = np.arange(8)
    bar_width = 0.35

    miss_means = [np.mean(miss_times[i]) if miss_times[i] else 0 for i in range(8)]
    miss_stds = [np.std(miss_times[i]) if miss_times[i] else 0 for i in range(8)]

    rects1 = ax.bar(index, miss_means, bar_width, yerr=miss_stds, color= 'orange', label='MISS', capsize=5)

    ax.set_xlabel('Redis ID')
    ax.set_ylabel('Tiempo de Respuesta (segundos)')
    ax.set_title('Tiempo Medio de Respuesta de MISS por Redis')
    ax.set_xticks(index)
    ax.set_xticklabels(index)
    ax.legend()

    plt.tight_layout()
    plt.savefig('/app/redis_miss_response_times.png')
    plt.show()

if __name__ == "__main__":
    while True:
        try:
            number_of_queries = int(input("¿Cuántos paquetes deseas enviar? (Ingresa 0 para salir): "))
            
            if number_of_queries == 0:
                print("Saliendo del programa...")
                break

            range_of_queries = int(input("¿Cuánto deseas limitar la base de datos?: "))
            
            main(number_of_queries, range_of_queries)
        
        except ValueError:
            print("Por favor, ingresa un número válido.")
