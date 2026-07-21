import requests
import time
import sys

base_url = "http://localhost:8000/api/v1"

print("Step 1: Logging in...")
login_data = {"email": "admin@example.com", "password": "admin"}
r = requests.post(f"{base_url}/auth/login", json=login_data)
if r.status_code != 200:
    print(f"Login failed: {r.text}")
    sys.exit(1)
token = r.json().get("access_token")
import base64, json
headers = {"Authorization": f"Bearer {token}"}
print("Login successful")

payload = token.split('.')[1]
payload += '=' * (-len(payload) % 4)
user_id = json.loads(base64.b64decode(payload))['sub']

print("\nStep 1b: Fetching categories...")
r = requests.get(f"{base_url}/categories", headers=headers)
categories = r.json() if r.status_code == 200 else []
if not categories:
    print("Creating category...")
    r = requests.post(f"{base_url}/categories", json={"name": "Test Category", "description": "Category for testing"}, headers=headers)
    cat_id = r.json().get("id")
else:
    cat_id = categories[0].get("id")

print("\nStep 2: Creating document record...")
doc_data = {
    "title": "Test Pipeline Document", 
    "description": "Testing the upload pipeline",
    "owner_id": user_id,
    "category_id": cat_id
}
r = requests.post(f"{base_url}/documents", json=doc_data, headers=headers)
if r.status_code != 201:
    print(f"Create doc failed: {r.text}")
    sys.exit(1)
doc_id = r.json().get("id")
print(f"Document created: {doc_id}")

print("\nStep 3: Uploading file...")
files = {'file': ('test.txt', b'This is a test file for the knowledge graph pipeline containing industrial engineering data about pumps.', 'text/plain')}
r = requests.post(f"{base_url}/documents/{doc_id}/upload", files=files, headers=headers)
if r.status_code != 200:
    print(f"Upload failed: {r.text}")
    sys.exit(1)
print("File uploaded successfully")

print("\nStep 4: Monitoring processing status...")
for _ in range(15):
    r = requests.get(f"{base_url}/documents/{doc_id}", headers=headers)
    doc = r.json()
    status = doc.get("status")
    print(f"Current status: {status}")
    if status == "ACTIVE":
        break
    time.sleep(2)

print("\nStep 5: Verifying Graph / Entities / Relationships")
r = requests.get(f"{base_url}/documents/{doc_id}/entities", headers=headers)
entities = r.json() if r.status_code == 200 else []
print(f"Extracted entities: {len(entities)}")

r = requests.get(f"{base_url}/documents/{doc_id}/relationships", headers=headers)
rels = r.json() if r.status_code == 200 else []
print("\nStep 6: Checking jobs table via API...")
r = requests.get(f"{base_url}/admin/jobs", headers=headers)
if r.status_code == 200:
    jobs = r.json().get("items", [])
    doc_jobs = [j for j in jobs if j.get("payload", {}).get("document_id") == doc_id]
    print(f"Jobs found for document {doc_id}: {len(doc_jobs)}")
    for j in jobs:
        print(f"Raw Job ID: {j.get('id')}, Type: {j.get('job_type')}, Status: {j.get('status')}, Payload: {j.get('payload')}, Error: {j.get('error_message')}")
else:
    print(f"Failed to fetch jobs: {r.status_code} {r.text}")

print("\nPipeline check finished.")
