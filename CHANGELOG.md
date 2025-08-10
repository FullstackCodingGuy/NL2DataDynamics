# Changelog

All notable changes to this project will be documented in this file.

## [0.1.3] - 2025-08-10

### Enhanced
- Added OpenAPI-compliant request/response models and docstrings to all API endpoints in [`backend/app/routes.py`](backend/app/routes.py:1) for proper Swagger documentation.

## [0.1.2] - 2025-08-10

### Added
- Implemented all major API endpoints in [`backend/app/routes.py`](backend/app/routes.py:1):
  - Health check
  - User registration, login, user info
  - Database query execution
  - Text analytics (placeholder)
  - Graphical analytics (placeholder)
  - Plugin registration and execution (placeholder)
  - Role management

## [0.1.1] - 2025-08-10

### Fixed
- Added `get_db` dependency function to [`backend/app/database.py`](backend/app/database.py:10) for proper DB session management and to resolve ImportError in API routes.

## [0.1.0] - 2025-08-10

### Added
- Initial FastAPI backend scaffold ([backend/app/main.py](backend/app/main.py:1))
- Configuration module for environment variables ([backend/app/config.py](backend/app/config.py:1))
- SQLAlchemy database integration ([backend/app/database.py](backend/app/database.py:1))
- User model for authentication and roles ([backend/app/models.py](backend/app/models.py:1))
- OAuth2/JWT authentication scaffolding ([backend/app/auth.py](backend/app/auth.py:1))
- API routes for registration, login, and protected user info ([backend/app/routes.py](backend/app/routes.py:1))
