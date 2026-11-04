import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:8080"

print("--- 1. Testing Sensitive File Protection (Vulnerability 1) ---")
for forbidden_path in ["/.env", "/.git/config", "/backend/server.py", "/docker-compose.yml"]:
    try:
        req = urllib.request.Request(f"{base_url}{forbidden_path}")
        with urllib.request.urlopen(req) as resp:
            print(f"[FAIL] {forbidden_path} returned {resp.status} (Expected 404)")
    except urllib.error.HTTPError as e:
        print(f"[PASS] {forbidden_path} correctly blocked with HTTP {e.code}")

print("\n--- 2. Testing Allowed Static Asset ---")
try:
    with urllib.request.urlopen(f"{base_url}/portal.html") as resp:
        print(f"[PASS] /portal.html accessible with HTTP {resp.status}")
except Exception as e:
    print(f"[FAIL] /portal.html inaccessible: {e}")

print("\n--- 3. Testing Unauthenticated Administrative API Call (Vulnerability 2) ---")
try:
    payload = json.dumps({"action": "adjustStock", "itemId": 1, "new_quantity": 50, "reason": "unauth_test"}).encode()
    req = urllib.request.Request(f"{base_url}/api", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        print(f"[FAIL] adjustStock executed without auth! HTTP {resp.status}")
except urllib.error.HTTPError as e:
    print(f"[PASS] adjustStock rejected with HTTP {e.code} ({e.reason})")

print("\n--- 4. Testing Staff Login and Token Generation ---")
token = None
try:
    login_payload = json.dumps({"action": "loginStaff", "username": "admin_staff", "password": "••••••••"}).encode()
    req = urllib.request.Request(f"{base_url}/api", data=login_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        if data.get("status") == "success" and data.get("token"):
            token = data["token"]
            print(f"[PASS] loginStaff success! Received signed token: {token[:25]}...")
        else:
            print(f"[FAIL] loginStaff failed: {data}")
except Exception as e:
    print(f"[FAIL] loginStaff exception: {e}")

print("\n--- 5. Testing Authorized Administrative API with Bearer Token ---")
if token:
    try:
        auth_payload = json.dumps({"action": "adjustStock", "itemId": 1, "new_quantity": 50, "reason": "authorized_test"}).encode()
        req = urllib.request.Request(
            f"{base_url}/api",
            data=auth_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[PASS] adjustStock with Bearer token executed successfully: HTTP {resp.status}")
    except Exception as e:
        print(f"[FAIL] Authorized adjustStock failed: {e}")

print("\n--- 6. Testing CORS Policy ---")
try:
    req = urllib.request.Request(f"{base_url}/portal.html", headers={"Origin": "https://malicious-attacker.com"})
    with urllib.request.urlopen(req) as resp:
        cors_header = resp.headers.get("Access-Control-Allow-Origin")
        if cors_header == "*":
            print(f"[FAIL] Wildcard CORS still present!")
        elif cors_header is None:
            print(f"[PASS] Untrusted origin does not receive Access-Control-Allow-Origin header.")
        else:
            print(f"[INFO] CORS header: {cors_header}")
except Exception as e:
    print(f"CORS test exception: {e}")

