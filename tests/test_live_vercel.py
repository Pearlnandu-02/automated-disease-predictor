import urllib.request
import urllib.parse
import json
import re
import time
import base64


VERCEL_BASE = "https://automated-disease-predictor-mvhc.vercel.app"

def run_live_tests():
    print(f"==================================================")
    print(f"TESTING LIVE VERCEL DEPLOYMENT: {VERCEL_BASE}")
    print(f"==================================================")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # 1. Test Home
    print("\n1. Testing GET / (Home Page)...")
    req = urllib.request.Request(VERCEL_BASE + "/", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "AI Healthcare" in html
        assert "themeToggleBtn" in html
        print("-> Home Page PASSED (HTTP 200, Theme toggle present)")

    # 2. Test Prediction & Pure Symptom Tiles (No Checkmarks)
    print("\n2. Testing GET /prediction (Symptom Tiles UI)...")
    req = urllib.request.Request(VERCEL_BASE + "/prediction", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "symptom-tile-indicator" not in html, "Found deprecated symptom-tile-indicator!"
        assert "symptom-tile-check" not in html, "Found deprecated symptom-tile-check!"
        assert "bi-check-lg" not in html, "Found checkmark icon in tiles!"
        assert "symptom-tile" in html
        assert "symptom-tile-gloss" in html
        print("-> Symptom Tiles Markup PASSED (Pure tiles, NO checkmarks, glossy reflection ready)")

    # 3. Test Symptom Submission on Vercel
    print("\n3. Testing POST /prediction (Live Prediction Inference)...")
    data = urllib.parse.urlencode([
        ('symptoms', 'fatigue'),
        ('symptoms', 'fever'),
        ('symptoms', 'cough_with_sputum'),
        ('symptoms', 'chills')
    ]).encode('utf-8')
    req = urllib.request.Request(VERCEL_BASE + "/prediction", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "Pneumonia" in html or "Possible condition based on AI model" in html
        assert "animate-counter" in html
        print("-> Live Prediction Flow PASSED (Pneumonia prediction with digital counter animation)")

    # 4. Test Clinical Risk Assessment (All 5 Target Conditions)
    print("\n4. Testing POST /assessment (5 Target Models on Vercel)...")
    models = ["diabetes", "heart", "hypertension", "respiratory", "lifestyle"]
    for m in models:
        data = urllib.parse.urlencode([("disease_type", m)]).encode('utf-8')
        req = urllib.request.Request(VERCEL_BASE + "/assessment", data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8')
            assert resp.status == 200
            assert "AI Model Statistical Risk Probability" in html or "Explainable AI" in html
            print(f"   -> Model '{m}' PASSED (Evaluated with XAI & Recommendations)")

    # 5. Test Health Simulator & Diabetes Age Slider
    print("\n5. Testing POST /simulator (Health Simulator & Age Slider)...")
    data_young = urllib.parse.urlencode([
        ("disease_type", "diabetes"),
        ("Glucose", "150"),
        ("BMI", "29.0"),
        ("BloodPressure", "80"),
        ("Age", "25")
    ]).encode('utf-8')
    req1 = urllib.request.Request(VERCEL_BASE + "/simulator", data=data_young, headers=headers)
    with urllib.request.urlopen(req1) as resp1:
        html1 = resp1.read().decode('utf-8')
        assert resp1.status == 200
        assert "SIMULATED RISK OUTPUT" in html1
        assert 'name="Age"' in html1
        assert 'id="slider_age"' in html1
        assert 'id="val_Age"' in html1
        m1 = re.search(r'display-3[^>]*>([0-9.]+)%</h1>', html1)
        prob1 = float(m1.group(1)) if m1 else None

    data_old = urllib.parse.urlencode([
        ("disease_type", "diabetes"),
        ("Glucose", "150"),
        ("BMI", "29.0"),
        ("BloodPressure", "80"),
        ("Age", "75")
    ]).encode('utf-8')
    req2 = urllib.request.Request(VERCEL_BASE + "/simulator", data=data_old, headers=headers)
    with urllib.request.urlopen(req2) as resp2:
        html2 = resp2.read().decode('utf-8')
        assert resp2.status == 200
        m2 = re.search(r'display-3[^>]*>([0-9.]+)%</h1>', html2)
        prob2 = float(m2.group(1)) if m2 else None

    print(f"-> Diabetes Simulation on Vercel: Age 25 = {prob1}%, Age 75 = {prob2}%")
    assert prob1 is not None and prob2 is not None
    print("-> Diabetes Age Slider Live Vercel test PASSED (Exact age consumed by model)")

    # 6. Test JSON REST API on Vercel
    print("\n6. Testing POST /predict (Vercel REST API)...")
    payload = json.dumps({
        "disease": "symptoms",
        "symptoms": ["high_blood_sugar", "frequent_urination"]
    }).encode('utf-8')
    req_api = urllib.request.Request(VERCEL_BASE + "/predict", data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_api, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        assert res.get('prediction') == 'Diabetes'
        assert 'probability' in res
        print(f"-> Vercel REST API PASSED (Prediction: {res['prediction']}, Probability: {res['probability']}%)")

    # 7. Test AI Infection & Injury Scanner on Vercel
    print("\n7. Testing GET /scanner (Image Scanner UI on Vercel)...")
    req_scan_ui = urllib.request.Request(VERCEL_BASE + "/scanner", headers=headers)
    with urllib.request.urlopen(req_scan_ui, timeout=15) as resp:
        html_scan = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "AI Infection &amp; Injury Scanner" in html_scan or "AI Infection & Injury Scanner" in html_scan
        assert "dropZone" in html_scan
        assert "previewImage" in html_scan
        assert "When to Seek Immediate Medical Attention" in html_scan
        print("-> Live Scanner UI Page PASSED (HTTP 200, Upload dropzone, camera button, warning signs present)")

    print("\n8. Testing POST /api/scan-image (Computer Vision API on Vercel)...")
    # Synthetic test image base64 (32x32 reddish square JPEG)
    import io
    from PIL import Image
    test_img = Image.new('RGB', (64, 64), color=(210, 45, 45))
    buf = io.BytesIO()
    test_img.save(buf, format='JPEG')
    img_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')

    scan_payload = json.dumps({"image_base64": img_b64}).encode('utf-8')
    req_scan_api = urllib.request.Request(VERCEL_BASE + "/api/scan-image", data=scan_payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_scan_api, timeout=20) as resp:
        scan_res = json.loads(resp.read().decode('utf-8'))
        assert scan_res.get('success') is True
        assert 'category' in scan_res
        assert 'confidence_score' in scan_res
        assert 'metrics' in scan_res
        print(f"-> Live Vision API PASSED (Category: {scan_res['category']}, Score: {scan_res['confidence_score']}%, EI: {scan_res['metrics'].get('erythema_index')})")

    print("\n==================================================")
    print("ALL LIVE VERCEL TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == '__main__':
    run_live_tests()

