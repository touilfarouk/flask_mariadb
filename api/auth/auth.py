from flask import Blueprint, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
from config import db_config
from utils.auth import generate_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")



@auth_bp.route("/signup", methods=["POST"])
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
        (firstname, lastname, email, hashed_password.decode("utf-8"), role)
    )
    conn.commit()
    user_id = cursor.lastrowid   # ✅ capture inserted user_id
    cursor.close()
    conn.close()

    token = generate_token(user_id, email, role)  # ✅ now includes id
    return jsonify({"message": "Signup successful", "token": token}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = generate_token(user["id"], user["email"], user["role"])  # ✅ pass id
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "firstname": user["firstname"],
                "lastname": user["lastname"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200
    else:
        return jsonify({"error": "Invalid password"}), 401



@auth_bp.route("/users", methods=["GET"])
@token_required
def get_users():
    """📋 Récupérer tous les utilisateurs"""
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("SELECT id, firstname, lastname, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": users}), 200


@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    """✏ Mettre à jour un utilisateur"""
    data = request.json
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    role = data.get("role")

    if not firstname or not lastname or not role:
        return jsonify({"error": "firstname, lastname et role requis"}), 400

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET firstname=%s, lastname=%s, role=%s WHERE id=%s",
        (firstname, lastname, role, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Utilisateur mis à jour avec succès"}), 200


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(user_id):
    """🗑 Supprimer un utilisateur"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Utilisateur supprimé avec succès"}), 200


