#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed the database with sample sections, personnel, and links without recreating tables.
Safe to run multiple times (uses INSERT IGNORE and checks).
"""
import pymysql
from api.config import db_config

SECTIONS = [
    {"code_section": 100, "label": "Direction Générale", "unit": "DG", "type": "Administrative"},
    {"code_section": 200, "label": "Comptabilité", "unit": "COMPTA", "type": "Financial"},
    {"code_section": 300, "label": "Ressources Humaines", "unit": "RH", "type": "Administrative"},
    {"code_section": 400, "label": "Production", "unit": "PROD", "type": "Operational"},
]

PERSONNEL = [
    {"matricule": "EMP001", "nom": "Dupont Jean", "qualification": "Directeur", "affectation": "Direction", "sections": [100]},
    {"matricule": "EMP002", "nom": "Martin Marie", "qualification": "Comptable", "affectation": "Comptabilité", "sections": [200]},
    {"matricule": "EMP003", "nom": "Bernard Paul", "qualification": "RH Manager", "affectation": "Ressources Humaines", "sections": [300]},
    {"matricule": "EMP004", "nom": "Durand Sophie", "qualification": "Opérateur", "affectation": "Production", "sections": [400]},
]

def seed():
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    # Insert sections (by unique code_section)
    code_to_id = {}
    for s in SECTIONS:
        cur.execute(
            """
            INSERT INTO section (code_section, label, unit, type)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE label=VALUES(label), unit=VALUES(unit), type=VALUES(type)
            """,
            (s["code_section"], s["label"], s["unit"], s["type"]),
        )
        # Fetch id
        cur.execute("SELECT id FROM section WHERE code_section=%s", (s["code_section"],))
        row = cur.fetchone()
        code_to_id[s["code_section"]] = row["id"]

    # Insert personnel (by unique matricule)
    matricule_to_id = {}
    for p in PERSONNEL:
        cur.execute(
            """
            INSERT INTO personnel (matricule, nom, qualification, affectation)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nom=VALUES(nom), qualification=VALUES(qualification), affectation=VALUES(affectation)
            """,
            (p["matricule"], p["nom"], p["qualification"], p["affectation"]),
        )
        cur.execute("SELECT id FROM personnel WHERE matricule=%s", (p["matricule"],))
        prow = cur.fetchone()
        pid = prow["id"]
        matricule_to_id[p["matricule"]] = pid

        # Reset links for that personnel, then insert
        cur.execute("DELETE FROM personnel_section WHERE personnel_id=%s", (pid,))
        for code in p.get("sections", []):
            sid = code_to_id.get(code)
            if sid:
                cur.execute(
                    "INSERT IGNORE INTO personnel_section (personnel_id, section_id) VALUES (%s, %s)",
                    (pid, sid),
                )

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding completed. Sections and personnel are populated.")

if __name__ == "__main__":
    seed()
