# Changelog

All notable changes to the OpenWebUI Prometheus Exporter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2023-12-07

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
- Flexible time window specification (hours, minutes)
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
