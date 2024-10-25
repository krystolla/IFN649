import paho.mqtt.client as mqtt
from flask import Flask, jsonify
from datetime import datetime
import threading

app = Flask(__name__)
bpm_data = []

# MQTT Configuration
mqtt_broker = "13.211.13.221"
mqtt_port = 1883
mqtt_topic = "patient/heartbeat"
MAX_SIZE = 200

lock = threading.Lock()  # Lock for thread safety

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    print("Connection returned result: " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    bpm = float(message.payload.decode('utf-8'))

    if len(bpm_data) >= MAX_SIZE:
        bpm_data.pop(0)

    bpm_data.append(bpm)
    
    print(f"Received BPM data: {bpm}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker, attempting to reconnect...")
    client.reconnect()

# Create an MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
try:
    client.connect(mqtt_broker, mqtt_port, 60)
    print(f"Connected to MQTT broker at {mqtt_broker}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

@app.route('/bpm', methods=['GET'])
def get_bpm():
    # Create a list of dictionaries with timestamp and BPM
    with lock:  # Ensure thread-safe access to bpm_data
        recent_readings = [
            {"timestamp": datetime.now().isoformat(), "bpm": bpm} for bpm in bpm_data[-10:]  # ì˜¨ë„ ëŒ€ì‹  BPM ë°ì´í„°
        ]
    return jsonify(recent_readings)

if __name__ == '__main__':
    client.loop_start()  # Start MQTT loop in a separate thread
    app.run(host='0.0.0.0', port=5000)  # Run Flask app