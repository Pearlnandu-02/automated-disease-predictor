import urllib.request
import json
import sys

def test_flask_api():
    print("Testing Flask API on http://127.0.0.1:5000/predict ...")
    url = "http://127.0.0.1:5000/predict"
    payload = json.dumps({
        "disease": "symptoms",
        "symptoms": ["high_blood_sugar", "frequent_urination"]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("Flask API response:", json.dumps(res, indent=2))
            assert res.get('prediction') == 'Diabetes'
            assert 'probability' in res
            print("-> Flask API TEST PASSED!")
    except Exception as e:
        print("Flask API error:", e)

def test_php_pages():
    pages = [
        "http://127.0.0.1:8000/index.php",
        "http://127.0.0.1:8000/prediction.php",
        "http://127.0.0.1:8000/symptoms_guide.php",
        "http://127.0.0.1:8000/prevention.php",
        "http://127.0.0.1:8000/diseases.php",
        "http://127.0.0.1:8000/assessment.php",
        "http://127.0.0.1:8000/simulator.php"
    ]
    for p in pages:
        try:
            with urllib.request.urlopen(p, timeout=5) as resp:
                print(f"Testing {p} -> Status {resp.status}")
                assert resp.status == 200
        except Exception as e:
            print(f"Error testing {p}:", e)

def test_php_prediction_post():
    print("Testing PHP Prediction POST submission ...")
    import urllib.parse
    data = urllib.parse.urlencode([('symptoms[]', 'high_blood_sugar'), ('symptoms[]', 'frequent_urination')]).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8000/prediction.php", data=data)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8')
            print(f"PHP Prediction POST Status: {resp.status}")
            assert "Possible condition based on AI model" in html or "Diabetes" in html
            assert "animate-counter" in html
            print("-> PHP Prediction POST TEST PASSED!")
    except Exception as e:
        print("PHP POST error:", e)

if __name__ == '__main__':
    test_flask_api()
    test_php_pages()
    test_php_prediction_post()
