import logging
from flask import Flask, request, jsonify
import json

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
    
    # Log request headers
    headers = dict(request.headers)
    headers_str = json.dumps(headers, indent=2)
    
    # Try to parse the request data as JSON
    try:
        request_data = request.get_json()
        if request_data is None:
            raise ValueError("No JSON content")
        request_body = json.dumps(request_data, indent=2)  # Convert dict to JSON string
    except:
        # If it's not JSON, get the raw data
        request_body = request.data.decode('utf-8')

    logging.info(f"Data request from {client_ip}, headers: {headers_str}, body: {request_body}")
    
    return jsonify({"message": "Received data"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)

