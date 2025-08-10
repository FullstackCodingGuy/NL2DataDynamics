# Developer Documentation

## Version 0.1.0 – Initial Backend Implementation

### Backend Structure

- [`backend/app/main.py`](backend/app/main.py:1): FastAPI app entry point, includes API routes and health check.
- [`backend/app/config.py`](backend/app/config.py:1): Configuration for environment variables, DB URL, secret key, token expiry.
- [`backend/app/database.py`](backend/app/database.py:1): SQLAlchemy engine, session, and base model setup.
- [`backend/app/models.py`](backend/app/models.py:1): User model with fields for username, email, hashed password, active status, and role.
- [`backend/app/auth.py`](backend/app/auth.py:1): OAuth2/JWT authentication logic, token generation, user verification.
- [`backend/app/routes.py`](backend/app/routes.py:1): API endpoints for user registration, login, and protected user info.
- [`backend/app/init_db.py`](backend/app/init_db.py:1): Script to initialize and seed the SQLite database.

### Authentication Flow

- Registration via `/register` endpoint.
- Login via `/token` endpoint, returns JWT access token.
- Protected endpoints require JWT in Authorization header.

### Database

- Uses SQLAlchemy ORM for DB abstraction.
- Default DB is SQLite for development; configurable for other SQL databases.

#### How to Initialize the Database

1. From your project root, run:
   ```bash
   python backend/app/init_db.py
   or
   python -m backend.app.init_db
   ```
   If you see an ImportError about relative imports, ensure you use absolute imports in `init_db.py`:
   ```python
   from backend.app.database import engine, Base, SessionLocal
   from backend.app.models import User
   ```
2. This will create all tables and seed the admin user (`admin` / `admin123`).
3. Run this script again if you change the schema or want to reseed data.

---

## How to Start the Application

### Prerequisites

- Python 3.11+
- Recommended: Use a virtual environment to avoid system package conflicts.

### Setting Up a Virtual Environment

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```
3. Install dependencies inside the virtual environment:
   ```bash
   pip install fastapi uvicorn sqlalchemy python-jose python-multipart
   ```

### Running the Backend (Development)

**Important:**  
To avoid import errors, always run Uvicorn from the project root directory (where the backend/ folder is located) and use absolute module paths.

1. Change directory to your project root:
   ```bash
   cd path/to/your/project/root
   ```
2. Start the FastAPI server with the correct module path:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. The API will be available at [http://localhost:8000](http://localhost:8000)

### Accessing API Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Both are enabled by default in FastAPI unless explicitly disabled in `main.py`.

### Environment Variables

- Set `DB_URL` for your database connection string (default is SQLite).
- Set `SECRET_KEY` for JWT token signing.

---

### Troubleshooting Installation Issues

- If you encounter PEP 668 errors, always use a virtual environment or pipx.
- To override and install system-wide (not recommended), use:
  ```bash
  python3 -m pip install fastapi --break-system-packages
  ```
- For user-level installs, add `--user` flag:
  ```bash
  python3 -m pip install fastapi --user
  ```

---

### Next Steps

- Implement analytics, plugin system, and frontend integration.
- Update this documentation with each new feature, change, or enhancement.
