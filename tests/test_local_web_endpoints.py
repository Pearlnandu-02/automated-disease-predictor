import requests

BASE_URL = "http://127.0.0.1:8000"

pages_to_test = [
    ("/", "AI Healthcare"),
    ("/index.php", "AI Healthcare"),
    ("/prediction.php", "Symptom"),
    ("/diseases.php", "Diseases"),
    ("/disease_detail.php?id=1", "Diabetes"),
    ("/disease_detail.php?id=26", "Common Cold"),
    ("/disease_detail.php?id=65", "Metabolic"),
    ("/symptoms_guide.php", "Symptom"),
    ("/prevention.php", "Prevention"),
    ("/assessment.php", "Assessment"),
    ("/simulator.php", "Simulator"),
    ("/image_scanner.php", "Scanner"),
    ("/login.php", "Login"),
    ("/register.php", "Register"),
    ("/about.php", "About"),
    ("/project_info.php", "Project"),
]

print("Testing Local PHP Server Endpoints:")
all_passed = True
for path, expected_text in pages_to_test:
    try:
        r = requests.get(BASE_URL + path, timeout=5)
        if r.status_code == 200 and expected_text.lower() in r.text.lower():
            print(f" [PASS] {path} -> HTTP 200 (Contains '{expected_text}')")
        else:
            print(f" [FAIL] {path} -> Status {r.status_code} (Contains '{expected_text}': {expected_text.lower() in r.text.lower()})")
            all_passed = False
    except Exception as e:
        print(f" [ERROR] {path} -> {e}")
        all_passed = False

if all_passed:
    print("\nAll 16 web pages are rendering with HTTP 200 and expected content!")
else:
    print("\nSome endpoints failed.")
