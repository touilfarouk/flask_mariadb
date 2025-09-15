#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

API_BASE_URL = "http://127.0.0.1:3000"


def login():
    res = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    res.raise_for_status()
    return res.json().get("token")


def headers(token):
    return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}


def main():
    token = login()
    h = headers(token)

    print("1) Create section")
    payload = {"code_section": 9001, "label": "Integration QA", "unit": "QA", "type": "Operational", "personnels": []}
    r = requests.post(f"{API_BASE_URL}/section/add", json=payload, headers=h)
    print("Create:", r.status_code, r.text)
    if r.status_code not in (200, 201):
        return
    section_id = r.json().get("id")

    print("2) Update section (assign no personnels, change label)")
    up = {"code_section": 9001, "label": "Integration QA Team", "unit": "QA", "type": "Operational", "personnels": []}
    r = requests.put(f"{API_BASE_URL}/section/update/{section_id}", json=up, headers=h)
    print("Update:", r.status_code, r.text)

    print("3) Delete section")
    r = requests.delete(f"{API_BASE_URL}/section/delete/{section_id}", headers=h)
    print("Delete:", r.status_code, r.text)


if __name__ == "__main__":
    main()
