from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
from config import db_config
from utils.auth import generate_token, token_required
from section.section import section_bp
from personnel.personnel import personnel_bp
from auth.auth import auth_bp
app = Flask(__name__)
CORS(app)

# ✅ No SECRET_KEY here, we now keep it in config.py
# 🔹 Register blueprints
app.register_blueprint(section_bp)
app.register_blueprint(personnel_bp)
app.register_blueprint(auth_bp)



@app.route("/users", methods=["GET"])
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


@app.route("/users/<int:user_id>", methods=["PUT"])
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


@app.route("/users/<int:user_id>", methods=["DELETE"])
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







@app.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({
        "id": request.user['id'],
        "email": request.user['email'],
        "role": request.user['role'],
        "message": "Welcome to the protected route!"
    }), 200

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000, debug=True)
