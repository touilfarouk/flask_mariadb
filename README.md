# Project Overview

This project is a Flask-based API with a modular frontend. Authentication is handled with JWTs. Access to sensitive endpoints is enforced by the Python API (server-side), not just by the frontend.

## API Endpoints Overview

- Auth (`/auth`)
  - `POST /auth/signup` → Create a user account. Body: `{ firstname, lastname, email, password, role? }` → returns `{ message, token }`.
  - `POST /auth/login` → Authenticate user. Body: `{ email, password }` → returns `{ message, token, user }`.
  - `GET /auth/users` → List users (admin only).
  - `PUT /auth/users/<id>` → Update user (admin only). Body: `{ firstname, lastname, role }`.
  - `DELETE /auth/users/<id>` → Delete user (admin only).

- Personnel (`/personnel`) [protected]
  - `GET /personnel/all` → List personnel with aggregated sections.
  - `GET /personnel/<id>` → Get personnel by id with sections.
  - `GET /personnel/<id>/sections` → Get section IDs assigned to personnel.
  - `POST /personnel/add` (admin) → Create personnel with optional `sections: number[]`.
  - `PUT /personnel/<id>` (admin) → Update personnel and their section assignments.
  - `DELETE /personnel/<id>` (admin) → Delete personnel (links removed via cascade).

- Section (`/section`) [protected]
  - `GET /section/all` → List sections with aggregated personnel.
  - `POST /section/add` (admin) → Create a section (supports linking personnels via join table).
  - `PUT /section/update/<id>` (admin) → Update section and reassign personnel.
  - `DELETE /section/delete/<id>` (admin) → Delete section (links removed via cascade).

- Utility
  - `GET /protected` [protected] → Validate token and return decoded user info `{ id, email, role }`.

Notes:
- All protected endpoints require `Authorization: Bearer <token>`.
- Admin-only endpoints additionally require `role === 'admin'` (enforced server-side).

## Quick Start (Walkthrough)

- Login
  - Open `frontend/login.html` in your browser.
  - Use the default admin credentials: `admin@example.com` / `admin123` (see `api/sql.sql`).
  - On success, a JWT is stored in `localStorage` and you are redirected to `frontend/index.html`.

- Dashboard
  - The dashboard loads counts via `GET /personnel/all` and `GET /section/all`.
  - Use the sidebar to navigate to Personnel or Sections.
  - Toggle dark/light theme with the floating button (state saved to `localStorage`).

- Manage Sections
  - Go to `frontend/section.html`.
  - Add a section by filling `code_section`, `label`, `unit`, `type` then submit.
  - Edit by clicking ✏️ which prefills the form, then submit to update.
  - Delete by clicking 🗑, then confirm.

- Manage Personnel
  - Go to `frontend/personnel.html`.
  - The Sections dropdown is auto-populated from `/section/all`.
  - Add a personnel with `matricule`, `nom`, `qualification`, `affectation` and select multiple sections.
  - Edit a personnel using ✏️; the app fetches current section assignments via `/personnel/<id>/sections` and preselects them.
  - Delete using 🗑 with confirmation.

Tip: If your session expires (401), the app clears the token and redirects to `login.html` automatically (see `frontend/js/api.js`).

## Example Requests and Responses

All examples assume `API_BASE_URL=http://127.0.0.1:3000`. Send the JWT as `Authorization: Bearer <token>`.

- Auth

```bash
# Signup
curl -s -X POST "$API_BASE_URL/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "firstname": "Alice",
    "lastname": "Smith",
    "email": "alice@example.com",
    "password": "alice123",
    "role": "customer"
  }'

# Login
curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# List users (admin)
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/auth/users"

# Update user (admin)
curl -s -X PUT "$API_BASE_URL/auth/users/2" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{ "firstname": "Alice", "lastname": "Cooper", "role": "manager" }'

# Delete user (admin)
curl -s -X DELETE "$API_BASE_URL/auth/users/2" \
  -H "Authorization: Bearer $TOKEN"
```

- Personnel

```bash
# List personnel
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/personnel/all"

# Get personnel by ID
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/personnel/1"

# Get personnel's section IDs
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/personnel/1/sections"

# Create personnel (admin)
curl -s -X POST "$API_BASE_URL/personnel/add" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "matricule": "EMP010",
    "nom": "Jane Doe",
    "qualification": "Analyste",
    "affectation": "Comptabilité",
    "sections": [1,2]
  }'

# Update personnel (admin)
curl -s -X PUT "$API_BASE_URL/personnel/1" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "matricule": "EMP001",
    "nom": "Dupont Jean",
    "qualification": "Directeur",
    "affectation": "Direction",
    "sections": [1,3]
  }'

# Delete personnel (admin)
curl -s -X DELETE "$API_BASE_URL/personnel/1" \
  -H "Authorization: Bearer $TOKEN"
```

- Section

```bash
# List sections
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/section/all"

# Create section (admin)
curl -s -X POST "$API_BASE_URL/section/add" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "code_section": 500,
    "label": "Qualité",
    "unit": "QA",
    "type": "Operational"
  }'

# Update section (admin)
curl -s -X PUT "$API_BASE_URL/section/update/1" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "code_section": 100,
    "label": "Direction Générale",
    "unit": "DG",
    "type": "Administrative"
  }'

# Delete section (admin)
curl -s -X DELETE "$API_BASE_URL/section/delete/1" \
  -H "Authorization: Bearer $TOKEN"
```

- Protected route

```bash
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE_URL/protected"
```

Example JSON response snippets

```json
// GET /personnel/all
{
  "success": true,
  "data": [
    {
      "id": 1,
      "matricule": "EMP001",
      "nom": "Dupont Jean",
      "qualification": "Directeur",
      "affectation": "Direction",
      "sections": "Direction Générale, Comptabilité"
    }
  ]
}

// GET /section/all
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code_section": 100,
      "label": "Direction Générale",
      "type": "Administrative",
      "unit": "DG",
      "personnels": "Dupont Jean"
    }
  ]
}

// POST /auth/login
{
  "message": "Login successful",
  "token": "<JWT>",
  "user": { "id": 1, "firstname": "Admin", "lastname": "User", "email": "admin@example.com", "role": "admin" }
}

## VS Code REST Client (.http)

Save the following content as `requests.http` at the project root. Install the VS Code extension "REST Client" (humao.rest-client). You can then click "Send Request" above each request.

```http
@baseUrl = http://127.0.0.1:3000
@adminEmail = admin@example.com
@adminPassword = admin123
@json = application/json

### Auth → Signup
POST {{baseUrl}}/auth/signup
Content-Type: {{json}}

{
  "firstname": "Alice",
  "lastname": "Smith",
  "email": "alice@example.com",
  "password": "alice123",
  "role": "customer"
}

### Auth → Login (captures token)
POST {{baseUrl}}/auth/login
Content-Type: {{json}}

{
  "email": "{{adminEmail}}",
  "password": "{{adminPassword}}"
}

> {% client.global.set("token", response.body.token); %}

### Utility → Protected (verify token)
GET {{baseUrl}}/protected
Authorization: Bearer {{token}}

### Auth → List users (admin)
GET {{baseUrl}}/auth/users
Authorization: Bearer {{token}}

### Auth → Update user (admin)
PUT {{baseUrl}}/auth/users/2
Authorization: Bearer {{token}}
Content-Type: {{json}}

{
  "firstname": "Alice",
  "lastname": "Cooper",
  "role": "manager"
}

### Auth → Delete user (admin)
DELETE {{baseUrl}}/auth/users/2
Authorization: Bearer {{token}}

### Section → List
GET {{baseUrl}}/section/all
Authorization: Bearer {{token}}

### Section → Create (admin)
POST {{baseUrl}}/section/add
Authorization: Bearer {{token}}
Content-Type: {{json}}

{
  "code_section": 500,
  "label": "Qualité",
  "unit": "QA",
  "type": "Operational"
}

### Section → Update (admin)
PUT {{baseUrl}}/section/update/1
Authorization: Bearer {{token}}
Content-Type: {{json}}

{
  "code_section": 100,
  "label": "Direction Générale",
  "unit": "DG",
  "type": "Administrative"
}

### Section → Delete (admin)
DELETE {{baseUrl}}/section/delete/1
Authorization: Bearer {{token}}

### Personnel → List
GET {{baseUrl}}/personnel/all
Authorization: Bearer {{token}}

### Personnel → Get by ID
GET {{baseUrl}}/personnel/1
Authorization: Bearer {{token}}

### Personnel → Get section IDs
GET {{baseUrl}}/personnel/1/sections
Authorization: Bearer {{token}}

### Personnel → Create (admin)
POST {{baseUrl}}/personnel/add
Authorization: Bearer {{token}}
Content-Type: {{json}}

{
  "matricule": "EMP010",
  "nom": "Jane Doe",
  "qualification": "Analyste",
  "affectation": "Comptabilité",
  "sections": [1,2]
}

### Personnel → Update (admin)
PUT {{baseUrl}}/personnel/1
Authorization: Bearer {{token}}
Content-Type: {{json}}

{
  "matricule": "EMP001",
  "nom": "Dupont Jean",
  "qualification": "Directeur",
  "affectation": "Direction",
  "sections": [1,3]
}

### Personnel → Delete (admin)
DELETE {{baseUrl}}/personnel/1
Authorization: Bearer {{token}}
```

Notes
- You can change `@baseUrl` to point to another server.
- After running the Login request, the token is captured and reused automatically.

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
