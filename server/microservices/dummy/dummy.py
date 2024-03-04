from flask import Blueprint, jsonify, request

dummy_blueprint = Blueprint('dummy', __name__)

active_peers = set()

@dummy_blueprint.route('/upload', methods=['POST'])
def upload_dummy():
    # Simula la carga de un archivo
    return jsonify({"message": "Upload realizado exitosamente"}), 200

@dummy_blueprint.route('/download', methods=['GET'])
def download_dummy():
    # Simula la descarga de un archivo
    return jsonify({"message": "Download realizado exitosamente"}), 200

@dummy_blueprint.route('/peers', methods=['GET', 'POST'])
def peers():
    global active_peers
    if request.method == 'POST':
        # Añadir el peer que hace el anuncio a la lista de peers activos
        new_peer = request.json.get('url')
        if new_peer:
            active_peers.add(new_peer)
            # Devolver la lista de peers activos actualizada como respuesta
            return jsonify({'peers': list(active_peers)})
        else:
            return jsonify({"error": "URL del peer no proporcionada"}), 400
    else:  # GET
        # Devolver la lista de peers activos
        return jsonify({'peers': list(active_peers)})

