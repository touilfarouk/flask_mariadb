import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import SECRET_KEY

# ✅ Generate JWT token including user_id
def generate_token(user_id, email, role):
    payload = {
        "id": user_id,   # 👈 add user_id from DB
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Middleware: verify JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token is missing"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid token format"}), 401

        token = parts[1]
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded  # 👈 now contains id, email, role
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


# Role-based authorization decorator
def roles_required(allowed_roles):
    """
    Ensure the authenticated user has one of the allowed roles.

    Usage:
        @app.route('/admin')
        @token_required
        @roles_required(['admin'])
        def admin_only():
            ...
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or 'role' not in user:
                return jsonify({"error": "Unauthorized"}), 401
            if user['role'] not in allowed_roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper
