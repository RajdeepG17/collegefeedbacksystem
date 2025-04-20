import json
import requests

# Base URL for the API
BASE_URL = 'http://localhost:8000'

def test_registration():
    """Test user registration"""
    # Data for non-student user (to avoid student-specific validations)
    user_data = {
        'email': 'tester@example.com',
        'password': 'Test123!',
        'password2': 'Test123!',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'teacher',  # Using teacher instead of student to avoid extra validation
    }
    
    # Try the accounts registration endpoint directly
    print("\n=== Trying /accounts/register/ endpoint ===")
    response = requests.post(f"{BASE_URL}/accounts/register/", json=user_data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw response: {response.text}")
    
    # Try auth registration endpoint
    print("\n=== Trying /api/auth/register/ endpoint ===")
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw response: {response.text}")

def test_login(email, password):
    """Test user login"""
    login_data = {
        'email': email,
        'password': password
    }
    
    # Try accounts login endpoint
    print("\n=== Trying /accounts/login/ endpoint ===")
    response = requests.post(f"{BASE_URL}/accounts/login/", json=login_data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw response: {response.text}")
    
    # Try auth login endpoint
    print("\n=== Trying /api/auth/login/ endpoint ===")
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    # First try with existing users
    print("=== Testing login with existing user ===")
    test_login('student@example.com', 'student123')
    
    # Then try registration
    print("\n=== Testing new user registration ===")
    test_registration()
    
    # Finally try login with the new user
    print("\n=== Testing login with new user ===")
    test_login('tester@example.com', 'Test123!') 