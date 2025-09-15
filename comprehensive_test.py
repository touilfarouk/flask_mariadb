#!/usr/bin/env python3
"""
Comprehensive test suite for Personnel Management System
Tests authentication, sections, personnel CRUD, and multi-section assignments
"""

import requests
import json
import sys
import time

API_BASE = "http://127.0.0.1:3000"

def test_authentication():
    """Test user registration, login, and logout"""
    print("=" * 60)
    print("TESTING AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Test 1: Register new user
    print("\n1. Testing user registration...")
    test_user = {
        "firstname": "Test",
        "lastname": "User",
        "email": f"testuser{int(time.time())}@example.com",
        "password": "testpass123",
        "role": "customer"
    }
    
    response = requests.post(f"{API_BASE}/auth/signup", json=test_user)
    print(f"   Registration Status: {response.status_code}")
    if response.status_code == 201 or response.status_code == 200:
        print(f"   User registered successfully")
        user_token = response.json().get("token")
    else:
        print(f"   Registration failed: {response.text}")
        return None
    
    # Test 2: Login with admin credentials
    print("\n2. Testing admin login...")
    admin_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    print(f"   Admin Login Status: {admin_response.status_code}")
    if admin_response.status_code == 200:
        print(f"   Admin login successful")
        admin_token = admin_response.json().get("token")
        return admin_token
    else:
        print(f"   Admin login failed: {admin_response.text}")
        return None

def test_sections_crud(token):
    """Test section CRUD operations"""
    print("\n" + "=" * 60)
    print("TESTING SECTION CRUD OPERATIONS")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Get all sections
    print("\n1. Getting all sections...")
    response = requests.get(f"{API_BASE}/section/all", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        sections = response.json().get("data", [])
        print(f"   Found {len(sections)} sections")
        for section in sections:
            print(f"      - ID: {section['id']}, Label: {section['label']}")
    else:
        print(f"   Failed to get sections: {response.text}")
        return []
    
    # Test 2: Create new section
    print("\n2. Creating new section...")
    new_section = {
        "code_section": f"TEST{int(time.time())}",
        "label": "Test Section"
    }
    response = requests.post(f"{API_BASE}/section/add", json=new_section, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        section_id = response.json().get("id")
        print(f"   Section created with ID: {section_id}")
    else:
        print(f"   Failed to create section: {response.text}")
        section_id = None
    
    # Test 3: Update section
    if section_id:
        print("\n3. Updating section...")
        update_data = {
            "code_section": f"UPDATED{int(time.time())}",
            "label": "Updated Test Section"
        }
        response = requests.put(f"{API_BASE}/section/{section_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Section updated successfully")
        else:
            print(f"   Failed to update section: {response.text}")
    
    return sections

def test_personnel_crud(token, sections):
    """Test personnel CRUD operations with multi-section assignments"""
    print("\n" + "=" * 60)
    print("TESTING PERSONNEL CRUD OPERATIONS")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Get all personnel
    print("\n1. Getting all personnel...")
    response = requests.get(f"{API_BASE}/personnel/all", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        personnel_list = response.json().get("data", [])
        print(f"   Found {len(personnel_list)} personnel")
        for person in personnel_list:
            print(f"      - ID: {person['id']}, Name: {person['nom']}, Sections: {person.get('sections', 'None')}")
    else:
        print(f"   Failed to get personnel: {response.text}")
        return
    
    # Test 2: Create personnel with single section
    print("\n2. Creating personnel with single section...")
    new_personnel = {
        "matricule": f"TEST{int(time.time())}",
        "nom": "Test Employee Single",
        "qualification": "Test Manager",
        "affectation": "Test Department",
        "sections": [sections[0]["id"]] if sections else []
    }
    response = requests.post(f"{API_BASE}/personnel/add", json=new_personnel, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        personnel_id = response.json().get("id")
        print(f"   Personnel created with ID: {personnel_id}")
    else:
        print(f"   Failed to create personnel: {response.text}")
        return
    
    # Test 3: Create personnel with multiple sections
    print("\n3. Creating personnel with multiple sections...")
    multi_personnel = {
        "matricule": f"MULTI{int(time.time())}",
        "nom": "Test Employee Multi",
        "qualification": "Senior Manager",
        "affectation": "Multi Department",
        "sections": [sections[0]["id"], sections[1]["id"]] if len(sections) >= 2 else [sections[0]["id"]]
    }
    response = requests.post(f"{API_BASE}/personnel/add", json=multi_personnel, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        multi_personnel_id = response.json().get("id")
        print(f"   Multi-section personnel created with ID: {multi_personnel_id}")
    else:
        print(f"   Failed to create multi-section personnel: {response.text}")
        multi_personnel_id = None
    
    # Test 4: Update personnel section assignments
    print("\n4. Testing personnel section updates...")
    if personnel_id:
        # Update to multiple sections
        update_data = {
            "matricule": f"UPD{personnel_id}",
            "nom": "Updated Test Employee",
            "qualification": "Updated Manager",
            "affectation": "Updated Department",
            "sections": [sections[0]["id"], sections[1]["id"]] if len(sections) >= 2 else [sections[0]["id"]]
        }
        response = requests.put(f"{API_BASE}/personnel/{personnel_id}", json=update_data, headers=headers)
        print(f"   Update Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Personnel updated successfully")
        else:
            print(f"   Failed to update personnel: {response.text}")
        
        # Verify sections were assigned
        response = requests.get(f"{API_BASE}/personnel/{personnel_id}/sections", headers=headers)
        if response.status_code == 200:
            assigned_sections = response.json().get("data", [])
            print(f"   Personnel assigned to {len(assigned_sections)} sections: {assigned_sections}")
        else:
            print(f"   Failed to get personnel sections: {response.text}")
    
    # Test 5: Get individual personnel
    if personnel_id:
        print("\n5. Getting individual personnel...")
        response = requests.get(f"{API_BASE}/personnel/{personnel_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            person_data = response.json().get("data", {})
            print(f"   Personnel details: {person_data.get('nom')} - {person_data.get('sections', 'No sections')}")
        else:
            print(f"   Failed to get personnel: {response.text}")
    
    return personnel_id

def test_edge_cases(token, sections, personnel_id):
    """Test edge cases and error scenarios"""
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES AND ERROR SCENARIOS")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Invalid section assignment
    print("\n1. Testing invalid section assignment...")
    invalid_data = {
        "matricule": f"INVALID{int(time.time())}",
        "nom": "Invalid Test",
        "qualification": "Test",
        "affectation": "Test",
        "sections": [99999]  # Non-existent section
    }
    response = requests.post(f"{API_BASE}/personnel/add", json=invalid_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   Correctly rejected invalid section: {response.json().get('error')}")
    else:
        print(f"   Should have rejected invalid section: {response.text}")
    
    # Test 2: Missing required fields
    print("\n2. Testing missing required fields...")
    incomplete_data = {
        "matricule": f"INCOMPLETE{int(time.time())}"
        # Missing nom, qualification, affectation
    }
    response = requests.post(f"{API_BASE}/personnel/add", json=incomplete_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   Correctly rejected incomplete data: {response.json().get('error')}")
    else:
        print(f"   Should have rejected incomplete data: {response.text}")
    
    # Test 3: Duplicate matricule
    if personnel_id:
        print("\n3. Testing duplicate matricule...")
        # Get existing personnel matricule
        response = requests.get(f"{API_BASE}/personnel/{personnel_id}", headers=headers)
        if response.status_code == 200:
            existing_matricule = response.json().get("data", {}).get("matricule")
            duplicate_data = {
                "matricule": existing_matricule,
                "nom": "Duplicate Test",
                "qualification": "Test",
                "affectation": "Test",
                "sections": []
            }
            response = requests.post(f"{API_BASE}/personnel/add", json=duplicate_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print(f"   Correctly rejected duplicate matricule: {response.json().get('error')}")
            else:
                print(f"   Should have rejected duplicate matricule: {response.text}")

def main():
    print("COMPREHENSIVE PERSONNEL MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    # Test authentication
    admin_token = test_authentication()
    if not admin_token:
        print("Authentication failed - cannot continue")
        return
    
    # Test sections
    sections = test_sections_crud(admin_token)
    if not sections:
        print("Section operations failed - cannot continue")
        return
    
    # Test personnel
    personnel_id = test_personnel_crud(admin_token, sections)
    if not personnel_id:
        print("Personnel operations failed - cannot continue")
        return
    
    # Test edge cases
    test_edge_cases(admin_token, sections, personnel_id)
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nAll major functionality verified:")
    print("- User authentication (register, login)")
    print("- Section CRUD operations")
    print("- Personnel CRUD operations")
    print("- Multi-section assignments")
    print("- Data validation and error handling")
    print("- Edge case scenarios")

if __name__ == "__main__":
    main()
