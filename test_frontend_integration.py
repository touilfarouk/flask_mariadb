#!/usr/bin/env python3
"""
Test frontend integration by simulating browser requests
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:3000"

def test_frontend_flow():
    """Test the complete frontend flow"""
    print("TESTING FRONTEND INTEGRATION FLOW")
    print("=" * 50)
    
    # Step 1: Login to get fresh token
    print("\n1. Getting fresh admin token...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("token")
    user_data = login_response.json().get("user", {})
    print(f"   Login successful for: {user_data.get('firstname')} {user_data.get('lastname')}")
    print(f"   Token preview: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Step 2: Test protected route
    print("\n2. Testing protected route...")
    protected_response = requests.get(f"{API_BASE}/protected", headers=headers)
    print(f"   Protected route status: {protected_response.status_code}")
    if protected_response.status_code == 200:
        print(f"   Protected response: {protected_response.json()}")
    
    # Step 3: Get sections for dropdown
    print("\n3. Loading sections for dropdown...")
    sections_response = requests.get(f"{API_BASE}/section/all", headers=headers)
    if sections_response.status_code == 200:
        sections = sections_response.json().get("data", [])
        print(f"   Loaded {len(sections)} sections")
        for section in sections:
            print(f"      - {section['id']}: {section['label']}")
    else:
        print(f"   Failed to load sections: {sections_response.text}")
        return
    
    # Step 4: Get all personnel
    print("\n4. Loading personnel list...")
    personnel_response = requests.get(f"{API_BASE}/personnel/all", headers=headers)
    if personnel_response.status_code == 200:
        personnel_list = personnel_response.json().get("data", [])
        print(f"   Loaded {len(personnel_list)} personnel")
        for person in personnel_list[:3]:  # Show first 3
            print(f"      - {person['id']}: {person['nom']} ({person.get('sections', 'No sections')})")
    else:
        print(f"   Failed to load personnel: {personnel_response.text}")
        return
    
    # Step 5: Test personnel operations
    if personnel_list:
        test_person = personnel_list[0]
        person_id = test_person['id']
        
        print(f"\n5. Testing personnel operations with ID {person_id}...")
        
        # Get individual personnel
        person_response = requests.get(f"{API_BASE}/personnel/{person_id}", headers=headers)
        if person_response.status_code == 200:
            person_data = person_response.json().get("data", {})
            print(f"   Individual personnel loaded: {person_data.get('nom')}")
        else:
            print(f"   Failed to load individual personnel: {person_response.text}")
            return
        
        # Get personnel sections
        sections_response = requests.get(f"{API_BASE}/personnel/{person_id}/sections", headers=headers)
        if sections_response.status_code == 200:
            assigned_sections = sections_response.json().get("data", [])
            print(f"   Personnel sections: {assigned_sections}")
        else:
            print(f"   Failed to load personnel sections: {sections_response.text}")
        
        # Test update (simulate frontend form submission)
        print(f"\n6. Testing personnel update (simulating frontend form)...")
        update_data = {
            "matricule": person_data.get("matricule"),
            "nom": f"Updated {person_data.get('nom', 'Name')}",
            "qualification": person_data.get("qualification", "Default"),
            "affectation": person_data.get("affectation", "Default"),
            "sections": [sections[0]["id"], sections[1]["id"]] if len(sections) >= 2 else [sections[0]["id"]]
        }
        
        print(f"   Update payload: {json.dumps(update_data, indent=2)}")
        
        update_response = requests.put(f"{API_BASE}/personnel/{person_id}", json=update_data, headers=headers)
        print(f"   Update status: {update_response.status_code}")
        print(f"   Update response: {update_response.text}")
        
        if update_response.status_code == 200:
            print("   Personnel update successful!")
            
            # Verify the update
            verify_response = requests.get(f"{API_BASE}/personnel/{person_id}", headers=headers)
            if verify_response.status_code == 200:
                updated_data = verify_response.json().get("data", {})
                print(f"   Verified update: {updated_data.get('nom')} - {updated_data.get('sections')}")
        else:
            print("   Personnel update failed!")
    
    print("\n" + "=" * 50)
    print("FRONTEND INTEGRATION TEST COMPLETED")
    print("=" * 50)
    print("\nToken for frontend testing:")
    print(f"Bearer {token}")

if __name__ == "__main__":
    test_frontend_flow()
