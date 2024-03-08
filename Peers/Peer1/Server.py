import json
from flask import Flask, request, jsonify
import pika

# Carga la configuración del Peer desde su archivo de configuración.
def load_config(config_filename):
    with open(config_filename, 'r') as file:
        return json.load(file)

config = load_config('peer_config.json')

app = Flask(__name__)

# Configura la conexión con RabbitMQ.
def send_notification_to_rabbit(notification_message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='notifications')
    channel.basic_publish(exchange='', routing_key='notifications', body=notification_message)
    connection.close()
    print(f"Enviada notificación a RabbitMQ: {notification_message}")

@app.route('/peer/upload', methods=['POST'])
def upload_dummy():
    # Este endpoint simula la recepción de un archivo sin procesarlo realmente.
    send_notification_to_rabbit(f"Upload dummy realizado en {config['ip']}:{config['port']}")
    return jsonify({"message": "Upload dummy exitoso"}), 200

@app.route('/peer/download', methods=['GET'])
def download_dummy():
    # Este endpoint simula el envío de un archivo.
    send_notification_to_rabbit(f"Download dummy realizado en {config['ip']}:{config['port']}")
    return jsonify({"message": "Download dummy exitoso"}), 200

if __name__ == "__main__":
    app.run(host=config['ip'], port=config['port'])