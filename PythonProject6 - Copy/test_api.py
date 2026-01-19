"""
Comprehensive API Testing Script
Tests all UI functionality against Backend API and Database

Usage:
    python test_api.py
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL for API
BASE_URL = "http://localhost:5000/api"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}

def print_test(name, status, message=""):
    """Print test result."""
    test_results["total"] += 1
    if status:
        test_results["passed"].append(name)
        print(f"✅ PASS: {name}")
        if message:
            print(f"   {message}")
    else:
        test_results["failed"].append(name)
        print(f"❌ FAIL: {name}")
        if message:
            print(f"   {message}")

def test_member_operations():
    """Test all member CRUD operations."""
    print("\n" + "="*60)
    print("TESTING MEMBER OPERATIONS")
    print("="*60)
    
    # Test 1: Create Member
    print("\n1. Testing Create Member...")
    test_member = {
        "id": "999888777",
        "fullname": "Test User",
        "email": "testuser@example.com",
        "phone": "0509998888"
    }
    try:
        response = requests.post(f"{BASE_URL}/members", json=test_member)
        if response.status_code == 201:
            data = response.json()
            print_test("Create Member", True, f"Created member ID: {test_member['id']}")
        else:
            print_test("Create Member", False, f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print_test("Create Member", False, f"Exception: {str(e)}")
    
    # Test 2: Get Member by ID
    print("\n2. Testing Get Member by ID...")
    try:
        response = requests.get(f"{BASE_URL}/members/{test_member['id']}")
        if response.status_code == 200:
            data = response.json()
            if data.get("id") == test_member["id"]:
                print_test("Get Member by ID", True)
            else:
                print_test("Get Member by ID", False, "Member ID mismatch")
        else:
            print_test("Get Member by ID", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Member by ID", False, f"Exception: {str(e)}")
    
    # Test 3: List All Members
    print("\n3. Testing List All Members...")
    try:
        response = requests.get(f"{BASE_URL}/members")
        if response.status_code == 200:
            data = response.json()
            members = data.get("members", [])
            print_test("List All Members", True, f"Found {len(members)} members")
        else:
            print_test("List All Members", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("List All Members", False, f"Exception: {str(e)}")
    
    # Test 4: Update Member
    print("\n4. Testing Update Member...")
    update_data = {
        "fullname": "Updated Test User",
        "email": "updated@example.com"
    }
    try:
        response = requests.put(f"{BASE_URL}/members/{test_member['id']}", json=update_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("fullname") == update_data["fullname"]:
                print_test("Update Member", True)
            else:
                print_test("Update Member", False, "Update not reflected")
        else:
            print_test("Update Member", False, f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print_test("Update Member", False, f"Exception: {str(e)}")
    
    # Test 5: Duplicate ID Check
    print("\n5. Testing Duplicate ID Prevention...")
    try:
        response = requests.post(f"{BASE_URL}/members", json=test_member)
        if response.status_code == 409:  # Conflict
            print_test("Duplicate ID Prevention", True, "Correctly rejected duplicate ID")
        else:
            print_test("Duplicate ID Prevention", False, f"Expected 409, got {response.status_code}")
    except Exception as e:
        print_test("Duplicate ID Prevention", False, f"Exception: {str(e)}")

def test_checkin_operations():
    """Test check-in functionality."""
    print("\n" + "="*60)
    print("TESTING CHECK-IN OPERATIONS")
    print("="*60)
    
    # Use existing member from seed data
    test_member_id = "123456789"
    
    # Test 1: Check-in with valid member
    print("\n1. Testing Check-in...")
    try:
        response = requests.post(f"{BASE_URL}/checkin", json={"member_id": test_member_id})
        data = response.json()
        if response.status_code == 201:
            result = data.get("result", "")
            reason = data.get("reason", "")
            if result in ["APPROVED", "DENIED"]:
                print_test("Check-in Request", True, f"Result: {result}, Reason: {reason}")
            else:
                print_test("Check-in Request", False, f"Invalid result: {result}")
        else:
            print_test("Check-in Request", False, f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print_test("Check-in Request", False, f"Exception: {str(e)}")

def test_subscription_operations():
    """Test subscription operations."""
    print("\n" + "="*60)
    print("TESTING SUBSCRIPTION OPERATIONS")
    print("="*60)
    
    # Test 1: Get Subscription Status
    print("\n1. Testing Get Subscription Status...")
    test_member_id = "123456789"
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/{test_member_id}/status")
        if response.status_code == 200:
            data = response.json()
            print_test("Get Subscription Status", True, f"Status: {data.get('status', 'N/A')}")
        else:
            print_test("Get Subscription Status", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Get Subscription Status", False, f"Exception: {str(e)}")

def test_class_session_operations():
    """Test class session operations."""
    print("\n" + "="*60)
    print("TESTING CLASS SESSION OPERATIONS")
    print("="*60)
    
    # Test 1: List All Sessions
    print("\n1. Testing List All Sessions...")
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", [])
            print_test("List All Sessions", True, f"Found {len(sessions)} sessions")
            if sessions:
                test_session_id = sessions[0].get("id")
                return test_session_id
        else:
            print_test("List All Sessions", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("List All Sessions", False, f"Exception: {str(e)}")
    
    return None

def test_trainer_operations():
    """Test trainer operations."""
    print("\n" + "="*60)
    print("TESTING TRAINER OPERATIONS")
    print("="*60)
    
    # Test 1: List All Trainers
    print("\n1. Testing List All Trainers...")
    try:
        response = requests.get(f"{BASE_URL}/trainers")
        if response.status_code == 200:
            data = response.json()
            trainers = data.get("trainers", [])
            print_test("List All Trainers", True, f"Found {len(trainers)} trainers")
        else:
            print_test("List All Trainers", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("List All Trainers", False, f"Exception: {str(e)}")

def test_validation():
    """Test input validation."""
    print("\n" + "="*60)
    print("TESTING INPUT VALIDATION")
    print("="*60)
    
    # Test 1: Invalid Email Format
    print("\n1. Testing Invalid Email Validation...")
    invalid_member = {
        "id": "111222333",
        "fullname": "Test",
        "email": "invalid-email",  # Invalid email
        "phone": "0501234567"
    }
    try:
        response = requests.post(f"{BASE_URL}/members", json=invalid_member)
        if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
            print_test("Email Validation", True, "Correctly rejected invalid email")
        else:
            print_test("Email Validation", False, f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        print_test("Email Validation", False, f"Exception: {str(e)}")
    
    # Test 2: Invalid Phone Format
    print("\n2. Testing Invalid Phone Validation...")
    invalid_member = {
        "id": "111222334",
        "fullname": "Test",
        "email": "test@example.com",
        "phone": "123"  # Invalid phone
    }
    try:
        response = requests.post(f"{BASE_URL}/members", json=invalid_member)
        if response.status_code in [400, 422]:
            print_test("Phone Validation", True, "Correctly rejected invalid phone")
        else:
            print_test("Phone Validation", False, f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        print_test("Phone Validation", False, f"Exception: {str(e)}")
    
    # Test 3: Invalid ID Format (not 9 digits)
    print("\n3. Testing Invalid ID Validation...")
    invalid_member = {
        "id": "12345",  # Not 9 digits
        "fullname": "Test",
        "email": "test@example.com",
        "phone": "0501234567"
    }
    try:
        response = requests.post(f"{BASE_URL}/members", json=invalid_member)
        if response.status_code in [400, 422]:
            print_test("ID Format Validation", True, "Correctly rejected invalid ID format")
        else:
            print_test("ID Format Validation", False, f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        print_test("ID Format Validation", False, f"Exception: {str(e)}")

def test_error_handling():
    """Test error handling."""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    # Test 1: Get Non-existent Member
    print("\n1. Testing Get Non-existent Member...")
    try:
        response = requests.get(f"{BASE_URL}/members/000000000")
        if response.status_code == 404:
            print_test("404 Not Found Handling", True)
        else:
            print_test("404 Not Found Handling", False, f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_test("404 Not Found Handling", False, f"Exception: {str(e)}")
    
    # Test 2: Update Non-existent Member
    print("\n2. Testing Update Non-existent Member...")
    try:
        response = requests.put(f"{BASE_URL}/members/000000000", json={"fullname": "Test"})
        if response.status_code == 404:
            print_test("Update Non-existent Member", True)
        else:
            print_test("Update Non-existent Member", False, f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_test("Update Non-existent Member", False, f"Exception: {str(e)}")

def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    
    if test_results['failed']:
        print("\nFailed Tests:")
        for test in test_results['failed']:
            print(f"  - {test}")
    
    success_rate = (len(test_results['passed']) / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

def main():
    """Run all tests."""
    print("="*60)
    print("API FUNCTIONALITY TEST SUITE")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/members", timeout=5)
        print("\n✅ Server is running and accessible")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Please make sure the Flask server is running on http://localhost:5000")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return
    
    # Run all test suites
    test_member_operations()
    test_checkin_operations()
    test_subscription_operations()
    test_class_session_operations()
    test_trainer_operations()
    test_validation()
    test_error_handling()
    
    # Print summary
    print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
