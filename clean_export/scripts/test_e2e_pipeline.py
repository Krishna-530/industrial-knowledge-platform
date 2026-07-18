import httpx
import time
import os

BASE_URL = "http://localhost:8000/api/v1"

def run_tests():
    print("Running E2E Integration Validation...")
    
    # Stage 1: Auth
    print("\n[STAGE 1] Authentication")
    try:
        response = httpx.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "AdminPassword123!"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("  [PASS] Login successful")
        else:
            print(f"  [FAIL] Login failed: {response.text}")
            return
    except Exception as e:
        print(f"  [FAIL] Connection error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Stage 2: Document Upload
    print("\n[STAGE 2] Document Upload")
    try:
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        owner_id = decoded["sub"]

        # Fetch category
        cat_resp = httpx.get(f"{BASE_URL}/categories", headers=headers)
        categories = cat_resp.json()
        if cat_resp.status_code == 200 and len(categories) > 0:
            category_id = categories[0]["id"]
        else:
            # Create a category if missing
            new_cat = httpx.post(f"{BASE_URL}/categories", json={"name": "Test Category"}, headers=headers)
            category_id = new_cat.json()["id"]

        # Create document
        doc_resp = httpx.post(f"{BASE_URL}/documents", json={
            "title": "Test Pump Spec",
            "owner_id": owner_id,
            "category_id": category_id
        }, headers=headers)
        if doc_resp.status_code == 201:
            doc_id = doc_resp.json()["id"]
            print(f"  [PASS] Create document successful. ID: {doc_id}")
            
            # Upload version
            files = {'file': ('test_spec.txt', b'This is an industrial test specification for a pump. It handles high pressure.', 'text/plain')}
            up_resp = httpx.post(f"{BASE_URL}/documents/{doc_id}/upload", files=files, headers=headers)
            if up_resp.status_code == 200:
                print(f"  [PASS] Upload version successful.")
            else:
                print(f"  [FAIL] Upload version failed: {up_resp.text}")
                return
        else:
            print(f"  [FAIL] Create document failed: {doc_resp.text}")
            return
    except Exception as e:
        print(f"  [FAIL] Upload exception: {e}")
        return

    # Stage 3: Processing Pipeline
    print("\n[STAGE 3] Processing Pipeline (Waiting for chunks)")
    time.sleep(2) # Give worker time to poll
    for _ in range(10):
        # We can check dashboard for total_chunks
        try:
            overview = httpx.get(f"{BASE_URL}/dashboard/overview", headers=headers)
            if overview.status_code == 200:
                stats = overview.json()
                if stats["stats"]["total_chunks"] > 0:
                    print("  [PASS] Processing successful (Chunks created)")
                    break
        except:
            pass
        time.sleep(1)
    else:
        print("  [FAIL] Processing failed (No chunks created after 10s)")

    # Stage 7: Dashboard
    print("\n[STAGE 7] Dashboard")
    try:
        overview = httpx.get(f"{BASE_URL}/dashboard/overview", headers=headers)
        if overview.status_code == 200:
            print("  [PASS] Dashboard loaded correctly")
        else:
            print(f"  [FAIL] Dashboard failed: {overview.status_code}")
    except Exception as e:
        print(f"  [FAIL] Dashboard exception: {e}")
        
    print("\nEnd of automated script. See results.")

if __name__ == "__main__":
    run_tests()
