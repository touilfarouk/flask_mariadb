from flask import Blueprint, request, jsonify
import pymysql
from config import db_config
from utils.auth import token_required
section_bp = Blueprint("section", __name__, url_prefix="/section")

# ✅ Get all sections (with personnel)
@section_bp.route("/all", methods=["GET"])
@token_required
def get_sections():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.label, s.type, s.unit,
               GROUP_CONCAT(p.nom SEPARATOR ', ') AS personnels
        FROM section s
        LEFT JOIN personnel_section ps ON s.id = ps.section_id
        LEFT JOIN personnel p ON ps.personnel_id = p.id
        GROUP BY s.id
        ORDER BY s.id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": rows}), 200, {"Cache-Control": "no-store"}


# ✅ Add section (with optional personnel links)
@section_bp.route("/add", methods=["POST"])
@token_required
def add_section():
    data = request.json
    label = data.get("label")
    unit = data.get("unit")
    type = data.get("type")
    personnel_ids = data.get("personnels", [])  # expect list of IDs

    if not label or not unit or not type:
        return jsonify({"error": "Label, Unit, and Type are required"}), 400

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO section (label, unit, type) VALUES (%s, %s, %s)",
        (label, unit, type)
    )
    new_id = cur.lastrowid

    # Insert links into personnel_section
    for pid in personnel_ids:
        cur.execute(
            "INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)",
            (pid, new_id)
        )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "id": new_id}), 201


# ✅ Update section (and reassign personnel)
@section_bp.route("/update/<int:section_id>", methods=["PUT"])
@token_required
def update_section(section_id):
    data = request.json
    label = data.get("label")
    unit = data.get("unit")
    type = data.get("type")
    personnel_ids = data.get("personnels", [])

    if not label or not unit or not type:
        return jsonify({"error": "Label, Unit, and Type are required"}), 400

    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    cur.execute(
        "UPDATE section SET label=%s, unit=%s, type=%s WHERE id=%s",
        (label, unit, type, section_id)
    )

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({"error": "Section not found"}), 404

    # Reset links
    cur.execute("DELETE FROM personnel_section WHERE section_id=%s", (section_id,))
    for pid in personnel_ids:
        cur.execute(
            "INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)",
            (pid, section_id)
        )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Section updated successfully"}), 200


# ✅ Delete section (links auto-removed by ON DELETE CASCADE)
@section_bp.route("/delete/<int:section_id>", methods=["DELETE"])
@token_required
def delete_section(section_id):
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("DELETE FROM section WHERE id=%s", (section_id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({"error": "Section not found"}), 404
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Section deleted successfully"}), 200
