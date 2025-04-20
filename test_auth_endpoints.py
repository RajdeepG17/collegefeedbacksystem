import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    print("\n=== Testing Login ===")
    login_data = {
        "email": "student@example.com", 
        "password": "student123"
    }
    
    # Try /api/auth/login/ endpoint
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"POST {BASE_URL}/auth/login/ - Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Success! Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error! Response: {response.text}")
    
    # Also try with username instead of email
    login_data_alt = {
        "username": "student@example.com", 
        "password": "student123"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data_alt)
    print(f"POST {BASE_URL}/auth/login/ with username - Status Code: {response.status_code}")
    
    # Try accounts login endpoint
    response = requests.post(f"{BASE_URL}/../accounts/login/", json=login_data)
    print(f"POST {BASE_URL}/../accounts/login/ - Status Code: {response.status_code}")
    

def test_register():
    print("\n=== Testing Registration ===")
    register_data = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "password2": "Password123!",  # Some APIs require password confirmation
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Try /api/auth/register/ endpoint
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"POST {BASE_URL}/auth/register/ - Status Code: {response.status_code}")
    if response.status_code == 201:
        print(f"Success! Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error! Response: {response.text}")
    
    # Try accounts register endpoint
    response = requests.post(f"{BASE_URL}/../accounts/register/", json=register_data)
    print(f"POST {BASE_URL}/../accounts/register/ - Status Code: {response.status_code}")

if __name__ == "__main__":
    test_login()
    test_register() 