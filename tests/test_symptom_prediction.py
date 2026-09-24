"""
tests/test_symptom_prediction.py
Automated verification test suite for MediSense AI Symptom-Based Disease Prediction Engine.
Validates the 8 core clinical presentation test cases, deterministic explainability,
multi-condition differential ranking, insufficient information gates, and graceful fallbacks.
"""

import os
import sys
import json
import subprocess

PHP_BINARY = r"C:\xampp\php\php.exe"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_php_symptom_matching(symptoms, context=None):
    """Executes SymptomPredictionService::matchSymptoms via PHP CLI and returns the parsed JSON."""
    if context is None:
        context = {}
    
    script = f"""
    require_once '{REPO_ROOT.replace('\\', '/')}/services/symptom_prediction.php';
    $symptoms = json_decode('{json.dumps(symptoms)}', true);
    $context = json_decode('{json.dumps(context)}', true);
    $result = SymptomPredictionService::matchSymptoms($symptoms, $context);
    echo json_encode($result);
    """
    
    proc = subprocess.run(
        [PHP_BINARY, "-r", script],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    if proc.returncode != 0:
        raise RuntimeError(f"PHP execution failed: {proc.stderr}")
    
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse PHP output: '{proc.stdout}' - Error: {e}")


def run_php_normalize(query):
    """Executes SymptomPredictionService::normalizeQuery via PHP CLI."""
    script = f"""
    require_once '{REPO_ROOT.replace('\\', '/')}/services/symptom_prediction.php';
    $res = SymptomPredictionService::normalizeQuery('{query}');
    echo json_encode(['normalized' => $res]);
    """
    proc = subprocess.run(
        [PHP_BINARY, "-r", script],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout).get('normalized')
    except Exception:
        return None


def test_suite():
    print("=" * 70)
    print(" MediSense AI - Symptom Prediction Automated Test Suite")
    print("=" * 70)

    test_cases = [
        {
            "id": "TEST 1",
            "name": "Respiratory Presentation: Fever + Cough + Fatigue",
            "symptoms": ["fever", "cough", "fatigue"],
            "expected_in_top": ["COVID-19", "Bronchitis", "Pneumonia", "Influenza"],
            "expect_status": "success",
            "min_score": 50
        },
        {
            "id": "TEST 2",
            "name": "Neurological / Systemic Presentation: Headache + Nausea + Dizziness",
            "symptoms": ["headache", "nausea", "dizziness"],
            "expected_in_top": ["Migraine", "Dehydration", "Concussion", "Tension Headache"],
            "expect_status": "success",
            "min_score": 50
        },
        {
            "id": "TEST 3",
            "name": "Gastrointestinal Presentation: Abdominal pain + Diarrhea + Vomiting",
            "symptoms": ["abdominal_pain", "diarrhea", "vomiting"],
            "expected_in_top": ["Gastroenteritis", "Food Poisoning", "Irritable Bowel Syndrome (IBS)"],
            "expect_status": "success",
            "min_score": 50
        },
        {
            "id": "TEST 4",
            "name": "Upper Respiratory Presentation: Sneezing + Runny nose + Sore throat",
            "symptoms": ["sneezing", "runny_nose", "sore_throat"],
            "expected_in_top": ["Common Cold", "Allergic Rhinitis", "Viral Pharyngitis"],
            "expect_status": "success",
            "min_score": 50
        },
        {
            "id": "TEST 5",
            "name": "Endocrine Presentation: Fatigue + Cold intolerance + Weight gain",
            "symptoms": ["fatigue", "cold_intolerance", "weight_gain"],
            "expected_in_top": ["Hypothyroidism"],
            "expect_status": "success",
            "min_score": 60
        },
        {
            "id": "TEST 6",
            "name": "Dermatological Presentation: Skin rash + Itching",
            "symptoms": ["skin_rash", "itching"],
            "expected_in_top": ["Eczema (Atopic Dermatitis)", "Contact Dermatitis", "Urticaria (Hives)"],
            "expect_status": "success",
            "min_score": 50
        },
        {
            "id": "TEST 7",
            "name": "Unknown / Tolerant Normalization: 'head ache', 'belly pain', and invalid input",
            "symptoms": ["xyz_completely_unknown_token", "invalid_symptom_key_999"],
            "expect_status": "insufficient_or_empty",
            "test_nlp_normalization": True
        },
        {
            "id": "TEST 8",
            "name": "Insufficient Information Gate: Empty list and single symptom",
            "symptoms_empty": [],
            "symptoms_single": ["fever"],
            "expect_status": "insufficient_information"
        }
    ]

    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        test_id = tc["id"]
        test_name = tc["name"]
        print(f"\n--- [{test_id}] {test_name} ---")

        if test_id == "TEST 8":
            # Test empty list
            res_empty = run_php_symptom_matching(tc["symptoms_empty"])
            res_single = run_php_symptom_matching(tc["symptoms_single"])
            
            cond1 = res_empty.get("status") == "insufficient_information"
            cond2 = res_single.get("status") == "insufficient_information"
            cond3 = "at least 2 symptoms" in res_single.get("message", "").lower()

            if cond1 and cond2 and cond3:
                print(f"  [PASS] Empty input -> status={res_empty.get('status')}")
                print(f"  [PASS] Single input ('fever') -> status={res_single.get('status')} | Message: {res_single.get('message')}")
                passed += 1
            else:
                print(f"  [FAIL] Insufficient gate check failed. Empty={res_empty}, Single={res_single}")
            continue

        if test_id == "TEST 7":
            # Test NLP normalization
            norm_headache = run_php_normalize("head ache")
            norm_belly = run_php_normalize("belly pain")
            norm_vomiting = run_php_normalize("puking")
            
            # Test matching with unknown symptoms
            res_unknown = run_php_symptom_matching(tc["symptoms"])
            
            cond_nlp = (norm_headache == "headache") and (norm_belly == "abdominal_pain") and (norm_vomiting == "vomiting")
            cond_unknown = (res_unknown.get("status") == "insufficient_information" or len(res_unknown.get("conditions", [])) == 0)
            
            print(f"  NLP Normalization: 'head ache' -> {norm_headache} | 'belly pain' -> {norm_belly} | 'puking' -> {norm_vomiting}")
            print(f"  Unknown tokens handling: conditions_returned={len(res_unknown.get('conditions', []))}")
            
            if cond_nlp and cond_unknown:
                print(f"  [PASS] Tolerant natural language normalization and graceful unknown token handling verified.")
                passed += 1
            else:
                print(f"  [FAIL] Normalization or unknown handling mismatch.")
            continue

        # Standard test cases 1 through 6
        res = run_php_symptom_matching(tc["symptoms"])
        status = res.get("status")
        conditions = res.get("conditions", [])

        if status != tc["expect_status"] or not conditions:
            print(f"  [FAIL] Expected status '{tc['expect_status']}' with conditions, got status='{status}', count={len(conditions)}")
            continue

        top_names = [c["name"] for c in conditions[:3]]
        top_name = conditions[0]["name"]
        top_score = conditions[0]["score"]
        match_level = conditions[0]["match_level"]
        
        # Verify that at least one of the expected conditions appears in the top ranked conditions
        found_expected = any(any(exp.lower() in t.lower() for exp in tc["expected_in_top"]) for t in top_names)
        score_ok = top_score >= tc["min_score"]

        print(f"  Top Match: {top_name} (Match Score: {top_score}/100, Level: {match_level})")
        print(f"  Top 3 Ranked: {', '.join(top_names)}")
        print(f"  Matched Symptoms: {conditions[0].get('matched_symptoms', [])}")
        print(f"  Differentiating: {conditions[0].get('differentiating', '')[:80]}...")
        if res.get("emergency_signs"):
            print(f"  Emergency Signs Flagged: {res['emergency_signs']}")

        if found_expected and score_ok:
            print(f"  [PASS] Expected condition verified in top differentials with score >= {tc['min_score']}")
            passed += 1
        else:
            print(f"  [FAIL] Expected one of {tc['expected_in_top']} in top matches, but got {top_names}")

    print("\n" + "=" * 70)
    print(f" Summary: {passed}/{total} Test Cases Passed Successfully.")
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = test_suite()
    sys.exit(0 if success else 1)
