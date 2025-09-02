from flask import Blueprint, request, jsonify
import pymysql
from config import db_config

section_bp = Blueprint("section", __name__, url_prefix="/section")

# ✅ Get all sections
@section_bp.route("/all", methods=["GET"])
def get_sections():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT id, label, type, unit FROM section ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": rows}), 200, {"Cache-Control": "no-store"}


# ✅ Add section
@section_bp.route("/add", methods=["POST"])
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
        (label, unit, type, personnel_id)  # if personnel_id is None → MySQL inserts NULL
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"success": True, "id": new_id}), 201

