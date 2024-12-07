# OpenWebUI Prometheus Exporter

A Prometheus exporter for OpenWebUI that provides detailed metrics about users, chats, documents, models, and system status.

## Features

- Comprehensive metrics collection from OpenWebUI's PostgreSQL database
- Connection pooling for efficient database access
- Time-windowed queries to prevent database overload
- Flexible time window specification (hours, minutes)
- Modular collector design for easy maintenance and extensions
- Detailed monitoring of:
  - User activity and authentication
  - Chat conversations and folders
  - Documents and knowledge bases
  - AI models and tools
  - System configuration and health

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/yourusername/exporter-openwebui.git
cd exporter-openwebui
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Required
export OPENWEBUI_DB_PASSWORD=your_password

# Optional - see ENV-VARS.md for all options
export METRICS_PORT=9090
export METRICS_UPDATE_INTERVAL=15m
```

4. Start the exporter:
```bash
python main.py
```

The exporter will start on the configured port (default: 9090). Metrics will be available at:
```
http://localhost:9090/metrics
```

## Configuration

All configuration is done through environment variables. For a complete list of available environment variables, their descriptions, defaults, and examples, see [ENV-VARS.md](ENV-VARS.md).

Key configuration features:
- Time windows for limiting SQL query ranges
- Database connection pooling
- Configurable metric update intervals

## Metrics Overview

### User Metrics
- `openwebui_users_total`: Total number of registered users
- `openwebui_users_active`: Number of active users (within request window)
- `openwebui_users_by_role`: Number of users by role
- `openwebui_auth_active`: Number of active auth entries
- `openwebui_oauth_users`: Number of users using OAuth
- `openwebui_user_last_active_seconds`: Timestamp of last user activity

### Chat Metrics
- `openwebui_chats_total`: Total number of chats
- `openwebui_chats_active`: Number of non-archived chats
- `openwebui_chats_archived`: Number of archived chats
- `openwebui_chats_pinned`: Number of pinned chats
- `openwebui_chats_by_user`: Number of chats per user
- `openwebui_chats_shared`: Number of shared chats
- `openwebui_chat_messages_total`: Total number of chat messages
- `openwebui_chat_age_seconds`: Age distribution of chats
- `openwebui_folders_total`: Total number of chat folders
- `openwebui_chats_in_folders`: Number of chats organized in folders

### Document Metrics
- `openwebui_documents_total`: Total number of documents
- `openwebui_documents_by_collection`: Number of documents by collection
- `openwebui_documents_by_user`: Number of documents per user
- `openwebui_files_total`: Total number of files
- `openwebui_files_by_user`: Number of files per user
- `openwebui_knowledge_bases_total`: Total number of knowledge bases
- `openwebui_knowledge_bases_by_user`: Number of knowledge bases per user
- `openwebui_memories_total`: Total number of memories
- `openwebui_memories_by_user`: Number of memories per user
- `openwebui_document_age_seconds`: Age distribution of documents

### Model Metrics
- `openwebui_models_total`: Total number of models
- `openwebui_models_active`: Number of active models
- `openwebui_models_by_user`: Number of models per user
- `openwebui_models_by_base`: Number of models by base model
- `openwebui_tools_total`: Total number of tools
- `openwebui_tools_by_user`: Number of tools per user
- `openwebui_functions_total`: Total number of functions
- `openwebui_functions_active`: Number of active functions
- `openwebui_functions_global`: Number of global functions
- `openwebui_functions_by_type`: Number of functions by type
- `openwebui_functions_by_user`: Number of functions per user

### System Metrics
- `openwebui_config_version`: Current configuration version
- `openwebui_config_last_update`: Timestamp of last configuration update
- `openwebui_groups_total`: Total number of groups
- `openwebui_users_in_groups`: Number of users in groups
- `openwebui_feedback_total`: Total number of feedback entries
- `openwebui_feedback_by_type`: Number of feedback entries by type

## Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'openwebui'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
```

## Development

The exporter is organized into modular collectors:

- `user_metrics.py`: User and authentication metrics
- `chat_metrics.py`: Chat and conversation metrics
- `document_metrics.py`: Document and file metrics
- `model_metrics.py`: AI model and tool metrics
- `system_metrics.py`: System configuration metrics

Each collector can be extended or modified independently to add new metrics or modify existing ones.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
