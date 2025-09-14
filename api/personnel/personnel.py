from flask import Blueprint, request, jsonify, send_file
import pymysql
import io
from datetime import datetime
from utils.auth import token_required
#import pandas as pd  # keep for Excel import/export
from config import db_config

personnel_bp = Blueprint("personnel", __name__, url_prefix="/personnel")

# ✅ Get all personnel with sections
@personnel_bp.route("/all", methods=["GET"])
@token_required
def get_personnel():
    try:
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("""
            SELECT p.id, p.matricule, p.nom, p.qualification, p.affectation,
                   GROUP_CONCAT(s.label SEPARATOR ', ') AS sections
            FROM personnel p
            LEFT JOIN personnel_section ps ON p.id = ps.personnel_id
            LEFT JOIN section s ON ps.section_id = s.id
            GROUP BY p.id
            ORDER BY p.matricule ASC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"success": True, "data": rows}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Get personnel by ID (with sections)
@personnel_bp.route("/<int:personnel_id>", methods=["GET"])
@token_required
def get_personnel_by_id(personnel_id):
    try:
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("""
            SELECT p.id, p.matricule, p.nom, p.qualification, p.affectation,
                   GROUP_CONCAT(s.label SEPARATOR ', ') AS sections
            FROM personnel p
            LEFT JOIN personnel_section ps ON p.id = ps.personnel_id
            LEFT JOIN section s ON ps.section_id = s.id
            WHERE p.id = %s
            GROUP BY p.id
        """, (personnel_id,))
        row = cur.fetchone()
        cur.close()  
        conn.close()

        if row:
            return jsonify({"success": True, "data": row}), 200
        else:
            return jsonify({"success": False, "error": "Personnel not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Add new personnel with sections
@personnel_bp.route("/add", methods=["POST"])
@token_required
def add_personnel():
    try:
        data = request.json
        matricule = data.get("matricule")
        nom = data.get("nom")
        qualification = data.get("qualification")
        affectation = data.get("affectation")
        section_ids = data.get("sections", [])  # array of section IDs

        if not all([matricule, nom, qualification, affectation]):
            return jsonify({"success": False, "error": "Champs obligatoires manquants"}), 400

        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        # Check unique matricule
        cur.execute("SELECT id FROM personnel WHERE matricule = %s", (matricule,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "Ce matricule existe déjà"}), 400

        cur.execute("""
            INSERT INTO personnel (matricule, nom, qualification, affectation)
            VALUES (%s, %s, %s, %s)
        """, (matricule, nom, qualification, affectation))
        new_id = cur.lastrowid

        # Insert section links
        for sid in section_ids:
            cur.execute("INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)", (new_id, sid))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "id": new_id, "message": "Personnel ajouté avec succès"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Update personnel and sections
@personnel_bp.route("/<int:personnel_id>", methods=["PUT"])
@token_required
def update_personnel(personnel_id):
    try:
        data = request.json or {}
        matricule = data.get("matricule")
        nom = data.get("nom")
        qualification = data.get("qualification")
        affectation = data.get("affectation")
        section_ids = data.get("sections", [])

        if not all([matricule, nom, qualification, affectation]):
            return jsonify({"success": False, "error": "Champs obligatoires manquants"}), 400

        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        # Check duplicate matricule
        cur.execute("SELECT id FROM personnel WHERE matricule = %s AND id != %s", (matricule, personnel_id))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "Ce matricule existe déjà"}), 400

        # Update personnel
        cur.execute("""
            UPDATE personnel 
            SET matricule = %s, nom = %s, qualification = %s, affectation = %s
            WHERE id = %s
        """, (matricule, nom, qualification, affectation, personnel_id))

        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "Personnel non trouvé"}), 404

        # Reset and reinsert sections
        cur.execute("DELETE FROM personnel_section WHERE personnel_id = %s", (personnel_id,))
        for sid in section_ids:
            cur.execute(
                "INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)",
                (personnel_id, sid),
            )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Personnel modifié avec succès"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Delete personnel
@personnel_bp.route("/<int:personnel_id>", methods=["DELETE"])
@token_required
def delete_personnel(personnel_id):
    try:
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("DELETE FROM personnel WHERE id = %s", (personnel_id,))
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "Personnel non trouvé"}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Personnel supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
