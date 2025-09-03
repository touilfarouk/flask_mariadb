from flask import Blueprint, request, jsonify
import pymysql
from config import db_config

personnel_bp = Blueprint("personnel", __name__, url_prefix="/personnel")


@personnel_bp.route("/sections", methods=["GET"])
def get_sections():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, label FROM section ORDER BY label ASC")
    sections = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": sections})


# ✅ Get all personnel
@personnel_bp.route("/all", methods=["GET"])
def get_personnel():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.firstname, p.lastname, p.role, p.code_section,
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


# ✅ Add a new personnel
@personnel_bp.route("/add", methods=["POST"])
def add_personnel():
    data = request.json
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    role = data.get("role")
    code_section = data.get("code_section")  # optional

    if not firstname or not lastname or not role:
        return jsonify({"error": "Firstname, Lastname, and role are required"}), 400

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO personnel (firstname, lastname, role, code_section) VALUES (%s, %s, %s, %s)",
        (firstname, lastname, role, code_section)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"success": True, "id": new_id}), 201

















# ✅ Assign a section to personnel
@personnel_bp.route("/assign_section", methods=["POST"])
def assign_section():
    data = request.json
    personnel_id = data.get("personnel_id")
    section_id = data.get("section_id")

    if not personnel_id or not section_id:
        return jsonify({"error": "Personnel ID and Section ID are required"}), 400

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE section SET personnel_id=%s WHERE id=%s",
        (personnel_id, section_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True}), 200
