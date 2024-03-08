import subprocess
import os
import time
import json
import pika
from threading import Thread

def start_server(server_script_path, cwd):
    """
    Inicia el servidor Flask para un Peer específico.
    """
    subprocess.Popen(["python", server_script_path], cwd=cwd)
    print(f"Starting server at {cwd}")

def start_peer_servers():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Peers'))
    peers = ['Peer1', 'Peer2']  # Lista explícita de directorios de Peer

    for peer_dir in peers:
        peer_path = os.path.join(base_dir, peer_dir)
        config_path = os.path.join(peer_path, "peer_config.json")
        print(peer_path)
        if not os.path.exists(config_path):
            print(f"Skipping {peer_dir}, config file not found.")
            continue
        with open(config_path, 'r') as file:
            config = json.load(file)
        
        server_script_path = "Server.py"
        print(f"Starting server for {peer_dir} on port {config['port']}")
        start_server(server_script_path, cwd=peer_path)
    pass

def perform_operations_between_peers():
    peers_operations = [
        {"source": "Peer1", "target": "Peer2", "operation": "upload"},
        {"source": "Peer2", "target": "Peer1", "operation": "download"}
    ]
    for operation in peers_operations:
        source_dir = os.path.join("Peers", operation["source"])
        client_script_path = os.path.join("Client.py")
        target_config_path = os.path.join("Peers", operation["target"], "peer_config.json")
        
        with open(target_config_path, 'r') as file:
            target_config = json.load(file)
        
        # Construye la URL del peer objetivo basado en su configuración
        target_url = f"http://{target_config['ip']}:{target_config['port']}"
        
        # Ejecuta el script del cliente para realizar la operación
        subprocess.run(["python", client_script_path, "--operation", operation["operation"], "--target-url", target_url], cwd=source_dir)
        print(f"{operation['source']} performed {operation['operation']} to {operation['target']}")
    pass

def start_rabbitmq_consumer():
    # Configura la conexión a RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Nombre de la cola de la que queremos consumir
    queue_name = 'notifications'

    # Asegúrate de que la cola existe
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        print(f" [x] Recibido {body.decode()}")

    # Configura el consumidor
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True)

    print(' [*] Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()

def main():
    # Inicia el consumidor de RabbitMQ en un hilo separado sin bloquearlo
    thread = Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()

    # Inicia los servidores de los peers
    start_peer_servers()

    # Espera a que los servidores estén listos antes de continuar
    time.sleep(5)

    # Realiza operaciones de upload y download entre peers
    perform_operations_between_peers()

    # Espera a que el usuario presione Enter para finalizar (o implementa otra lógica de terminación)
    input("Presiona Enter para finalizar...")



if __name__ == "__main__":
    main()