# IoT Device Analytics Dashboard

A comprehensive real-time IoT analytics platform built with Flask, providing monitoring, health scoring, anomaly detection, and intelligent alerts for IoT sensor devices.

## 🌟 Features

### Real-Time Monitoring

- **Live Dashboard**: Real-time visualization of device metrics and health scores
- **Device Status**: Monitor all connected devices with their current status (online/offline)
- **Metric Tracking**: Track temperature, vibration, speed, battery levels, and more

### Analytics & Intelligence

- **Health Scoring**: Automated health score calculation based on device parameters
- **Anomaly Detection**: Z-score based anomaly detection using rolling window analysis
- **Alert System**: Intelligent alerts for:
  - Overheating (temperature > 75°C)
  - High vibration (> 1.5 g-force)
  - Low battery (< 30%)
  - Battery drops (> 10% drop)
  - Anomaly detection (statistical outliers)

### Data Visualization

- **Interactive Charts**: Plotly-powered charts for:
  - Temperature trends with rolling averages
  - Vibration analysis
  - Battery & health correlation
  - Anomaly score visualization
- **Historical Trends**: View data trends over time
- **Real-time Updates**: Dashboard auto-refreshes every 3 seconds

### Simulator Control

- **Built-in Simulator**: Control an IoT sensor simulator from the web interface
- **Start/Stop/Restart**: Easy controls to manage data generation
- **External API**: Support for external devices to push sensor data

### User Interface

- **Modern Dark Theme**: Beautiful, professional dark UI with glassmorphism effects
- **Responsive Design**: Works on desktop and tablet devices
- **Multi-page Dashboard**:
  - Live Dashboard
  - Devices overview
  - Alerts management
  - Trends analysis
  - Streaming controls

## 🏗️ Architecture

### Technology Stack

**Backend:**

- Flask 3.1.2 - Web framework
- MySQL - Database for sensor data storage
- Pandas - Data processing and analytics
- NumPy - Numerical computations

**Frontend:**

- Bootstrap 5.3.3 - UI framework
- Plotly.js - Interactive charts
- Custom CSS - Dark theme with modern styling
- Vanilla JavaScript - Real-time updates

**Simulator:**

- Python threading - Background data generation
- Random data generation - Synthetic sensor data

### Project Structure

```
IOT_Analytics/
├── backend/
│   ├── app.py              # Flask application and routes
│   ├── analytics.py        # Analytics pipeline (health scores, anomaly detection)
│   ├── static/
│   │   └── css/
│   │       └── main.css    # Main stylesheet
│   └── templates/
│       ├── dashboard.html  # Main dashboard page
│       ├── devices.html    # Devices overview page
│       ├── alerts.html     # Alerts page
│       ├── trends.html     # Trends visualization
│       ├── streaming.html  # Simulator control page
│       └── login.html      # Login page
├── simulator/
│   ├── Simulator.py        # Simulator class with thread management
│   └── sensor_simulator.py # Sensor data generation
├── database/
│   └── sensor_data.csv     # Sample data (optional)
└── README.md
```

## 📊 Analytics Pipeline

The system processes sensor data through a comprehensive analytics pipeline:

1. **Data Loading**: Load sensor data from MySQL database
2. **Timestamp Conversion**: Convert timestamps to datetime objects
3. **Time Sorting**: Sort data chronologically
4. **Missing Data Handling**: Forward-fill and backward-fill missing values
5. **Rolling Features**: Calculate rolling averages (5-point window)
6. **Alert Detection**: Flag anomalies (overheat, high vibration, low battery, battery drops)
7. **Health Scoring**: Calculate device health (0-100% based on alert severity)
8. **Recent Flags**: Mark recent data (last 5 minutes)
9. **Anomaly Scores**: Z-score based anomaly detection (2.0 threshold)
10. **Device Status**: Detect offline devices (no data for 15+ seconds)

### Health Score Calculation

Health scores are calculated based on alert severity:

- Base score: 100%
- Overheating: -30%
- High vibration: -20%
- Low battery: -20%
- Battery drop: -10%

### Anomaly Detection

Uses rolling z-score analysis:

- Window size: 20 data points
- Threshold: 2.0 standard deviations
- Monitors: Temperature, Vibration, Speed, Battery
- Flags anomalies when any signal exceeds threshold

## 👤 Author

Developed for IoT Analytics and Monitoring By Parth Kothawade


