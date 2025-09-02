from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
from config import db_config
from utils.auth import generate_token, token_required

app = Flask(__name__)
CORS(app)

# ✅ No SECRET_KEY here, we now keep it in config.py
@app.route("/section/all", methods=["GET"])
def get_sections():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, label, type, unit FROM section ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": rows}), 200, {"Cache-Control": "no-store"}


# ✅ Section routes
@app.route("/section/add", methods=["POST"])
def add_section():
    data = request.json
    label = data.get("label")
    unit = data.get("unit")
    type = data.get("type")
    personnel_id = data.get("personnel_id")  # can be None / null

    # ✅ only check required fields
    if not label or not unit or not type:
        return jsonify({"error": "Label, Unit, and Type are required"}), 400

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO section (label, unit, type, personnel_id) VALUES (%s, %s, %s, %s)",
        (label, unit, type, personnel_id)  # if personnel_id is None, MySQL will insert NULL
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"success": True, "id": new_id}), 201







# -------------------- Personnel Routes --------------------

# GET all personnel with their section label
@app.route("/personnel/all", methods=["GET"])
def get_personnel():
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.firstname, p.lastname, p.email, p.code_section,
               GROUP_CONCAT(s.label SEPARATOR ', ') AS section_labels
        FROM personnel p
        LEFT JOIN section s ON s.personnel_id = p.id
        GROUP BY p.id
        ORDER BY p.id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": rows}), 200, {"Cache-Control": "no-store"}



# ADD a new personnel
@app.route("/personnel/add", methods=["POST"])
def add_personnel():
    data = request.json
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    code_section = data.get("code_section")  # optional

    if not firstname or not lastname or not email:
        return jsonify({"error": "Firstname, Lastname, and Email are required"}), 400

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO personnel (firstname, lastname, email, code_section) VALUES (%s, %s, %s, %s)",
        (firstname, lastname, email, code_section)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"success": True, "id": new_id}), 201


# Optional: assign a section to personnel
@app.route("/personnel/assign_section", methods=["POST"])
def assign_section():
    data = request.json
    personnel_id = data.get("personnel_id")
    section_id = data.get("section_id")

    if not personnel_id or not section_id:
        return jsonify({"error": "Personnel ID and Section ID are required"}), 400

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE section SET personnel_id=%s WHERE id=%s",
        (personnel_id, section_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True}), 200














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
        (firstname, lastname, email, hashed_password.decode("utf-8"), role)
    )
    conn.commit()
    cursor.close()
    conn.close()

    token = generate_token(email, role)
    return jsonify({"message": "Signup successful", "token": token}), 200


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


@app.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({
        "email": request.user['email'],
        "role": request.user['role'],
        "message": "Welcome to the protected route!"
    }), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=3000, debug=True)
