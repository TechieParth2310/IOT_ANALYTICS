# backend/app.py

import os
import sys
from functools import wraps

import mysql.connector
import numpy as np
import pandas as pd
from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, session, flash
)

# Ensure project root is on sys.path before local imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.analytics import (  # noqa: E402
    load_sensor_data, convert_timestamp, sort_by_time, handle_missing,
    add_rolling_features, add_alerts, add_health_score, add_recent_flags,
    add_anomaly_scores, add_device_status
)
from simulator.Simulator import Simulator  # noqa: E402


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Simple in-memory user store for demo purposes
USERS = {
    "admin": {
        "password": os.environ.get("ADMIN_PASSWORD", "admin123"),
        "name": "Admin User"
    }
}
INGEST_API_KEY = os.environ.get("INGEST_API_KEY", "ingest-key")


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            # For API endpoints, return JSON error instead of redirect
            if request.path.startswith('/api/') or request.path.startswith('/sim/'):
                return jsonify({"error": "Unauthorized", "running": False}), 401
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper

# ---------------- DB CONNECTION ----------------


def get_db_connection():
    """
    Create a fresh DB connection per call. The connection object from
    mysql.connector is not thread-safe, so avoid sharing a global instance
    between the Flask threads and the simulator thread.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Parth@2310",
        database="iot_analytics"
    )

# ---------------- SAVE FUNCTION ----------------


def save_to_db(data):
    query = """
    INSERT INTO sensor_data (device_id, temperature, vibration, speed, battery, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        data["device_id"],
        data["temperature"],
        data["vibration"],
        data["speed"],
        data["battery"],
        data["timestamp"]
    )

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        db.commit()
    finally:
        cursor.close()
        db.close()


# ---------------- SIMULATOR INSTANCE ----------------
sim = Simulator(save_fn=save_to_db, interval_seconds=5)


# ---------------- SENSOR API (For manual POST) ----------------
@app.route('/api/sensor', methods=['POST'])
def receive_sensor():
    api_key = request.headers.get("X-API-KEY")
    if "user" not in session and api_key != INGEST_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    print("Received Manual API:", data)
    save_to_db(data)
    return jsonify({"status": "success"})


# ---------------- ANALYTICS PIPELINE ----------------


@app.route('/api/analytics')
@login_required
def api_analytics():
    df = load_sensor_data()
    df = convert_timestamp(df)
    df = sort_by_time(df)
    df = handle_missing(df)
    df = add_rolling_features(df)
    df = add_alerts(df)
    df = add_health_score(df)
    df = add_recent_flags(df)
    df = add_anomaly_scores(df)
    df = add_device_status(df)

    df['timestamp'] = df['timestamp'].astype(str)
    df = df.replace({np.nan: None})
    
    # Ensure boolean columns are properly converted (pandas bool -> Python bool)
    bool_cols = ['overheat', 'high_vibration', 'low_battery', 'battery_drop', 'recent', 'recent_alert', 'anomaly', 'offline']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    return jsonify(df.to_dict(orient="records"))


# ---------------- SIMULATOR CONTROL API ----------------
@app.route('/sim/start', methods=['POST'])
@login_required
def start_sim():
    try:
        print(f"[API] /sim/start called by user: {session.get('user', {}).get('username', 'unknown')}")
        sim.start()
        status = sim.status()
        print(f"[API] Simulator started. Status: {status}")
        return jsonify(status)
    except Exception as exc:
        app.logger.exception("Failed to start simulator thread")
        print(f"[API] Error starting simulator: {exc}")
        return jsonify({"running": False, "error": str(exc)}), 500


@app.route('/sim/stop', methods=['POST'])
@login_required
def stop_sim():
    try:
        print(f"[API] /sim/stop called by user: {session.get('user', {}).get('username', 'unknown')}")
        sim.stop()
        status = sim.status()
        print(f"[API] Simulator stopped. Status: {status}")
        return jsonify(status)
    except Exception as exc:
        app.logger.exception("Failed to stop simulator thread")
        print(f"[API] Error stopping simulator: {exc}")
        return jsonify({"running": sim.is_running(), "error": str(exc)}), 500


@app.route('/sim/status')
@login_required
def status_sim():
    status = sim.status()
    return jsonify(status)


# ---------------- FRONTEND ----------------
@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = USERS.get(username)
        if user and user["password"] == password:
            session['user'] = {"username": username, "name": user["name"]}
            next_page = request.args.get("next") or url_for('dashboard')
            return redirect(next_page)
        flash("Invalid username or password", "danger")
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", active_page="dashboard", user=session.get("user"))


@app.route('/devices')
@login_required
def devices():
    return render_template("devices.html", active_page="devices", user=session.get("user"))


@app.route('/alerts')
@login_required
def alerts():
    return render_template("alerts.html", active_page="alerts", user=session.get("user"))


@app.route('/trends')
@login_required
def trends():
    return render_template("trends.html", active_page="trends", user=session.get("user"))


@app.route('/streaming')
@login_required
def streaming():
    return render_template("streaming.html", active_page="streaming", user=session.get("user"))


if __name__ == '__main__':
    app.run(debug=True)
