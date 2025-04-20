import requests
import json

# Base URL
BASE_URL = 'http://localhost:8000'

# Test basic login
login_data = {
    'email': 'tester@example.com',
    'password': 'Test123!'
}

print(f"Attempting login with {login_data}")

# Try all possible login endpoints
endpoints = [
    '/api/auth/login/',
    '/accounts/login/',
    '/auth/login/',
]

for endpoint in endpoints:
    full_url = f"{BASE_URL}{endpoint}"
    print(f"\nTrying endpoint: {full_url}")
    try:
        response = requests.post(full_url, json=login_data, timeout=5)
        print(f"Status code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Raw response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {full_url}: {e}") 