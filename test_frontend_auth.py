import json
import requests

# Base URL for the API
BASE_URL = 'http://localhost:8000'

def test_login():
    """Test login with frontend-compatible format"""
    # The data structure as sent by the frontend
    login_data = {
        'email': 'tester@example.com',  # The user we just created
        'password': 'Test123!'
    }
    
    # Try the simpler login formats
    print("\n=== Testing API Auth Login (Frontend Format) ===")
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        print(f"Token received: {data.get('access', '')[:20]}...")
        return data
    except:
        print(f"Raw response: {response.text}")
        return None

def test_user_profile(token):
    """Test user profile fetch with token"""
    if not token:
        print("No token available, skipping profile test")
        return
        
    headers = {
        'Authorization': f"Bearer {token}"
    }
    
    # Try different user endpoints
    endpoints = [
        '/api/auth/user/',
        '/api/auth/profile/',
        '/accounts/me/',
    ]
    
    for endpoint in endpoints:
        print(f"\n=== Testing {endpoint} ===")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Raw response: {response.text}")

if __name__ == "__main__":
    # Login and get token
    login_response = test_login()
    
    # If login successful, test profile endpoints
    if login_response and 'access' in login_response:
        token = login_response['access']
        test_user_profile(token)
    else:
        print("Login failed, cannot test profile endpoints") 