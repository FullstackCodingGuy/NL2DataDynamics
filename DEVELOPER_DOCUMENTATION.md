# Developer Documentation

## Version 0.1.0 – Initial Backend Implementation

### Backend Structure

- [`backend/app/main.py`](backend/app/main.py:1): FastAPI app entry point, includes API routes and health check.
- [`backend/app/config.py`](backend/app/config.py:1): Configuration for environment variables, DB URL, secret key, token expiry.
- [`backend/app/database.py`](backend/app/database.py:1): SQLAlchemy engine, session, and base model setup.
- [`backend/app/models.py`](backend/app/models.py:1): User model with fields for username, email, hashed password, active status, and role.
- [`backend/app/auth.py`](backend/app/auth.py:1): OAuth2/JWT authentication logic, token generation, user verification.
- [`backend/app/routes.py`](backend/app/routes.py:1): API endpoints for user registration, login, and protected user info.

### Authentication Flow

- Registration via `/register` endpoint.
- Login via `/token` endpoint, returns JWT access token.
- Protected endpoints require JWT in Authorization header.

### Database

- Uses SQLAlchemy ORM for DB abstraction.
- Default DB is SQLite for development; configurable for other SQL databases.

### Next Steps

- Implement analytics, plugin system, and frontend integration.
- Update this documentation with each new feature, change, or enhancement.
