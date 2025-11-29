import requests
import random
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000/api/sensor"   # Backend endpoint
API_KEY = "ingest-key"  # Must match INGEST_API_KEY in backend/app.py

DEVICE_IDS = ["R1", "R2", "R3", "R4"]

def generate_sensor_data():
    return {
        "device_id": random.choice(DEVICE_IDS),
        "temperature": round(random.uniform(30, 90), 2),
        "vibration": round(random.uniform(0.2, 2.0), 2),
        "speed": round(random.uniform(0.5, 5.0), 2),
        "battery": random.randint(20, 100),
        "timestamp": datetime.now().isoformat()
    }


while True:
    data = generate_sensor_data()
    print("Sending:", data)

    try:
        response = requests.post(API_URL, json=data, headers={"X-API-KEY": API_KEY})
        print("Server:", response.text)
    except Exception as e:
        print("Error:", e)

    time.sleep(5)  # Send data every 5 seconds
