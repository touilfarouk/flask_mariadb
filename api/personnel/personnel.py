from flask import Blueprint, request, jsonify, send_file
import pymysql
import io
from datetime import datetime
from utils.auth import token_required, roles_required
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


# ✅ Get section IDs for personnel
@personnel_bp.route("/<int:personnel_id>/sections", methods=["GET"])
@token_required
def get_personnel_sections(personnel_id):
    try:
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("""
            SELECT section_id 
            FROM personnel_section 
            WHERE personnel_id = %s
        """, (personnel_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        section_ids = [row['section_id'] for row in rows]
        return jsonify({"success": True, "data": section_ids}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Add new personnel with sections
@personnel_bp.route("/add", methods=["POST"])
@token_required
@roles_required(["admin"])
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

        # Insert section links with validation
        if section_ids:
            # Convert to integers and validate
            try:
                section_ids = [int(sid) for sid in section_ids if sid]
            except (ValueError, TypeError):
                cur.close()
                conn.close()
                return jsonify({"success": False, "error": "Invalid section ID format"}), 400
                
            for sid in section_ids:
                # Validate section exists before inserting
                cur.execute("SELECT id FROM section WHERE id = %s", (sid,))
                if cur.fetchone():
                    cur.execute("INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)", (new_id, sid))
                else:
                    cur.close()
                    conn.close()
                    return jsonify({"success": False, "error": f"Section with ID {sid} not found"}), 400

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "id": new_id, "message": "Personnel ajouté avec succès"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Update personnel and sections
@personnel_bp.route("/<int:personnel_id>", methods=["PUT"])
@token_required
@roles_required(["admin"])
def update_personnel(personnel_id):
    try:
        data = request.json or {}
        print(f"DEBUG: Update request for personnel ID {personnel_id}")
        print(f"DEBUG: Request data: {data}")
        
        matricule = data.get("matricule")
        nom = data.get("nom")
        qualification = data.get("qualification")
        affectation = data.get("affectation")
        section_ids = data.get("sections", [])

        if not all([matricule, nom, qualification, affectation]):
            return jsonify({"success": False, "error": "Champs obligatoires manquants"}), 400

        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        # Check if personnel exists first
        cur.execute("SELECT matricule FROM personnel WHERE id = %s", (personnel_id,))
        current_personnel = cur.fetchone()
        
        if not current_personnel:
            cur.close()
            conn.close()
            return jsonify({"success": False, "error": "Personnel non trouvé"}), 404

        # Check duplicate matricule only if matricule is being changed
        if current_personnel['matricule'] != matricule:
            cur.execute("SELECT id FROM personnel WHERE matricule = %s", (matricule,))
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

        # Note: cur.rowcount can be 0 when values are unchanged. We already checked existence above,
        # so do not treat 0 affected rows as not found. Proceed to update section links below.

        # Reset and reinsert sections
        cur.execute("DELETE FROM personnel_section WHERE personnel_id = %s", (personnel_id,))
        
        # Only insert sections if provided
        if section_ids:
            # Convert to integers and validate
            try:
                section_ids = [int(sid) for sid in section_ids if sid]
            except (ValueError, TypeError):
                cur.close()
                conn.close()
                return jsonify({"success": False, "error": "Invalid section ID format"}), 400
                
            for sid in section_ids:
                # Validate section exists before inserting
                cur.execute("SELECT id FROM section WHERE id = %s", (sid,))
                if cur.fetchone():
                    cur.execute(
                        "INSERT INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)",
                        (personnel_id, sid),
                    )
                else:
                    cur.close()
                    conn.close()
                    return jsonify({"success": False, "error": f"Section with ID {sid} not found"}), 400

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Personnel modifié avec succès"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ✅ Delete personnel
@personnel_bp.route("/<int:personnel_id>", methods=["DELETE"])
@token_required
@roles_required(["admin"])
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
