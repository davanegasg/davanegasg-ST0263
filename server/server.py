import argparse
import json
import requests
import threading
import time
from flask import Flask, jsonify
from microservices.dummy.dummy import dummy_blueprint

# Dirección del archivo compartido que contiene la lista de peers conocidos
CONFIG_FILE_PATH = "server/config.json"

#pylance: report
discovery_thread_active = True

app = Flask(__name__)

def load_config():
    """Carga la configuración desde el archivo compartido."""
    with open(CONFIG_FILE_PATH) as config_file:
        return json.load(config_file)

def save_config(config):
    """Guarda la configuración en el archivo compartido."""
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def announce_to_known_peers(own_url, known_peers):
    """Anuncia el nuevo peer a los peers conocidos."""
    for peer in known_peers:
        if peer != own_url:        
            try:
                requests.post(f"{peer}/dummy/peers", json={"url": own_url})
            except requests.exceptions.RequestException as e:
                print(f"No se pudo anunciar a {peer}: {e}")

def discover_peers(server_url, known_peers):
    """Descubre nuevos peers en la red y actualiza la lista de peers conocidos."""
    new_peers = []
    for peer in known_peers:
        if peer != server_url:  # Evita hacer solicitudes a sí mismo
            try:
                response = requests.get(f"{peer}/dummy/peers")
                if response.status_code == 200:
                    new_peers.extend(response.json()['peers'])
            except requests.exceptions.RequestException as e:
                print(f"No se pudo descubrir peers desde {peer}: {e}")
    return list(set(new_peers))

def run_discovery_thread(server_url, known_peers):
    """Hilo para realizar el descubrimiento de peers en segundo plano."""
    while True:
        time.sleep(10)  # Realiza el descubrimiento cada 10 segundos
        new_peers = discover_peers(server_url, known_peers)
        known_peers.extend(new_peers)  # Añade los nuevos peers a la lista de peers conocidos
        known_peers = list(set(known_peers))  # Elimina duplicados
        save_config({"known_peers": known_peers})  # Guarda la lista actualizada de peers conocidos

def get_args():
    """Obtiene argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, help="Puerto en el que el servidor debe escuchar", required=True)
    args = parser.parse_args()
    return args



def run_discovery_thread(server_url, known_peers):
    """Hilo para realizar el descubrimiento de peers en segundo plano."""
    global discovery_thread_active
    while discovery_thread_active:
        time.sleep(10)  # Realiza el descubrimiento cada 10 segundos
        new_peers = discover_peers(server_url, known_peers)
        known_peers.extend(new_peers)  # Añade los nuevos peers a la lista de peers conocidos
        known_peers = list(set(known_peers))  # Elimina duplicados
        save_config({"known_peers": known_peers})  # Guarda la lista actualizada de peers conocidos
    print("Hilo de descubrimiento de peers detenido.")


def main():
    global discovery_thread_active
    args = get_args()
    config = load_config()
    server_url = f"http://localhost:{args.port}"
    known_peers = config['known_peers']
    
    # Si la lista de peers conocidos está vacía, guarda la dirección del propio servidor
    if not known_peers:
        known_peers.append(server_url)
        save_config({"known_peers": known_peers})
    elif server_url not in known_peers:  # Agrega el propio URL si no está en la lista
        known_peers.append(server_url)
        save_config({"known_peers": known_peers})
    
    # Inicia un hilo para realizar el descubrimiento de peers en segundo plano
    discovery_thread = threading.Thread(target=run_discovery_thread, args=(server_url, known_peers))
    discovery_thread.daemon = True
    discovery_thread.start()

    
    
    # Anuncia este peer a los peers conocidos
    announce_to_known_peers(server_url, known_peers)

    # Registrar el blueprint en la aplicación Flask
    app.register_blueprint(dummy_blueprint, url_prefix='/dummy')

    # Detiene el hilo de descubrimiento cuando se sale del bucle principal
    discovery_thread_active = False
    # Inicia el servidor Flask
    app.run(host="0.0.0.0", port=args.port)
    
    
    

if __name__ == '__main__':
    main()
    
