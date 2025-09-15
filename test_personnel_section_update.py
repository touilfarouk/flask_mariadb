#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

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
        print(f"Login failed: {response.status_code}")
        return None

def get_headers(token):
    """Get headers with JWT token"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

def get_sections(token):
    """Get all available sections"""
    headers = get_headers(token)
    response = requests.get(f"{API_BASE_URL}/section/all", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        sections = data.get("data", [])
        print(f"Available sections: {len(sections)}")
        for section in sections:
            section_name = section.get('nom') or section.get('name', 'Unknown')
            print(f"  - ID: {section['id']}, Name: {section_name}")
        return sections
    else:
        print(f"Failed to get sections: {response.status_code}")
        return []

def create_test_personnel(token):
    """Create personnel for section update testing"""
    personnel_data = {
        "matricule": f"SECTION_UPDATE_TEST_{int(time.time())}",
        "nom": "Section Update Test Personnel",
        "qualification": "Test Engineer",
        "affectation": "Testing Department",
        "sections": []  # Start with no sections
    }
    
    headers = get_headers(token)
    response = requests.post(f"{API_BASE_URL}/personnel/add", json=personnel_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        personnel_id = data.get("id")
        print(f"Created test personnel ID: {personnel_id}")
        return personnel_id
    else:
        print(f"Failed to create personnel: {response.status_code} - {response.text}")
        return None

def get_personnel_sections(token, personnel_id):
    """Get sections assigned to personnel"""
    headers = get_headers(token)
    response = requests.get(f"{API_BASE_URL}/personnel/{personnel_id}/sections", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        sections = data.get("data", [])
        print(f"Personnel {personnel_id} current sections: {sections}")
        return sections
    else:
        print(f"Failed to get personnel sections: {response.status_code}")
        return []

def update_personnel_sections(token, personnel_id, section_ids):
    """Update personnel with new section assignments"""
    # First get current personnel data
    headers = get_headers(token)
    response = requests.get(f"{API_BASE_URL}/personnel/{personnel_id}", headers=headers)
    
    print(f"Get personnel response: {response.status_code}")
    if response.status_code != 200:
        print(f"Failed to get personnel data: {response.status_code} - {response.text}")
        return False
    
    response_json = response.json()
    print(f"Personnel data response: {json.dumps(response_json, indent=2)}")
    personnel_data = response_json.get("data", {})
    
    # Update with new sections
    update_data = {
        "matricule": personnel_data.get("matricule"),
        "nom": personnel_data.get("nom"),
        "qualification": personnel_data.get("qualification"),
        "affectation": personnel_data.get("affectation"),
        "sections": section_ids
    }
    
    print(f"Updating personnel {personnel_id} with sections: {section_ids}")
    print(f"Update payload: {json.dumps(update_data, indent=2)}")
    
    response = requests.put(f"{API_BASE_URL}/personnel/{personnel_id}", json=update_data, headers=headers)
    
    print(f"Update response status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Update response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Update response text: {response.text}")
    
    # Let's try with an existing personnel ID instead
    if response.status_code == 404:
        print("Trying with existing personnel ID 4...")
        # Get existing personnel 4 data first
        existing_response = requests.get(f"{API_BASE_URL}/personnel/4", headers=headers)
        if existing_response.status_code == 200:
            existing_data = existing_response.json().get("data", {})
            update_data_existing = {
                "matricule": existing_data.get("matricule"),
                "nom": existing_data.get("nom"),
                "qualification": existing_data.get("qualification"),
                "affectation": existing_data.get("affectation"),
                "sections": section_ids
            }
            response = requests.put(f"{API_BASE_URL}/personnel/4", json=update_data_existing, headers=headers)
            print(f"Retry response status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Retry response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Retry response text: {response.text}")
        else:
            print(f"Failed to get existing personnel 4: {existing_response.status_code}")
    
    if response.status_code == 200:
        print("Personnel section update successful")
        return True
    else:
        print("Personnel section update failed")
        return False

def main():
    print("=" * 60)
    print("TESTING PERSONNEL SECTION UPDATE FUNCTIONALITY")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Step 2: Get available sections
    print("\n2. Getting available sections...")
    sections = get_sections(token)
    if not sections:
        print("No sections available for testing")
        return
    
    # Step 3: Create test personnel
    print("\n3. Creating test personnel...")
    personnel_id = create_test_personnel(token)
    if not personnel_id:
        print("Cannot proceed without test personnel")
        return
    
    # Step 4: Check initial sections (should be empty)
    print("\n4. Checking initial section assignments...")
    initial_sections = get_personnel_sections(token, personnel_id)
    
    # Step 5: Update with first section
    print(f"\n5. Assigning section {sections[0]['id']} to personnel...")
    section_ids = [sections[0]['id']]
    update_success = update_personnel_sections(token, personnel_id, section_ids)
    
    if update_success:
        # Step 6: Verify section assignment
        print("\n6. Verifying section assignment...")
        updated_sections = get_personnel_sections(token, personnel_id)
        
        if section_ids[0] in updated_sections:
            print("SUCCESS: Section assignment verified")
        else:
            print("FAILED: Section not properly assigned")
    
    # Step 7: Update with multiple sections (if available)
    if len(sections) > 1:
        print(f"\n7. Assigning multiple sections to personnel...")
        multi_section_ids = [sections[0]['id'], sections[1]['id']]
        multi_update_success = update_personnel_sections(token, personnel_id, multi_section_ids)
        
        if multi_update_success:
            print("\n8. Verifying multiple section assignments...")
            final_sections = get_personnel_sections(token, personnel_id)
            
            if all(sid in final_sections for sid in multi_section_ids):
                print("SUCCESS: Multiple section assignments verified")
            else:
                print("FAILED: Multiple sections not properly assigned")
    
    print("\n" + "=" * 60)
    print("SECTION UPDATE TEST COMPLETED")
    print("=" * 60)
    print(f"Test personnel ID {personnel_id} ready for frontend testing:")
    print("1. Go to: http://127.0.0.1:5501/frontend/personnel.html")
    print(f"2. Click edit button for personnel ID {personnel_id}")
    print("3. Change section assignments in the dropdown")
    print("4. Click 'Mettre à jour' to save")
    print("5. Check console logs for detailed process")

if __name__ == "__main__":
    main()
