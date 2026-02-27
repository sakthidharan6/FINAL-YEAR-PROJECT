import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_live_api():
    print(f"Checking API at {BASE_URL}...")
    
    # 1. Health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"/health: {resp.status_code} - {resp.text}")
        if resp.status_code != 200:
            print("Health check failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Health check error: {e}")
        sys.exit(1)

    # 2. History
    try:
        resp = requests.get(f"{BASE_URL}/history?period=1mo")
        print(f"/history: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"  Got {len(data)} records.")
        else:
            print(f"  Error: {resp.text}")
    except Exception as e:
        print(f"History check error: {e}")

    # 3. Predict
    try:
        resp = requests.post(f"{BASE_URL}/predict", json={"days": 3})
        print(f"/predict: {resp.status_code}")
        if resp.status_code == 200:
            res = resp.json()
            res = resp.json()
            print(f"  Predictions: {res['predictions']}")
            print(f"  Dates: {res['dates']}")
            
            if 'metrics' in res:
                m = res['metrics']
                print(f"  Metrics found: RMSE={m.get('RMSE')}, MAE={m.get('MAE')}, R2={m.get('R2')}")
            else:
                print("  WARNING: 'metrics' key missing in response!")
        else:
            print(f"  Error: {resp.text}")
    except Exception as e:
        print(f"Prediction check error: {e}")

if __name__ == "__main__":
    test_live_api()
