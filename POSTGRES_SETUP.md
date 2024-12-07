# PostgreSQL Setup Guide

This guide explains how to set up PostgreSQL for use with the OpenWebUI Prometheus Exporter.

## Prerequisites

- PostgreSQL installed and running
- Administrative access to PostgreSQL

## Setup Steps

### 1. Create Database User

Create a dedicated user for the OpenWebUI exporter:

```sql
CREATE USER openwebui_exporter WITH PASSWORD 'your_secure_password';
```

### 2. Grant Permissions

The exporter needs READ-ONLY access to the OpenWebUI database tables. Grant the necessary permissions:

```sql
-- Connect to the OpenWebUI database
\c openwebui

-- Grant USAGE on schema
GRANT USAGE ON SCHEMA public TO openwebui_exporter;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO openwebui_exporter;

-- Grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO openwebui_exporter;
```

### 3. Configure Connection Settings

Set the following environment variables for the exporter to connect to your database:

```bash
export OPENWEBUI_DB_NAME=openwebui
export OPENWEBUI_DB_USER=openwebui_exporter
export OPENWEBUI_DB_PASSWORD=your_secure_password
export OPENWEBUI_DB_HOST=localhost
export OPENWEBUI_DB_PORT=5432
```

### 4. Connection Pool Configuration

Configure the database connection pool size based on your needs:

```bash
export DB_MIN_CONNECTIONS=5
export DB_MAX_CONNECTIONS=20
```

#### Connection Pool Guidelines

- **Minimum Connections** (`DB_MIN_CONNECTIONS`):
  - Default: 5
  - Recommended range: 3-10
  - Keep this low enough to not waste resources but high enough to handle basic load

- **Maximum Connections** (`DB_MAX_CONNECTIONS`):
  - Default: 20
  - Recommended range: 10-50
  - Consider your PostgreSQL `max_connections` setting
  - Formula: `max_connections = number_of_exporters * DB_MAX_CONNECTIONS + buffer`

### 5. Verify Connection

Test the database connection using psql:

```bash
psql -h $OPENWEBUI_DB_HOST -p $OPENWEBUI_DB_PORT -U $OPENWEBUI_DB_USER -d $OPENWEBUI_DB_NAME
```

## Performance Considerations

### Query Optimization

The exporter uses time windows to limit query ranges:

```bash
# Configure time windows for queries
export METRICS_REQUEST_WINDOW=24h  # Limit activity queries to last 24 hours
export METRICS_ERROR_WINDOW=1h     # Limit error queries to last hour
```

### Index Recommendations

Create the following indexes to optimize query performance:

```sql
-- User activity queries
CREATE INDEX IF NOT EXISTS idx_user_last_active ON public.user(last_active_at);

-- Chat queries
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON public.chat(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_updated_at ON public.chat(updated_at);

-- Document queries
CREATE INDEX IF NOT EXISTS idx_document_timestamp ON public.document(timestamp);
```

### Monitoring Database Impact

Monitor these PostgreSQL metrics to ensure the exporter isn't overloading your database:

- `pg_stat_activity`: Check for long-running queries
- `pg_stat_statements`: Monitor query performance
- Connection count: `SELECT count(*) FROM pg_stat_activity`

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: could not connect to server: Connection refused
   ```
   - Check if PostgreSQL is running
   - Verify host and port settings
   - Check pg_hba.conf for proper access configuration

2. **Permission Denied**
   ```
   Error: permission denied for table X
   ```
   - Verify GRANT statements were executed
   - Check user permissions: `\du openwebui_exporter`

3. **Too Many Connections**
   ```
   Error: too many connections for role "openwebui_exporter"
   ```
   - Reduce `DB_MAX_CONNECTIONS`
   - Check PostgreSQL `max_connections` setting
   - Monitor active connections

### Diagnostic Queries

Check user permissions:
```sql
SELECT table_name, privilege_type 
FROM information_schema.table_privileges 
WHERE grantee = 'openwebui_exporter';
```

Monitor exporter connections:
```sql
SELECT datname, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE usename = 'openwebui_exporter';
```

## Security Recommendations

1. Use a dedicated database user for the exporter
2. Grant only READ permissions
3. Use SSL for remote connections
4. Regularly rotate the database password
5. Consider network security (firewall rules, pg_hba.conf)

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Connection Pooling Documentation](https://www.postgresql.org/docs/current/client-interfaces.html)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)
