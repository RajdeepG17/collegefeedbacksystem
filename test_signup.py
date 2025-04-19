import requests
import json
import traceback
import time

def test_signup():
    timestamp = int(time.time())
    url = "http://localhost:8000/api/auth/register/"
    data = {
        "email": f"test.student{timestamp}@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "student",
        "student_id": "AB123456",
        "department": "Computer Science",
        "year_of_study": 2
    }
    
    try:
        print("Sending registration request with data:", json.dumps(data, indent=2))
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        try:
            print("Response:", json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print("Response:", response.text)
            
        print("\nHeaders:", dict(response.headers))
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_signup() 