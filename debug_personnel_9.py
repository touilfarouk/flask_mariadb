#!/usr/bin/env python3
"""
Debug script to check personnel ID 9 specifically
"""

import requests
import json

API_BASE = "http://127.0.0.1:3000"

def get_admin_token():
    """Login as admin and get JWT token"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Login failed: {response.text}")
        return None

def debug_personnel_9():
    """Debug personnel ID 9 specifically"""
    token = get_admin_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("DEBUGGING PERSONNEL ID 9")
    print("=" * 40)
    
    # Check if personnel 9 exists
    print("\n1. Checking if personnel ID 9 exists...")
    response = requests.get(f"{API_BASE}/personnel/9", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        personnel_data = response.json().get("data", {})
        print(f"   Personnel 9 exists: {json.dumps(personnel_data, indent=2)}")
    else:
        print(f"   Personnel 9 not found: {response.text}")
        return
    
    # Check personnel sections
    print("\n2. Checking personnel 9 sections...")
    response = requests.get(f"{API_BASE}/personnel/9/sections", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        sections = response.json().get("data", [])
        print(f"   Personnel 9 sections: {sections}")
    else:
        print(f"   Failed to get sections: {response.text}")
    
    # Try a simple update with different matricule
    print("\n3. Attempting simple update with different matricule...")
    update_data = {
        "matricule": f"UPDATED_{personnel_data.get('matricule', 'MULTI1757931318')}",
        "nom": personnel_data.get("nom", "Test Employee Multi"),
        "qualification": personnel_data.get("qualification", "Senior Manager"),
        "affectation": personnel_data.get("affectation", "Multi Department"),
        "sections": [2, 3]  # Assign to sections 2 and 3
    }
    print(f"   Update data: {json.dumps(update_data, indent=2)}")
    
    response = requests.put(f"{API_BASE}/personnel/9", json=update_data, headers=headers)
    print(f"   Update Status: {response.status_code}")
    print(f"   Update Response: {response.text}")
    
    # Try update with same matricule
    print("\n4. Attempting update with SAME matricule...")
    update_data_same = {
        "matricule": personnel_data.get("matricule"),
        "nom": "Updated Name Same Matricule",
        "qualification": "Updated Qualification",
        "affectation": "Updated Department",
        "sections": [1]  # Different sections
    }
    print(f"   Update data (same matricule): {json.dumps(update_data_same, indent=2)}")
    
    response = requests.put(f"{API_BASE}/personnel/9", json=update_data_same, headers=headers)
    print(f"   Update Status (same matricule): {response.status_code}")
    print(f"   Update Response (same matricule): {response.text}")
    
    # Verify after update
    if response.status_code == 200:
        print("\n4. Verifying after update...")
        response = requests.get(f"{API_BASE}/personnel/9", headers=headers)
        if response.status_code == 200:
            updated_data = response.json().get("data", {})
            print(f"   Updated personnel 9: {json.dumps(updated_data, indent=2)}")
        else:
            print(f"   Failed to verify update: {response.text}")

if __name__ == "__main__":
    debug_personnel_9()
