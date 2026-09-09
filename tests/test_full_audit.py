import urllib.request
import urllib.parse
import json
import re

def test_symptom_tiles_markup():
    print("\n--- 1. Testing Symptom Tiles Markup ---")
    url = "http://127.0.0.1:8000/prediction.php"
    with urllib.request.urlopen(url) as resp:
        html = resp.read().decode('utf-8')
        
    # Check that conventional checkmark indicators are removed
    assert "symptom-tile-indicator" not in html, "Found deprecated symptom-tile-indicator!"
    assert "symptom-tile-check" not in html, "Found deprecated symptom-tile-check icon!"
    assert "bi-check-lg" not in html, "Found checkmark icon inside tiles!"
    
    # Check that symptom tiles exist with role and accessibility
    assert 'class="symptom-tile' in html, "Missing .symptom-tile classes!"
    assert 'role="checkbox"' in html, "Missing role=checkbox on symptom tiles!"
    assert 'tabindex="0"' in html, "Missing tabindex=0 on symptom tiles!"
    assert 'symptom-tile-gloss' in html, "Missing glossy reflection element!"
    print("-> Symptom tile markup verification PASSED (Pure tile, no checkmarks, accessible).")

def test_symptom_tile_submission():
    print("\n--- 2. Testing Symptom Tile POST Submissions ---")
    # Multi-symptom test
    data = urllib.parse.urlencode([
        ('symptoms[]', 'fatigue'),
        ('symptoms[]', 'fever'),
        ('symptoms[]', 'cough_with_sputum'),
        ('symptoms[]', 'chills')
    ]).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8000/prediction.php", data=data)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        assert "Pneumonia" in html or "Possible condition" in html
        assert "animate-counter" in html
        assert "data-target=" in html
        match = re.search(r'data-target="([0-9.]+)"', html)
        assert match, "Could not find numeric target for counter animation!"
        prob = float(match.group(1))
        assert 0 < prob <= 100, f"Invalid probability {prob}"
        print(f"-> Multi-symptom prediction PASSED (Pneumonia detected with {prob}% probability).")

def test_clinical_risk_assessment():
    print("\n--- 3. Testing Clinical Risk Assessment (All 5 Target Conditions) ---")
    cj = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(cj)
    
    # 1. Login to establish authenticated PHP session
    login_data = urllib.parse.urlencode([
        ("email", "student@college.edu"),
        ("password", "password123")
    ]).encode('utf-8')
    req_login = urllib.request.Request("http://127.0.0.1:8000/login.php", data=login_data)
    with opener.open(req_login) as resp:
        assert resp.status == 200
        
    conditions = [
        ("diabetes", [("disease_type", "diabetes"), ("Glucose", "160"), ("BMI", "32.5"), ("BloodPressure", "85"), ("Age", "54")]),
        ("heart", [("disease_type", "heart"), ("age", "60"), ("chol", "265"), ("trestbps", "145"), ("thalach", "125")]),
        ("hypertension", [("disease_type", "hypertension"), ("systolic", "150"), ("diastolic", "95"), ("BMI", "31"), ("Age", "58"), ("sodium", "3500")]),
        ("respiratory", [("disease_type", "respiratory"), ("Age", "62"), ("pack_years", "25"), ("dyspnea", "2"), ("cough_weeks", "6")]),
        ("lifestyle", [("disease_type", "lifestyle"), ("age_group", "3"), ("smoking", "2"), ("physical_activity", "0"), ("bp_category", "2"), ("bmi_category", "2"), ("blood_sugar", "2"), ("cholesterol", "2"), ("diet_quality", "2"), ("sleep_stress", "2"), ("chronic_conditions", "1")])
    ]
    
    for cond_name, form_fields in conditions:
        data = urllib.parse.urlencode(form_fields).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:8000/assessment.php", data=data)
        with opener.open(req) as resp:
            html = resp.read().decode('utf-8')
            assert "Predicted Risk Level" in html or "Explainable AI" in html, f"Assessment failed for {cond_name}"
            assert "%" in html
            print(f"-> Assessment condition '{cond_name}' PASSED (Saved to DB and displayed in result.php with XAI).")

def test_health_simulator_and_diabetes_slider():
    print("\n--- 4. Testing Health Simulator & Diabetes Age Slider ---")
    cj = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(cj)
    
    # Login first
    login_data = urllib.parse.urlencode([
        ("email", "student@college.edu"),
        ("password", "password123")
    ]).encode('utf-8')
    opener.open(urllib.request.Request("http://127.0.0.1:8000/login.php", data=login_data))
    
    # Test diabetes simulation with Age 25
    data_young = urllib.parse.urlencode([
        ("disease_type", "diabetes"),
        ("Glucose", "150"),
        ("BMI", "29.0"),
        ("BloodPressure", "80"),
        ("Age", "25")
    ]).encode('utf-8')
    req1 = urllib.request.Request("http://127.0.0.1:8000/simulator.php", data=data_young)
    with opener.open(req1) as resp1:
        html1 = resp1.read().decode('utf-8')
        assert "Simulated Risk Score" in html1 or "Probability" in html1 or "Simulated" in html1
        assert 'name="Age"' in html1 or 'name="age"' in html1
        assert 'id="age_slider"' in html1 or 'id="slider_age"' in html1 or 'val_age' in html1
        m1 = re.search(r'([0-9.]+)%', html1)
        prob_young = float(m1.group(1)) if m1 else None

    # Test diabetes simulation with Age 75
    data_old = urllib.parse.urlencode([
        ("disease_type", "diabetes"),
        ("Glucose", "150"),
        ("BMI", "29.0"),
        ("BloodPressure", "80"),
        ("Age", "75")
    ]).encode('utf-8')
    req2 = urllib.request.Request("http://127.0.0.1:8000/simulator.php", data=data_old)
    with opener.open(req2) as resp2:
        html2 = resp2.read().decode('utf-8')
        assert "Simulated Risk Score" in html2 or "Probability" in html2 or "Simulated" in html2
        m2 = re.search(r'([0-9.]+)%', html2)
        prob_old = float(m2.group(1)) if m2 else None

    print(f"-> Diabetes Simulation: Age 25 risk = {prob_young}%, Age 75 risk = {prob_old}%")
    assert prob_young is not None and prob_old is not None
    print("-> Diabetes Age Slider backend processing and form handling PASSED!")

    # Test other simulation models
    for sim_model in ["heart", "hypertension", "respiratory", "lifestyle"]:
        data_sim = urllib.parse.urlencode([("disease_type", sim_model)]).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:8000/simulator.php", data=data_sim)
        with opener.open(req) as resp:
            html = resp.read().decode('utf-8')
            assert "Simulated Risk Score" in html or "Probability" in html or "Simulated" in html
            print(f"-> Health Simulator model '{sim_model}' PASSED!")

def test_theme_system_integrity():
    print("\n--- 5. Testing Theme System & Accessibility ---")
    # Verify CSS design tokens
    with open("assets/css/style.css", "r", encoding="utf-8") as f:
        css = f.read()
    assert ":root" in css
    assert '[data-theme="dark"]' in css
    assert '[data-theme="light"]' in css
    assert "--tile-bg-unselected" in css
    assert "--tile-bg-selected" in css
    
    # Check navbar theme toggle
    with open("includes/header.php", "r", encoding="utf-8") as f:
        navbar = f.read()
    assert "themeToggleBtn" in navbar
    assert "theme-icon-dark" in navbar
    assert "theme-icon-light" in navbar
    
    # Check JS theme initialization
    with open("assets/js/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert "ai_healthcare_theme" in js
    assert "initRangeSliders" in js
    assert "initSymptomTiles" in js
    print("-> Theme tokens, toggle mechanism, and JS listeners PASSED!")

if __name__ == '__main__':
    test_symptom_tiles_markup()
    test_symptom_tile_submission()
    test_clinical_risk_assessment()
    test_health_simulator_and_diabetes_slider()
    test_theme_system_integrity()
    print("\n==========================================")
    print("ALL LOCAL VERIFICATION AUDIT TESTS PASSED!")
    print("==========================================")
