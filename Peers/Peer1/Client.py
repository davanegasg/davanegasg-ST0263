import requests
import sys
import json

# Carga la configuración de los Peers desde un archivo JSON
def load_config():
    with open('peer_config.json') as f:
        return json.load(f)

config = load_config()

def make_request(peer_info, action):
    base_url = f"http://127.0.0.1:{peer_info['flask_port']}/peer/{action}"
    try:
        if action == 'upload':
            response = requests.post(base_url)
        elif action == 'download':
            response = requests.get(base_url)
        else:
            print("Acción no válida.")
            return

        # Asegúrate de que la respuesta es exitosa y tiene contenido antes de intentar decodificar JSON
        if response.status_code == 200 and response.content:
            print(f"Respuesta de {peer_info['peer_id']}: {response.json()}")
        else:
            print(f"Error o respuesta vacía de {peer_info['peer_id']}: Estado {response.status_code}")
    except Exception as e:
        print(f"Excepción al realizar solicitud a {peer_info['peer_id']}: {e}")


if __name__ == "__main__":
    peer_id = sys.argv[1]
    action = sys.argv[2]
    if len(sys.argv) != 3:
        print(f"Uso: python Client.py 5001 {action}")
        sys.exit(1)
    make_request(peer_id, action)
    
