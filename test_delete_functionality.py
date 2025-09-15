#!/usr/bin/env python3
"""
Test delete functionality for both personnel and sections
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

def test_delete_functionality():
    """Test delete functionality for personnel and sections"""
    token = get_admin_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("TESTING DELETE FUNCTIONALITY")
    print("=" * 50)
    
    # Test 1: Create test personnel to delete
    print("\n1. Creating test personnel for deletion...")
    test_personnel = {
        "matricule": "DELETE_TEST_001",
        "nom": "Test Delete Personnel",
        "qualification": "Test Manager",
        "affectation": "Test Department",
        "sections": []
    }
    
    response = requests.post(f"{API_BASE}/personnel/add", json=test_personnel, headers=headers)
    if response.status_code == 201:
        personnel_id = response.json().get("id")
        print(f"   Test personnel created with ID: {personnel_id}")
    else:
        print(f"   Failed to create test personnel: {response.text}")
        return
    
    # Test 2: Delete personnel
    print(f"\n2. Testing personnel deletion (ID: {personnel_id})...")
    response = requests.delete(f"{API_BASE}/personnel/{personnel_id}", headers=headers)
    print(f"   Delete Status: {response.status_code}")
    print(f"   Delete Response: {response.text}")
    
    if response.status_code == 200:
        print("   Personnel deletion successful!")
        
        # Verify deletion
        verify_response = requests.get(f"{API_BASE}/personnel/{personnel_id}", headers=headers)
        if verify_response.status_code == 404:
            print("   Verified: Personnel no longer exists")
        else:
            print(f"   Warning: Personnel still exists: {verify_response.text}")
    else:
        print("   Personnel deletion failed!")
    
    # Test 3: Create test section to delete
    print("\n3. Creating test section for deletion...")
    test_section = {
        "code_section": "DELETE_TEST",
        "label": "Test Delete Section",
        "unit": "Test Unit",
        "type": "Test Type"
    }
    
    response = requests.post(f"{API_BASE}/section/add", json=test_section, headers=headers)
    if response.status_code == 201:
        section_id = response.json().get("id")
        print(f"   Test section created with ID: {section_id}")
    else:
        print(f"   Failed to create test section: {response.text}")
        return
    
    # Test 4: Delete section
    print(f"\n4. Testing section deletion (ID: {section_id})...")
    response = requests.delete(f"{API_BASE}/section/delete/{section_id}", headers=headers)
    print(f"   Delete Status: {response.status_code}")
    print(f"   Delete Response: {response.text}")
    
    if response.status_code == 200:
        print("   Section deletion successful!")
        
        # Verify deletion by getting all sections
        verify_response = requests.get(f"{API_BASE}/section/all", headers=headers)
        if verify_response.status_code == 200:
            sections = verify_response.json().get("data", [])
            deleted_section = next((s for s in sections if s["id"] == section_id), None)
            if not deleted_section:
                print("   Verified: Section no longer exists in list")
            else:
                print(f"   Warning: Section still exists: {deleted_section}")
    else:
        print("   Section deletion failed!")
    
    # Test 5: Test deleting non-existent records
    print("\n5. Testing deletion of non-existent records...")
    
    # Try to delete non-existent personnel
    response = requests.delete(f"{API_BASE}/personnel/99999", headers=headers)
    print(f"   Non-existent personnel delete status: {response.status_code}")
    if response.status_code == 404:
        print("   Correctly returned 404 for non-existent personnel")
    
    # Try to delete non-existent section
    response = requests.delete(f"{API_BASE}/section/delete/99999", headers=headers)
    print(f"   Non-existent section delete status: {response.status_code}")
    if response.status_code == 404:
        print("   Correctly returned 404 for non-existent section")
    
    print("\n" + "=" * 50)
    print("DELETE FUNCTIONALITY TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_delete_functionality()
