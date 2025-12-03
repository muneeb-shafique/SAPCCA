import requests
import time
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
        return None, None

    # Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Failed to login {name}: {resp.text}")
        return None, None
        
    data = resp.json()
    return data["token"], data["user"]["id"]

def run_test():
    print("1. Registering users...")
    token_a, id_a = register_and_login("UserA")
    token_b, id_b = register_and_login("UserB")
    
    if not token_a or not token_b:
        return

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("2. User A sending friend request to User B...")
    resp = requests.post(f"{BASE_URL}/friends/request", json={"receiver_id": id_b}, headers=headers_a)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("3. User B checking pending requests...")
    resp = requests.get(f"{BASE_URL}/friends/pending", headers=headers_b)
    requests_list = resp.json().get("requests", [])
    print(f"   Pending requests: {requests_list}")
    
    if not requests_list:
        print("   No pending requests found!")
        return

    request_id = requests_list[0]["request_id"]

    print(f"4. User B accepting request {request_id}...")
    resp = requests.post(f"{BASE_URL}/friends/accept", json={"request_id": request_id}, headers=headers_b)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("5. User A checking friends list...")
    resp = requests.get(f"{BASE_URL}/friends/list", headers=headers_a)
    friends_a = resp.json()
    print(f"   User A friends: {friends_a}")
    
    print("6. User B checking friends list...")
    resp = requests.get(f"{BASE_URL}/friends/list", headers=headers_b)
    friends_b = resp.json()
    print(f"   User B friends: {friends_b}")

    # Verification
    found_b_in_a = any(f["id"] == id_b for f in friends_a)
    found_a_in_b = any(f["id"] == id_a for f in friends_b)

    if found_b_in_a and found_a_in_b:
        print("\nSUCCESS: Friends list endpoint is working correctly!")
    else:
        print("\nFAILURE: Friends list verification failed.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"An error occurred: {e}")
