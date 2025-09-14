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
