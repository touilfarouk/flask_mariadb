from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import jwt
import datetime
from functools import wraps
import bcrypt

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'your_secret_key'

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
  
    'database': 'comptabilite',
    'cursorclass': pymysql.cursors.DictCursor
}

# Utility: generate JWT token
def generate_token(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")

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
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

# Signup route
@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.json
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "customer")

    if not firstname or not lastname or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Email already in use"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (firstname, lastname, email, password, role) VALUES (%s, %s, %s, %s, %s)",
        (firstname, lastname, email, hashed_password, role)
    )
    conn.commit()
    cursor.close()
    conn.close()

    token = generate_token(email, role)
    return jsonify({"message": "Signup successful", "token": token}), 200

# Login route
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = generate_token(user['email'], user['role'])
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

# Protected route
@app.route("/protected", methods=["GET"])
@token_required
def protected():
    # Example: you can return user info
    user_info = {
        "email": request.user['email'],
        "role": request.user['role'],
        "message": "Welcome to the protected route!"
    }
    return jsonify(user_info), 200

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5050, debug=True)
