import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(filename='honeypot.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

@app.route('/ping', methods=['GET'])
def ping():
    client_ip = request.remote_addr
    logging.info(f"PING request from {client_ip}")
    return "Pong!"

@app.route('/api/v1/status', methods=['GET'])
def status():
    client_ip = request.remote_addr
    logging.info(f"Status request from {client_ip}")
    return {"status": "alive"}

@app.route('/api/v1/data', methods=['POST'])
def data():
    client_ip = request.remote_addr
    logging.info(f"Data request from {client_ip}")
    return {"message": "Received data"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
