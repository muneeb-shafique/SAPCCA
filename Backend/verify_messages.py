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
    print("=== MESSAGING SYSTEM VERIFICATION ===\n")
    
    print("1. Registering two users...")
    token_a, id_a = register_and_login("Alice")
    token_b, id_b = register_and_login("Bob")
    
    if not token_a or not token_b:
        print("Failed to setup users!")
        return

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    print("2. Making them friends...")
    # Alice sends friend request to Bob
    resp = requests.post(f"{BASE_URL}/friends/request", json={"receiver_id": id_b}, headers=headers_a)
    print(f"   Friend request: {resp.status_code}")
    
    # Bob gets pending requests
    resp = requests.get(f"{BASE_URL}/friends/pending", headers=headers_b)
    requests_list = resp.json().get("requests", [])
    
    if requests_list:
        request_id = requests_list[0]["request_id"]
        # Bob accepts
        resp = requests.post(f"{BASE_URL}/friends/accept", json={"request_id": request_id}, headers=headers_b)
        print(f"   Friend accepted: {resp.status_code}")
    else:
        print("   WARNING: No pending requests found")

    print("\n3. Testing messaging...")
    
    # Alice sends message to Bob
    print("   Alice sending message to Bob...")
    resp = requests.post(f"{BASE_URL}/messages/send", 
                        json={"receiver_id": id_b, "message": "Hello Bob!"},
                        headers=headers_a)
    print(f"   Response: {resp.status_code} - {resp.json()}")
    
    # Bob sends message to Alice
    print("   Bob sending message to Alice...")
    resp = requests.post(f"{BASE_URL}/messages/send",
                        json={"receiver_id": id_a, "message": "Hi Alice!"},
                        headers=headers_b)
    print(f"   Response: {resp.status_code} - {resp.json()}")
    
    # Alice sends another message
    print("   Alice sending another message...")
    resp = requests.post(f"{BASE_URL}/messages/send",
                        json={"receiver_id": id_b, "message": "How are you?"},
                        headers=headers_a)
    print(f"   Response: {resp.status_code} - {resp.json()}")

    print("\n4. Retrieving chat history...")
    
    # Alice gets chat history with Bob
    print("   Alice's view of chat:")
    resp = requests.get(f"{BASE_URL}/messages/chat/{id_b}", headers=headers_a)
    if resp.status_code == 200:
        messages = resp.json().get("messages", [])
        print(f"   Found {len(messages)} messages")
        for msg in messages:
            print(f"      From: {msg['from']} - {msg['text']}")
    else:
        print(f"   ERROR: {resp.status_code} - {resp.text}")
    
    # Bob gets chat history with Alice
    print("\n   Bob's view of chat:")
    resp = requests.get(f"{BASE_URL}/messages/chat/{id_a}", headers=headers_b)
    if resp.status_code == 200:
        messages = resp.json().get("messages", [])
        print(f"   Found {len(messages)} messages")
        for msg in messages:
            print(f"      From: {msg['from']} - {msg['text']}")
        
        if len(messages) == 3:
            print("\n✅ SUCCESS: Messaging system is working correctly!")
        else:
            print(f"\n❌ FAILURE: Expected 3 messages, got {len(messages)}")
    else:
        print(f"   ERROR: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"An error occurred: {e}")
