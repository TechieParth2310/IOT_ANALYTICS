# backend/simulator.py

import threading
import time
import random
from datetime import datetime

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


class Simulator:
    def __init__(self, save_fn, interval_seconds: float = 1.0):
        self.save_fn = save_fn
        self.interval = interval_seconds

        self._thread = None
        self._stop_event = threading.Event()
        self.last_error = None

    def _run_loop(self):
        try:
            while not self._stop_event.is_set():
                data = generate_sensor_data()
                print("[SIMULATOR] Sending:", data)
                try:
                    self.save_fn(data)
                except Exception as e:
                    # Keep the loop alive but capture the last error for diagnostics
                    self.last_error = str(e)
                    print("[SIMULATOR] Error:", e)

                time.sleep(self.interval)

            print("[SIMULATOR] STOPPED")
        except Exception as e:
            # Surface any unexpected crash so the UI can show it
            self.last_error = str(e)
            print("[SIMULATOR] CRASHED:", e)
        finally:
            # When the loop exits, drop the thread reference so status is accurate
            self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self.last_error = None
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[SIMULATOR] STARTED")

    def stop(self):
        if self._thread:
            thread_ref = self._thread
            self._stop_event.set()
            # Wait briefly for the thread to exit so status reflects reality
            thread_ref.join(timeout=self.interval * 2)
            if not thread_ref.is_alive():
                self._thread = None

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def status(self):
        return {
            "running": self.is_running(),
            "error": self.last_error
        }
