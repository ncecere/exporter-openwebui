# Environment Variables Reference

This document lists all environment variables supported by the OpenWebUI Prometheus Exporter.

## Metrics Configuration

### METRICS_PORT
- **Description**: Port number where the Prometheus metrics will be exposed
- **Default**: `9090`
- **Example**: `METRICS_PORT=9090`

### METRICS_UPDATE_INTERVAL
- **Description**: How frequently metrics are updated. Supports 'm' (minutes) and 'h' (hours) suffixes
- **Default**: `15m`
- **Example**: `METRICS_UPDATE_INTERVAL=5m`

### METRICS_REQUEST_WINDOW
- **Description**: Time window for request/activity metrics. Limits how far back SQL queries will look for user activity data. Supports 'm' (minutes) and 'h' (hours) suffixes
- **Default**: `24h`
- **Example**: `METRICS_REQUEST_WINDOW=12h`

### METRICS_ERROR_WINDOW
- **Description**: Time window for error metrics. Limits how far back SQL queries will look for error data. Supports 'm' (minutes) and 'h' (hours) suffixes
- **Default**: `1h`
- **Example**: `METRICS_ERROR_WINDOW=30m`

## Database Connection

### OPENWEBUI_DB_NAME
- **Description**: PostgreSQL database name
- **Default**: `openwebui`
- **Example**: `OPENWEBUI_DB_NAME=openwebui_prod`

### OPENWEBUI_DB_USER
- **Description**: PostgreSQL database user
- **Default**: `postgres`
- **Example**: `OPENWEBUI_DB_USER=openwebui_user`

### OPENWEBUI_DB_PASSWORD
- **Description**: PostgreSQL database password
- **Default**: ` ` (empty string)
- **Example**: `OPENWEBUI_DB_PASSWORD=your_secure_password`

### OPENWEBUI_DB_HOST
- **Description**: PostgreSQL database host address
- **Default**: `localhost`
- **Example**: `OPENWEBUI_DB_HOST=db.example.com`

### OPENWEBUI_DB_PORT
- **Description**: PostgreSQL database port
- **Default**: `5432`
- **Example**: `OPENWEBUI_DB_PORT=5432`

## Connection Pool Configuration

### DB_MIN_CONNECTIONS
- **Description**: Minimum number of database connections to maintain in the connection pool
- **Default**: `5`
- **Example**: `DB_MIN_CONNECTIONS=10`

### DB_MAX_CONNECTIONS
- **Description**: Maximum number of database connections allowed in the connection pool
- **Default**: `20`
- **Example**: `DB_MAX_CONNECTIONS=50`

## Example Configuration

Here's a complete example configuration:

```bash
# Metrics Configuration
export METRICS_PORT=9090
export METRICS_UPDATE_INTERVAL=15m
export METRICS_REQUEST_WINDOW=24h
export METRICS_ERROR_WINDOW=1h

# Database Connection
export OPENWEBUI_DB_NAME=openwebui
export OPENWEBUI_DB_USER=openwebui_user
export OPENWEBUI_DB_PASSWORD=your_secure_password
export OPENWEBUI_DB_HOST=localhost
export OPENWEBUI_DB_PORT=5432

# Connection Pool
export DB_MIN_CONNECTIONS=5
export DB_MAX_CONNECTIONS=20
