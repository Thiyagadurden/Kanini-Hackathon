import requests
import sys

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

def check_frontend():
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print(f"[SUCCESS] Frontend is reachable at {FRONTEND_URL}")
        else:
            print(f"[WARNING] Frontend returned status code {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Frontend check failed: {e}")

def check_backend():
    users = [
        ("patient@example.com", "Patient"),
        ("nurse@example.com", "Nurse"),
        ("doctor@example.com", "Doctor"),
        ("management@example.com", "Management"),
        ("admin@example.com", "Admin")
    ]
    
    for email, role in users:
        try:
            print(f"\nChecking login for {role} ({email})...")
            login_url = f"{BACKEND_URL}/api/auth/token/"
            data = {
                "email": email,
                "password": "password123"
            }
            response = requests.post(login_url, json=data)
            
            if response.status_code == 200:
                print(f"[SUCCESS] Login successful for {role}")
                token = response.json().get('access')
                if token:
                    print(f"[SUCCESS] Received access token for {role}")
                else:
                    print(f"[WARNING] No token received for {role}")
            else:
                print(f"[ERROR] Login failed for {role}: {response.status_code}")
                # print(response.text) # Uncomment for debug
        except Exception as e:
            print(f"[ERROR] Exception checking {role}: {e}")

if __name__ == "__main__":
    print("Verifying services...")
    check_frontend()
    check_backend()
