import sys
from fastapi.testclient import TestClient

try:
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        print("Verification Successful!")
        sys.exit(0)
    else:
        print("Verification Failed!")
        sys.exit(1)
except Exception as e:
    print(f"Error during verification: {e}")
    sys.exit(1)
