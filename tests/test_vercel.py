import urllib.request
import json

VERCEL_URL = "https://automated-disease-predictor-mvhc.vercel.app"

def test_vercel():
    print(f"Testing Vercel deployment at: {VERCEL_URL}")
    endpoints = [
        "/",
        "/prediction",
        "/symptoms",
        "/prevention",
        "/diseases",
        "/assessment"
    ]
    for ep in endpoints:
        url = VERCEL_URL + ep
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"GET {ep} -> Status: {resp.status}")
        except Exception as e:
            print(f"GET {ep} -> FAILED: {e}")

    # Test online REST predict endpoint
    predict_url = VERCEL_URL + "/predict"
    payload = json.dumps({
        "disease": "symptoms",
        "symptoms": ["high_blood_sugar", "frequent_urination"]
    }).encode('utf-8')
    req = urllib.request.Request(predict_url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("POST /predict -> Status:", resp.status)
            print("Response:", json.dumps(data, indent=2))
            assert data.get('prediction') == 'Diabetes'
            print("-> Vercel online /predict verified SUCCESS!")
    except Exception as e:
        print("POST /predict -> FAILED:", e)

if __name__ == '__main__':
    test_vercel()
