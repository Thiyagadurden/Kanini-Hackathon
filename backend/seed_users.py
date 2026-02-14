import os
import django
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

users_data = [
    {
        "email": "patient@example.com",
        "password": "password123",
        "first_name": "Patient",
        "last_name": "One",
        "role": "patient"
    },
    {
        "email": "nurse@example.com",
        "password": "password123",
        "first_name": "Nurse",
        "last_name": "Joy",
        "role": "nurse"
    },
    {
        "email": "doctor@example.com",
        "password": "password123",
        "first_name": "Doctor",
        "last_name": "Strange",
        "role": "doctor"
    },
    {
        "email": "management@example.com",
        "password": "password123",
        "first_name": "Hospital",
        "last_name": "Manager",
        "role": "management"
    },
    {
        "email": "admin@example.com",
        "password": "password123",
        "first_name": "System",
        "last_name": "Admin",
        "role": "admin",
        "is_superuser": True,
        "is_staff": True
    }
]

def create_users():
    for data in users_data:
        email = data["email"]
        if not User.objects.filter(email=email).exists():
            print(f"Creating user {email}...")
            if data.get("is_superuser"):
                User.objects.create_superuser(
                    email=email,
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    role=data["role"]
                )
            else:
                User.objects.create_user(
                    email=email,
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    role=data["role"]
                )
            print(f"User {email} created successfully.")
        else:
            print(f"User {email} already exists.")

if __name__ == "__main__":
    create_users()
