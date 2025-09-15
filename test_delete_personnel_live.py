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
        print("Login successful")
        return token
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_headers(token):
    """Get headers with JWT token"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

def create_test_personnel(token):
    """Create a test personnel for deletion"""
    personnel_data = {
        "matricule": "DELETE_TEST_001",
        "nom": "Test Delete Personnel",
        "qualification": "Test Qualification",
        "affectation": "Test Department",
        "sections": []
    }
    
    headers = get_headers(token)
    response = requests.post(f"{API_BASE_URL}/personnel/add", json=personnel_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        personnel_id = data.get("id")
        print(f"Test personnel created with ID: {personnel_id}")
        return personnel_id
    else:
        print(f"Failed to create test personnel: {response.status_code} - {response.text}")
        return None

def get_personnel_list(token):
    """Get all personnel to verify existence"""
    headers = get_headers(token)
    response = requests.get(f"{API_BASE_URL}/personnel/all", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        personnel_list = data.get("data", [])
        print(f"Found {len(personnel_list)} personnel in database")
        return personnel_list
    else:
        print(f"Failed to get personnel list: {response.status_code} - {response.text}")
        return []

def delete_personnel(token, personnel_id):
    """Delete personnel by ID"""
    headers = get_headers(token)
    response = requests.delete(f"{API_BASE_URL}/personnel/{personnel_id}", headers=headers)
    
    print(f"Delete request sent for personnel ID: {personnel_id}")
    print(f"Response status: {response.status_code}")
    
    try:
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        print(f"Personnel {personnel_id} deleted successfully")
        return True
    else:
        print(f"Failed to delete personnel {personnel_id}")
        return False

def verify_deletion(token, personnel_id):
    """Verify that personnel was actually deleted"""
    headers = get_headers(token)
    response = requests.get(f"{API_BASE_URL}/personnel/{personnel_id}", headers=headers)
    
    if response.status_code == 404:
        print(f"Verified: Personnel {personnel_id} no longer exists")
        return True
    else:
        print(f"Personnel {personnel_id} still exists after deletion")
        return False

def main():
    print("=" * 60)
    print("TESTING PERSONNEL DELETE FUNCTIONALITY")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Step 2: Show current personnel list
    print("\n2. Getting current personnel list...")
    personnel_list = get_personnel_list(token)
    
    if personnel_list:
        print("\nCurrent personnel:")
        for p in personnel_list[:5]:  # Show first 5
            print(f"   ID: {p.get('id')} - {p.get('nom')} ({p.get('matricule')})")
        if len(personnel_list) > 5:
            print(f"   ... and {len(personnel_list) - 5} more")
    
    # Step 3: Create test personnel
    print("\n3. Creating test personnel for deletion...")
    test_id = create_test_personnel(token)
    if not test_id:
        print("Cannot proceed without test personnel")
        return
    
    # Step 4: Verify creation
    print("\n4. Verifying test personnel exists...")
    updated_list = get_personnel_list(token)
    test_personnel = next((p for p in updated_list if p.get('id') == test_id), None)
    if test_personnel:
        print(f"Test personnel confirmed: {test_personnel.get('nom')} (ID: {test_id})")
    else:
        print(f"Test personnel not found in list")
        return
    
    # Step 5: Delete the test personnel
    print(f"\n5. Deleting test personnel (ID: {test_id})...")
    delete_success = delete_personnel(token, test_id)
    
    # Step 6: Verify deletion
    print(f"\n6. Verifying deletion...")
    if delete_success:
        verify_deletion(token, test_id)
        
        # Check updated list
        final_list = get_personnel_list(token)
        remaining_test = next((p for p in final_list if p.get('id') == test_id), None)
        if not remaining_test:
            print(f"Confirmed: Personnel {test_id} successfully removed from database")
        else:
            print(f"Personnel {test_id} still appears in personnel list")
    
    print("\n" + "=" * 60)
    print("DELETE TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
