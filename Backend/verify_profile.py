import requests
import uuid

BASE_URL = "http://127.0.0.1:5000/api"

def register_and_login(name):
    email = f"{name.lower()}_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # Register
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    if resp.status_code != 200:
        print(f"Failed to register {name}: {resp.text}")
        return None

    # Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Failed to login {name}: {resp.text}")
        return None
        
    data = resp.json()
    return data["token"]

def run_test():
    print("=== PROFILE MANAGEMENT VERIFICATION ===\n")
    
    print("1. Registering and logging in user...")
    token = register_and_login("TestUser")
    
    if not token:
        print("Failed to setup user!")
        return

    headers = {"Authorization": f"Bearer {token}"}

    print("\n2. Getting profile...")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    print(f"   Response: {resp.status_code}")
    if resp.status_code == 200:
        profile = resp.json()
        print(f"   Name: {profile.get('name')}")
        print(f"   Email: {profile.get('email')}")
        print(f"   Avatar: {profile.get('avatar')}")
        original_name = profile.get('name')
    else:
        print(f"   ERROR: {resp.text}")
        return

    print("\n3. Updating profile (name only)...")
    resp = requests.post(f"{BASE_URL}/profile/update", 
                        json={"name": "Updated Name"},
                        headers=headers)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("\n4. Getting profile again to verify name update...")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    if resp.status_code == 200:
        profile = resp.json()
        print(f"   Name: {profile.get('name')}")
        if profile.get('name') == "Updated Name":
            print("   ✓ Name updated successfully!")
        else:
            print("   ✗ Name update failed!")
            return
    else:
        print(f"   ERROR: {resp.text}")
        return

    print("\n5. Updating profile (avatar only)...")
    resp = requests.post(f"{BASE_URL}/profile/update",
                        json={"avatar": "https://example.com/new-avatar.jpg"},
                        headers=headers)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("\n6. Getting profile again to verify avatar update...")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    if resp.status_code == 200:
        profile = resp.json()
        print(f"   Avatar: {profile.get('avatar')}")
        if profile.get('avatar') == "https://example.com/new-avatar.jpg":
            print("   ✓ Avatar updated successfully!")
        else:
            print("   ✗ Avatar update failed!")
            return
    else:
        print(f"   ERROR: {resp.text}")
        return

    print("\n7. Updating both name and avatar...")
    resp = requests.post(f"{BASE_URL}/profile/update",
                        json={
                            "name": "Final Name",
                            "avatar": "https://example.com/final-avatar.jpg"
                        },
                        headers=headers)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("\n8. Final profile check...")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    if resp.status_code == 200:
        profile = resp.json()
        print(f"   Name: {profile.get('name')}")
        print(f"   Avatar: {profile.get('avatar')}")
        
        if (profile.get('name') == "Final Name" and 
            profile.get('avatar') == "https://example.com/final-avatar.jpg"):
            print("\nSUCCESS: Profile management is working correctly!")
        else:
            print("\nFAILURE: Profile update verification failed")
    else:
        print(f"   ERROR: {resp.text}")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"An error occurred: {e}")
