# Changelog

All notable changes to the OpenWebUI Prometheus Exporter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.2] - 2025-03-14

### Fixed
- Fixed `openwebui_messages_total` metric to properly count all messages
- Fixed JSON type casting in SQL queries by adding explicit JSONB casts
- Added detailed logging for message counting to help with troubleshooting

## [1.3.1] - 2025-03-14

### Added
- New metric `openwebui_messages_total` to count the total number of messages across all chats

### Changed
- Renamed `openwebui_chat_messages_total` to `openwebui_messages_by_model` and improved implementation to count actual messages by model
- Updated documentation to remove references to metrics that no longer exist

## [1.3.0] - 2025-03-14

### Added
- New metric `openwebui_active_users` to track users active in the last 30 minutes
- New metric `openwebui_prompts_total` to count the total number of prompts
- New metric `openwebui_assistants_total` to count models where base_model_id is NOT NULL

### Changed
- Modified `openwebui_models_total` to only count base models (where base_model_id IS NULL)
- Fixed `openwebui_files_total` metric to properly count all files without labels

### Removed
- Removed the following metrics:
  - openwebui_auth_active
  - openwebui_oauth_users
  - openwebui_folders_total
  - openwebui_chats_in_folders
  - openwebui_documents_by_collection
  - openwebui_documents_by_user
  - openwebui_knowledge_bases_by_user
  - openwebui_memories_total
  - openwebui_feedback_by_type
  - openwebui_functions_by_type
  - openwebui_functions_by_user

## [1.2.1] - 2025-03-06

### Added
- Support for seconds ('s') in time window formats for all time-related configuration
- Updated documentation to reflect new time format options

### Fixed
- Fixed error when using seconds ('s') in METRICS_UPDATE_INTERVAL environment variable

## [1.2.0] - 2024-12-13

### Added
- User email labels to all user-related metrics:
  - openwebui_chats_by_user
  - openwebui_documents_by_user
  - openwebui_files_by_user
  - openwebui_knowledge_bases_by_user
  - openwebui_memories_by_user
  - openwebui_models_by_user
  - openwebui_tools_by_user
  - openwebui_functions_by_user
  - openwebui_users_in_groups
  - openwebui_feedback_by_type
  - openwebui_user_last_active_seconds

### Changed
- Enhanced Dockerfile with multi-stage builds:
  - Added builder stage for dependencies
  - Added development stage with testing tools
  - Improved production stage
- Updated docker-compose.yml:
  - Removed hardcoded secrets
  - Added environment variable substitution
  - Added build target configuration
- Improved database connection handling:
  - Enhanced connection pool management
  - Better cursor lifecycle handling
  - Added debug logging for troubleshooting
- Updated GitHub Actions workflow:
  - Added support for multi-stage builds
  - Enhanced caching strategy
  - Added build arguments support

## [1.1.0] - 2024-12-07

### Changed
- Improved chat metrics to properly extract model names from chat messages
- Enhanced file metrics to show accurate knowledge base relationships
- Updated document metrics collector to properly handle file-to-knowledge-base mappings
- Removed sensitive information from docker-compose.yml

### Removed
- Removed the following metrics:
  - openwebui_table_size_bytes
  - openwebui_table_rows
  - openwebui_last_migration_timestamp
  - openwebui_migrations_total

## [1.0.2] - 2023-12-07

### Added
- Human-readable labels for all metrics:
  - User names alongside user IDs
  - Model names alongside model IDs
  - Function names alongside function types
  - Tool names in tool metrics
  - Folder names in folder metrics
  - Group names and owner information
  - Collection names for documents
  - Knowledge base names

### Changed
- Updated all collectors to include both ID and name-based labels
- Improved metric readability and usability
- Enhanced query joins to fetch related names

## [1.0.1] - 2023-12-06

### Fixed
- Fixed system metrics collector to use proper PostgreSQL queries for table statistics
- Removed dependency on pg_catalog.pg_statio_user_tables.reltuples
- Improved table size and row count collection methods

## [1.0.0] - 2023-12-05

### Added
- Initial release of OpenWebUI Prometheus Exporter
- Comprehensive metric collection for:
  - User activity and authentication
  - Chat conversations and folders
  - Documents and knowledge bases
  - AI models and tools
  - System configuration and health
- Database connection pooling with configurable limits
- Time-windowed queries to prevent database overload
- Flexible time window specification (seconds, minutes, hours, days)
- Docker support with multi-stage builds
- Docker Compose configuration for easy deployment
- Comprehensive documentation:
  - README.md with quick start guide
  - ENV-VARS.md with environment variable reference
  - POSTGRES_SETUP.md with database setup guide

### Features
- User Metrics:
  - Total users, active users, users by role
  - Authentication status and OAuth usage
  - User activity tracking
- Chat Metrics:
  - Total, active, and archived chats
  - Chat organization and sharing statistics
  - Message counts and age distribution
- Document Metrics:
  - Document and file statistics
  - Knowledge base usage
  - Memory tracking
- Model Metrics:
  - Model deployment and usage statistics
  - Tool and function tracking
  - Global function monitoring
- System Metrics:
  - Configuration version tracking
  - Database migration status
  - Table sizes and row counts
  - Group and feedback statistics

### Technical Details
- Database Features:
  - Connection pooling (configurable min/max connections)
  - Read-only access mode
  - Optimized query patterns
- Time Window Support:
  - Configurable windows for request and error metrics
  - Support for hours ('h') and minutes ('m') notation
  - Default windows: 24h for requests, 1h for errors
- Docker Support:
  - Multi-stage build for minimal image size
  - Non-root user for security
  - Health checks for both exporter and database
  - Volume persistence for PostgreSQL data
