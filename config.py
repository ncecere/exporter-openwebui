import os
from utils.time_window import parse_time_window, time_window_to_seconds

# Metrics Server Configuration
METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))

# Time Windows for Metrics
# These windows limit the time range for SQL queries to prevent database overload
METRICS_REQUEST_WINDOW = parse_time_window(os.getenv('METRICS_REQUEST_WINDOW', '24h'))
METRICS_ERROR_WINDOW = parse_time_window(os.getenv('METRICS_ERROR_WINDOW', '1h'))

# Database Configuration
DB_NAME = os.getenv('OPENWEBUI_DB_NAME', 'openwebui')
DB_USER = os.getenv('OPENWEBUI_DB_USER', 'postgres')
DB_PASSWORD = os.getenv('OPENWEBUI_DB_PASSWORD', '')
DB_HOST = os.getenv('OPENWEBUI_DB_HOST', 'localhost')
DB_PORT = int(os.getenv('OPENWEBUI_DB_PORT', '5432'))
DB_MIN_CONNECTIONS = int(os.getenv('DB_MIN_CONNECTIONS', '5'))
DB_MAX_CONNECTIONS = int(os.getenv('DB_MAX_CONNECTIONS', '20'))

# Convert time windows to seconds for database queries
REQUEST_WINDOW_SECONDS = time_window_to_seconds(METRICS_REQUEST_WINDOW)
ERROR_WINDOW_SECONDS = time_window_to_seconds(METRICS_ERROR_WINDOW)

# Update interval can use time window format
try:
    update_interval = parse_time_window(os.getenv('METRICS_UPDATE_INTERVAL', '15m'))
    METRICS_UPDATE_INTERVAL = time_window_to_seconds(update_interval)
except ValueError:
    # If parsing fails, assume the value is in seconds
    METRICS_UPDATE_INTERVAL = int(os.getenv('METRICS_UPDATE_INTERVAL', '15'))
