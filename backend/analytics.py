import os
import sys
import mysql.connector
import pandas as pd
import numpy as np


# Ensure project root is on the path so local modules resolve reliably
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


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


def load_sensor_data():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "SELECT device_id, temperature, vibration, speed, battery, timestamp FROM sensor_data ORDER BY timestamp ASC")

    rows = cursor.fetchall()

    # Close cursor and connection properly
    cursor.close()
    db.close()

    df = pd.DataFrame(rows, columns=[
                      "device_id", "temperature", "vibration", "speed", "battery", "timestamp"])

    return df


def convert_timestamp(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def sort_by_time(df):
    df = df.sort_values(by='timestamp')
    df = df.reset_index(drop=True)  # VERY IMPORTANT
    return df


def handle_missing(df):
    # Forward fill missing values
    df = df.ffill()

    # Backward fill missing values (for any starting NaNs)
    df = df.bfill()

    return df


def add_rolling_features(df):
    # Rolling average of temperature over last 5 readings
    df['temp_avg'] = df['temperature'].rolling(window=5).mean()

    # Rolling average of vibration
    df['vibration_avg'] = df['vibration'].rolling(5).mean()

    # Rolling average of speed
    df['speed_avg'] = df['speed'].rolling(5).mean()

    # Rolling average of battery
    df['battery_avg'] = df['battery'].rolling(5).mean()

    return df


def add_overheat_flag(df):
    df['overheat'] = df['temperature'] > 75
    return df


def add_vibration_flag(df):
    df['high_vibration'] = df['vibration'] > 1.5
    return df


def add_low_battery_flag(df):
    df['low_battery'] = df['battery'] < 30
    return df


def add_battery_drop_flag(df):
    df['battery_drop'] = df['battery'].diff() < -10
    return df


def add_alerts(df):
    df['overheat'] = df['temperature'] > 75
    df['high_vibration'] = df['vibration'] > 1.5
    df['low_battery'] = df['battery'] < 30
    df['battery_drop'] = df['battery'].diff() < -10
    return df


def add_health_score(df):
    df['health'] = 100 - (
        df['overheat'] * 30 +
        df['high_vibration'] * 20 +
        df['low_battery'] * 20 +
        df['battery_drop'] * 10
    )
    return df


def add_recent_flags(df, window_minutes: int = 5):
    """
    Mark rows that are within the recent window and whether they contain alerts.
    """
    if df.empty:
        df['recent'] = False
        df['recent_alert'] = False
        return df

    latest_ts = df['timestamp'].max()
    cutoff = latest_ts - pd.Timedelta(minutes=window_minutes)
    df['recent'] = df['timestamp'] >= cutoff
    df['recent_alert'] = df['recent'] & (
        df['overheat'] | df['high_vibration'] | df['low_battery'] | df['battery_drop']
    )
    return df


def add_anomaly_scores(df, window: int = 20, threshold: float = 2.0):
    """
    Adds simple rolling z-score based anomaly detection for key signals.
    Lower threshold (2.0 instead of 3.0) makes it more sensitive to detect anomalies.
    """
    if df.empty:
        df['anomaly_score'] = 0.0
        df['anomaly'] = False
        return df

    for col in ['temperature', 'vibration', 'speed', 'battery']:
        roll_mean = df[col].rolling(window=window, min_periods=5).mean()
        roll_std = df[col].rolling(window=window, min_periods=5).std()
        z_col = f'{col}_z'
        # Calculate z-score, handling division by zero
        df[z_col] = (df[col] - roll_mean) / roll_std.replace({0: np.nan})
        df[z_col] = df[z_col].fillna(0)

    # Calculate anomaly score as mean of absolute z-scores across all signals
    z_cols = [c for c in df.columns if c.endswith('_z')]
    if z_cols:
        df['anomaly_score'] = df[z_cols].abs().mean(axis=1)
    else:
        df['anomaly_score'] = 0.0
    
    # Flag as anomaly if any individual signal exceeds threshold OR mean exceeds threshold
    # This makes it more sensitive to anomalies
    individual_anomalies = pd.Series([False] * len(df), index=df.index)
    for col in ['temperature', 'vibration', 'speed', 'battery']:
        z_col = f'{col}_z'
        if z_col in df.columns:
            individual_anomalies = individual_anomalies | (df[z_col].abs() > threshold)
    
    # Anomaly if mean score exceeds threshold OR any individual signal exceeds threshold
    df['anomaly'] = (df['anomaly_score'] > threshold) | individual_anomalies
    
    return df


def add_device_status(df, expected_interval_sec: int = 5, grace_factor: int = 3):
    """
    Flag devices as offline when they haven't sent data within a grace window.
    """
    if df.empty:
        df['offline'] = False
        return df

    latest_overall = df['timestamp'].max()
    latest_per_device = df.groupby('device_id')['timestamp'].transform('max')
    seconds_since_last = (
        latest_overall - latest_per_device).dt.total_seconds()
    df['seconds_since_last'] = seconds_since_last
    df['offline'] = df['seconds_since_last'] > (
        expected_interval_sec * grace_factor)
    return df
