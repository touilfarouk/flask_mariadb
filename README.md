# Project Overview

This project is a Flask-based API with a modular frontend. Authentication is handled with JWTs. Access to sensitive endpoints is enforced by the Python API (server-side), not just by the frontend.

## Structure

- `api/`
  - `main.py`: Flask app entrypoint. Registers blueprints and exposes `GET /protected`.
  - `config.py`: `SECRET_KEY` and DB connection settings.
  - `utils/auth.py`: JWT generation, `@token_required`, and `@roles_required` decorators.
  - `auth/auth.py`: Auth endpoints (`/auth/signup`, `/auth/login`, `/auth/users*`).
  - `personnel/` and `section/`: Protected CRUD endpoints.
- `frontend/`
  - `index.html`, `login.html`, `personnel.html`, `section.html`.
  - `js/api.js`: Adds `Authorization: Bearer <token>` automatically if `localStorage["token"]` exists.
  - `js/login.js`: Handles login and stores token as `localStorage["token"]`.
  - `js/protected.js`: Optional client guard and server verification via `GET /protected`.

## Requirements

- Python 3.10+
- MariaDB/MySQL running with a database named in `api/config.py`.

Python packages:
- Flask
- flask-cors
- PyMySQL
- bcrypt
- PyJWT

## Setup (Windows)

1) Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

2) Install dependencies

```powershell
pip install Flask flask-cors PyMySQL bcrypt PyJWT
```

3) Configure backend

- Edit `api/config.py` and set:
  - `SECRET_KEY` to a strong random value.
  - `db_config` values for your environment.

4) Initialize database

- See `api/sql.sql` for tables and sample data as needed.

5) Run the API

```powershell
python api/main.py
```

The server runs on `http://127.0.0.1:3000` by default.

6) Open the frontend

- Double-click or serve static files under `frontend/`.
- Start at `frontend/login.html` to log in.
- `frontend/index.html` uses `js/protected.js` to verify session.

## Authentication & Authorization

- On successful login (`POST /auth/login`), the API returns a JWT.
- The frontend stores the token in `localStorage` under the key `token`.
- `frontend/js/api.js` automatically attaches `Authorization: Bearer <token>` to all requests when available.
- Backend enforces protection using `@token_required` on sensitive endpoints.

### Role-based Access (optional)

`api/utils/auth.py` provides a `@roles_required([...])` decorator. Example usage:

```python
from utils.auth import token_required, roles_required

@app.route('/admin-area')
@token_required
@roles_required(['admin'])
def admin_area():
    return jsonify({"ok": True})
```

If the user does not have an allowed role, the API returns HTTP 403.

## Notes

- Frontend checks in `js/protected.js` are for UX. The API remains the source of truth: requests without a valid token receive 401/403.
- Standard base URL in the frontend is `http://127.0.0.1:3000`.
- Consider moving secrets and DB credentials to environment variables for production.
