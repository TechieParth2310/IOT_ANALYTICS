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

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- MySQL Server
- pip (Python package manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd IOT_Analytics
   ```

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install Flask==3.1.2
   pip install mysql-connector-python
   pip install pandas
   pip install numpy
   pip install plotly
   ```

4. **Set up MySQL Database**

   ```sql
   CREATE DATABASE iot_analytics;

   USE iot_analytics;

   CREATE TABLE sensor_data (
       id INT AUTO_INCREMENT PRIMARY KEY,
       device_id VARCHAR(10) NOT NULL,
       temperature DECIMAL(5,2),
       vibration DECIMAL(5,2),
       speed DECIMAL(5,2),
       battery INT,
       timestamp DATETIME,
       INDEX idx_device_id (device_id),
       INDEX idx_timestamp (timestamp)
   );
   ```

5. **Configure Database Connection**

   Update the database credentials in `backend/analytics.py` and `backend/app.py`:

   ```python
   mysql.connector.connect(
       host="localhost",
       user="your_username",
       password="your_password",
       database="iot_analytics"
   )
   ```

6. **Set Environment Variables (Optional)**
   ```bash
   export FLASK_SECRET_KEY="your-secret-key"
   export ADMIN_PASSWORD="your-admin-password"
   export INGEST_API_KEY="your-api-key"
   ```

### Running the Application

1. **Start the Flask server**

   ```bash
   cd backend
   python app.py
   ```

   Or using Flask CLI:

   ```bash
   export FLASK_APP=app.py
   flask run
   ```

2. **Access the dashboard**

   - Open your browser and navigate to `http://127.0.0.1:5000`
   - Default login credentials:
     - Username: `admin`
     - Password: `admin123` (or set via `ADMIN_PASSWORD` env var)

3. **Start the Simulator**
   - Navigate to the "Streaming" page
   - Click "Start" to begin generating synthetic sensor data
   - Or run the simulator manually:
     ```bash
     python simulator/sensor_simulator.py
     ```

## 📡 API Endpoints

### Authentication Required Endpoints

All endpoints except `/login` and `/api/sensor` (with API key) require authentication.

### Public Endpoints

- `GET /login` - Login page
- `POST /login` - Authenticate user
- `POST /api/sensor` - Ingest sensor data (requires API key in header: `X-API-KEY`)

### Protected Endpoints

**Pages:**

- `GET /` - Redirects to dashboard
- `GET /dashboard` - Main dashboard page
- `GET /devices` - Devices overview page
- `GET /alerts` - Alerts page
- `GET /trends` - Trends visualization page
- `GET /streaming` - Simulator control page
- `GET /logout` - Logout user

**API:**

- `GET /api/analytics` - Get processed analytics data (JSON)
- `POST /sim/start` - Start the simulator
- `POST /sim/stop` - Stop the simulator
- `GET /sim/status` - Get simulator status

### Example API Usage

**Post sensor data:**

```bash
curl -X POST http://127.0.0.1:5000/api/sensor \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key" \
  -d '{
    "device_id": "R1",
    "temperature": 62.5,
    "vibration": 0.8,
    "speed": 2.5,
    "battery": 88,
    "timestamp": "2025-01-01T12:00:00Z"
  }'
```

**Get analytics data:**

```bash
curl http://127.0.0.1:5000/api/analytics \
  -H "Cookie: session=your-session-cookie"
```

## 🎛️ Simulator

The built-in simulator generates synthetic sensor data for testing and demonstration.

### Features

- **Configurable Interval**: Default 5 seconds between data points
- **Multiple Devices**: Supports 4 devices (R1, R2, R3, R4)
- **Realistic Data**: Random values within realistic ranges:
  - Temperature: 30-90°C
  - Vibration: 0.2-2.0 g-force
  - Speed: 0.5-5.0 m/s
  - Battery: 20-100%

### Control via Web Interface

- Navigate to "Streaming" page
- Use Start/Stop buttons to control the simulator
- Status updates in real-time

### Control via CLI

```bash
python simulator/sensor_simulator.py
```

## 📈 Metrics Explained

### Active Devices

Number of unique devices that have sent data in the dataset.

### Average Temperature

Mean temperature across all devices and data points.

### Alerts (Last 5 min)

Count of alert conditions detected in the most recent 5-minute window.

### Average Health Score

Mean health score across all devices (0-100%).

### Offline Devices

Devices that haven't sent data in the last 15 seconds (3x expected interval).

### Anomaly Rate (5m)

Percentage of recent data points flagged as statistical anomalies.

### Recent Alerts (5m)

Count of alerts triggered in the last 5 minutes.

### Data Freshness

Seconds since the most recent sensor reading.

## 🔒 Security

- **Session-based Authentication**: Flask sessions for user authentication
- **API Key Support**: For external device integration
- **Password Protection**: Configurable admin password
- **CSRF Protection**: Built-in Flask security features

## 🎨 Customization

### Theme Colors

Edit `backend/static/css/main.css` to customize:

- Accent colors (`--accent`, `--accent-2`)
- Background colors (`--bg-main`, `--bg-panel`)
- Text colors (`--text-main`, `--text-secondary`, `--text-muted`)

### Alert Thresholds

Modify thresholds in `backend/analytics.py`:

- Overheat: `temperature > 75` (line 105)
- High vibration: `vibration > 1.5` (line 106)
- Low battery: `battery < 30` (line 107)
- Battery drop: `battery.diff() < -10` (line 108)
- Anomaly threshold: `threshold: float = 2.0` (line 140)

### Data Refresh Rate

Change refresh intervals in templates:

- Dashboard refresh: `setInterval(refreshDashboard, 3000)` (3 seconds)
- Status updates: `setInterval(updateSimStatus, 2000)` (2 seconds)

## 🐛 Troubleshooting

### Database Connection Issues

- Verify MySQL is running: `mysql -u root -p`
- Check database credentials in `backend/analytics.py`
- Ensure database and table exist

### Simulator Not Starting

- Check console for errors
- Verify database connection is working
- Check that port 5000 is not in use

### Charts Not Displaying

- Check browser console for JavaScript errors
- Verify Plotly.js is loaded (CDN)
- Check network tab for failed requests

### Text Not Visible

- Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- Clear browser cache
- Check CSS file is loaded correctly

## 📝 License

This project is available for educational and demonstration purposes.

## 👤 Author

Developed for IoT Analytics and Monitoring

## 🔮 Future Enhancements

- [ ] Real-time WebSocket updates (instead of polling)
- [ ] User management system
- [ ] Data export functionality
- [ ] Email/SMS alert notifications
- [ ] Machine learning-based anomaly detection
- [ ] Device configuration management
- [ ] Historical data archiving
- [ ] Multi-tenant support
- [ ] REST API documentation (Swagger)
- [ ] Docker containerization

---

**Note**: This is a demonstration project. For production use, implement additional security measures, error handling, and scalability improvements.
