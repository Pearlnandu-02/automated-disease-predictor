import urllib.request
import urllib.parse

pages = [
    "http://127.0.0.1:8000/index.php",
    "http://127.0.0.1:8000/prediction.php",
    "http://127.0.0.1:8000/image_scanner.php",
    "http://127.0.0.1:8000/symptoms_guide.php",
    "http://127.0.0.1:8000/prevention.php",
    "http://127.0.0.1:8000/diseases.php",
    "http://127.0.0.1:8000/disease_detail.php?id=1",
    "http://127.0.0.1:8000/disease_detail.php?id=3",
    "http://127.0.0.1:8000/assessment.php",
    "http://127.0.0.1:8000/simulator.php",
    "http://127.0.0.1:8000/dataset_info.php",
    "http://127.0.0.1:8000/project_info.php",
    "http://127.0.0.1:8000/contact.php",
    "http://127.0.0.1:8000/login.php",
    "http://127.0.0.1:8000/register.php"
]

cj = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cj)

# Login
login_data = urllib.parse.urlencode([
    ("email", "student@college.edu"),
    ("password", "password123")
]).encode('utf-8')
opener.open(urllib.request.Request("http://127.0.0.1:8000/login.php", data=login_data))

# Authenticated pages
auth_pages = [
    "http://127.0.0.1:8000/dashboard.php",
    "http://127.0.0.1:8000/assessment.php",
    "http://127.0.0.1:8000/simulator.php"
]

print("--- Testing All Site Pages ---")
for p in pages:
    with opener.open(p) as resp:
        content = resp.read().decode('utf-8')
        assert resp.status == 200, f"Page {p} returned {resp.status}"
        assert "Fatal error" not in content, f"Fatal error on {p}"
        assert "Parse error" not in content, f"Parse error on {p}"
        print(f"[OK] {p} (HTTP 200, clean render)")

for p in auth_pages:
    with opener.open(p) as resp:
        content = resp.read().decode('utf-8')
        assert resp.status == 200, f"Page {p} returned {resp.status}"
        assert "Fatal error" not in content, f"Fatal error on {p}"
        print(f"[OK AUTH] {p} (HTTP 200, clean render)")

print("\nAll pages verified successfully!")
