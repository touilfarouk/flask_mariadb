#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:3000"

def login():
    """Login and get JWT token"""
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        print("Login successful - token obtained")
        return token
    else:
        print(f"Login failed: {response.status_code}")
        return None

def create_frontend_test_personnel(token):
    """Create personnel specifically for frontend delete testing"""
    personnel_data = {
        "matricule": "FRONTEND_DELETE_001",
        "nom": "Frontend Delete Test User",
        "qualification": "Test Engineer",
        "affectation": "Frontend Testing Department",
        "sections": []
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{API_BASE_URL}/personnel/add", json=personnel_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        personnel_id = data.get("id")
        print(f"Created test personnel for frontend testing:")
        print(f"  ID: {personnel_id}")
        print(f"  Name: {personnel_data['nom']}")
        print(f"  Matricule: {personnel_data['matricule']}")
        print(f"\nNow you can test delete from frontend:")
        print(f"1. Go to: http://127.0.0.1:5501/frontend/personnel.html")
        print(f"2. Look for personnel ID {personnel_id}")
        print(f"3. Click the delete button (trash icon)")
        print(f"4. Confirm deletion in dialog")
        print(f"5. Check console logs for delete process")
        return personnel_id
    else:
        print(f"Failed to create test personnel: {response.status_code}")
        return None

def main():
    print("=" * 60)
    print("CREATING PERSONNEL FOR FRONTEND DELETE TESTING")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Create test personnel
    test_id = create_frontend_test_personnel(token)
    
    if test_id:
        print("\n" + "=" * 60)
        print("READY FOR FRONTEND TESTING")
        print("=" * 60)
        print(f"Test personnel ID {test_id} is ready for deletion testing")
        print("Open the frontend and try deleting this personnel!")
    else:
        print("Failed to create test personnel")

if __name__ == "__main__":
    main()
