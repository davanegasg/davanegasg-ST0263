import requests
import json

def load_config():
    """Carga la configuración del cliente desde config.json."""
    with open('client/config.json') as config_file:
        return json.load(config_file)

def announce_to_peers(own_url, known_peers):
    """Anuncia este cliente a cada peer conocido."""
    active_peers = set()
    for peer in known_peers:
        try:
            response = requests.post(f"{peer}/dummy/peers", json={"url": own_url})
            if response.status_code == 200:
                # Agrega el peer actual a la lista de peers activos y actualiza con cualquier peer que este conozca
                active_peers.add(peer)
                active_peers.update(response.json()['peers'])
                print(f"Anunciado a {peer} con éxito. Peers conocidos: {response.json()['peers']}")
        except requests.exceptions.RequestException as e:
            print(f"Error al anunciar a {peer}: {e}")
    return list(active_peers)


def choose_peer(active_peers):
    """Permite al usuario elegir un peer de la lista de peers activos."""
    print("\nPeers activos descubiertos:")
    for i, peer in enumerate(active_peers, start=1):
        print(f"{i}. {peer}")
    choice = int(input("Elige el número del peer para interactuar: ")) - 1
    return active_peers[choice]

def choose_dummy_service(peer_url):
    """Permite al usuario elegir qué servicio DUMMY ejecutar en el peer seleccionado."""
    services = ['upload', 'download']
    print("\nServicios DUMMY disponibles:")
    for i, service in enumerate(services, start=1):
        print(f"{i}. {service}")
    choice = int(input("Elige el servicio DUMMY para ejecutar: ")) - 1
    
    if services[choice] == 'upload':
        response = requests.post(f"{peer_url}/dummy/upload", json={"file": "fakefile.txt"})
    elif services[choice] == 'download':
        response = requests.get(f"{peer_url}/dummy/download")
    
    print("Respuesta del servicio DUMMY:", response.json())

def main():
    config = load_config()
    own_url = config['own_url']  # La URL propia debe estar especificada en config.json
    known_peers = config['known_peers']
    
    # Anunciarse a sí mismo a los peers conocidos y obtener una lista de peers activos
    active_peers = announce_to_peers(own_url, known_peers)
    print("Peers activos descubiertos:", active_peers)
    
    # Si hay peers activos, permite al usuario elegir uno y ejecutar un servicio DUMMY
    if active_peers:
        selected_peer = choose_peer(active_peers)
        choose_dummy_service(selected_peer)
    else:
        print("No se descubrieron peers activos. Asegúrate de que los servidores estén en ejecución.")

if __name__ == "__main__":
    main()
