from fastapi.testclient import TestClient
from backend.main import app
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

client = TestClient(app)

def test_health():
    print("Testing /health...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_history():
    print("\nTesting /history (fetching 1mo for speed)...")
    # We use a short period to avoid timeouts in test
    response = client.get("/history?period=1mo")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"Received {len(data)} records.")
        # Check integrity
        if data:
            print(f"Sample: {data[0]}")
    else:
        print(response.text)
    assert response.status_code == 200

def test_predict():
    print("\nTesting /predict (1 day)...")
    # This might actually invoke the model, ensuring it loads and runs
    response = client.post("/predict", json={"days": 1})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(response.text)
    assert response.status_code == 200

if __name__ == "__main__":
    try:
        test_health()
        test_history()
        test_predict()
        print("\nALL TESTS PASSED ✅")
    except Exception as e:
        print(f"\nTEST FAILED ❌: {e}")
        exit(1)
