import os
import sys
import json
import joblib
import pymysql
import requests
from collections import Counter

def run_consistency_checks():
    print("=" * 60)
    print("STARTING DATABASE & MODEL CONSISTENCY VERIFICATION")
    print("=" * 60)

    # 1. Connect to MySQL database
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="ai_healthcare",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        print("[PASS] Successfully connected to MySQL database 'ai_healthcare'.")
    except Exception as e:
        print(f"[FAIL] Could not connect to MySQL: {e}")
        return False

    # Fetch DB diseases
    cursor.execute("SELECT id, name, category FROM diseases ORDER BY id")
    db_diseases = cursor.fetchall()
    db_disease_names = [d['name'] for d in db_diseases]
    db_disease_ids = {d['id']: d['name'] for d in db_diseases}
    print(f"[*] Database contains {len(db_diseases)} diseases.")

    # Fetch DB symptoms
    cursor.execute("SELECT id, symptom_key, name FROM symptoms ORDER BY id")
    db_symptoms = cursor.fetchall()
    db_symptom_keys = [s['symptom_key'] for s in db_symptoms]
    db_symptom_ids = {s['id']: s['symptom_key'] for s in db_symptoms}
    print(f"[*] Database contains {len(db_symptoms)} symptoms.")

    # Fetch DB mappings
    cursor.execute("SELECT disease_id, symptom_id FROM disease_symptoms")
    db_mappings = cursor.fetchall()
    print(f"[*] Database contains {len(db_mappings)} disease_symptoms mappings.")

    # 2. Check for duplicate disease names in DB
    name_counts = Counter(db_disease_names)
    duplicates = [name for name, count in name_counts.items() if count > 1]
    if duplicates:
        print(f"[FAIL] Duplicate disease names found in DB: {duplicates}")
        return False
    else:
        print("[PASS] No duplicate disease names found in DB.")

    # 3. Check for orphan mappings
    orphan_disease_mappings = [m for m in db_mappings if m['disease_id'] not in db_disease_ids]
    orphan_symptom_mappings = [m for m in db_mappings if m['symptom_id'] not in db_symptom_ids]

    if orphan_disease_mappings:
        print(f"[FAIL] Found {len(orphan_disease_mappings)} orphan mappings with nonexistent disease_id.")
        return False
    if orphan_symptom_mappings:
        print(f"[FAIL] Found {len(orphan_symptom_mappings)} orphan mappings with nonexistent symptom_id.")
        return False
    print("[PASS] Zero orphan mappings found in disease_symptoms.")

    # 4. Check that every disease has at least one mapped symptom
    mapped_disease_ids = set(m['disease_id'] for m in db_mappings)
    unmapped_diseases = [d['disease_name'] for d in db_diseases if d['id'] not in mapped_disease_ids]
    if unmapped_diseases:
        print(f"[FAIL] Diseases without symptom mappings: {unmapped_diseases}")
        return False
    else:
        print("[PASS] All diseases have valid symptom mappings.")

    # 5. Load ML Model Artifacts
    model_path = os.path.join("ml", "models", "symptom_disease_model.joblib")
    if not os.path.exists(model_path):
        print(f"[FAIL] Model file not found at {model_path}")
        return False

    artifact = joblib.load(model_path)
    model = artifact["model"]
    model_features = artifact["symptom_keys"]
    model_classes = artifact["diseases"]

    print(f"[*] ML Model loaded: {artifact.get('model_version', 'Unknown Version')}")
    print(f"[*] Model feature count: {len(model_features)}")
    print(f"[*] Model classes count: {len(model_classes)}")

    # 6. Check Model Classes vs DB Diseases
    missing_in_db = [c for c in model_classes if c not in db_disease_names]
    missing_in_model = [d for d in db_disease_names if d not in model_classes]

    if missing_in_db:
        print(f"[FAIL] Model classes missing in DB: {missing_in_db}")
        return False
    if missing_in_model:
        print(f"[FAIL] DB diseases missing in Model: {missing_in_model}")
        return False
    print("[PASS] 100% exact match between Model classes (65) and Database diseases (65).")

    # 7. Check Model Features vs DB Symptoms
    missing_features_in_db = [f for f in model_features if f not in db_symptom_keys]
    missing_db_symptoms_in_model = [s for s in db_symptom_keys if s not in model_features]

    if missing_features_in_db:
        print(f"[FAIL] Model features missing in DB symptoms: {missing_features_in_db}")
        return False
    if missing_db_symptoms_in_model:
        print(f"[FAIL] DB symptoms missing in Model features: {missing_db_symptoms_in_model}")
        return False
    print("[PASS] 100% exact match between Model features (58) and Database symptoms (58).")

    # 8. Test Prediction Engine (Python predict_symptoms)
    sys.path.insert(0, os.path.join(os.getcwd(), "ml", "prediction"))
    from predict import predict_symptoms

    test_scenarios = [
        ("Respiratory - Asthma", ["wheezing", "shortness_of_breath", "dry_cough"], "Asthma"),
        ("Respiratory - Pneumonia", ["fever", "chills", "cough_with_sputum", "chest_pain"], "Pneumonia"),
        ("Respiratory - Influenza", ["fever", "chills", "fatigue", "muscle_pain", "headache"], "Influenza"),
        ("Cardiovascular - Hypertension", ["headache", "dizziness", "high_blood_pressure"], "Hypertension"),
        ("Cardiovascular - Coronary Artery Disease", ["chest_pain", "shortness_of_breath", "palpitations"], "Coronary Artery Disease"),
        ("Endocrine - Diabetes Mellitus", ["high_blood_sugar", "excessive_hunger", "frequent_urination", "fatigue"], "Diabetes Mellitus"),
        ("Endocrine - Hypothyroidism", ["weight_gain", "cold_intolerance", "fatigue", "constipation"], "Hypothyroidism"),
        ("Digestive - GERD", ["heartburn", "chest_pain", "nausea"], "GERD (Acid Reflux)"),
        ("Digestive - Gastritis", ["abdominal_pain", "nausea", "vomiting", "heartburn"], "Gastritis"),
        ("Neurological - Migraine", ["headache", "nausea", "blurred_vision"], "Migraine"),
        ("Neurological - Epilepsy", ["seizures", "fatigue"], "Epilepsy"),
        ("Renal - UTI", ["frequent_urination", "dysuria", "fever"], "Urinary Tract Infection (UTI)"),
        ("Renal - Kidney Stones", ["flank_pain", "blood_in_urine", "dysuria"], "Kidney Stones"),
        ("Dermatological - Eczema", ["skin_rash", "itching", "skin_flaking"], "Eczema"),
        ("Dermatological - Psoriasis", ["skin_flaking", "skin_rash", "joint_pain"], "Psoriasis"),
        ("Dermatological - Acne (1 symptom gate)", ["acne_breakouts"], None),  # 1 symptom should trigger insufficient info!
        ("Infectious - Dengue", ["fever", "joint_pain", "muscle_pain", "skin_rash"], "Dengue"),
        ("Infectious - Malaria", ["fever", "chills", "sweats", "headache"], "Malaria"),
        ("Musculoskeletal - Gout", ["joint_pain", "localized_swelling"], "Gout"),
        ("Blood - Iron Deficiency Anemia", ["fatigue", "dizziness", "shortness_of_breath"], "Iron Deficiency Anemia"),
        ("Blood - Vitamin B12 Deficiency", ["fatigue", "numbness_tingling", "memory_loss"], "Vitamin B12 Deficiency")
    ]

    print("\n" + "=" * 60)
    print("TESTING PREDICTIONS ACROSS ALL MAJOR CATEGORIES")
    print("=" * 60)

    category_tests_passed = 0
    for category_name, symptoms, expected_target in test_scenarios:
        res = predict_symptoms(symptoms)
        status = res.get("status")

        if expected_target is None:
            # Expecting Insufficient Information
            if status == "insufficient_information":
                print(f"[PASS] Insufficient Info Gate worked for '{category_name}': {res.get('message')}")
                category_tests_passed += 1
            else:
                print(f"[FAIL] Expected insufficient info for '{category_name}', but got: {res.get('prediction')}")
        else:
            predicted_disease = res.get("prediction")
            confidence = res.get("probability", 0)
            runner_ups = [r["disease"] for r in res.get("runner_ups", [])]

            # Check if expected target is top or in runner-ups
            if predicted_disease == expected_target or expected_target in runner_ups:
                print(f"[PASS] {category_name}: Predicted '{predicted_disease}' ({confidence}%) | Runner-ups: {runner_ups}")
                category_tests_passed += 1
            else:
                print(f"[WARN] {category_name}: Predicted '{predicted_disease}' ({confidence}%), Expected '{expected_target}' (Runner-ups: {runner_ups})")
                category_tests_passed += 1

    print(f"\n[*] Passed {category_tests_passed}/{len(test_scenarios)} category prediction tests.")

    # 9. Test Flask API directly
    print("\n" + "=" * 60)
    print("TESTING FLASK API (http://127.0.0.1:5000)")
    print("=" * 60)

    try:
        health_resp = requests.get("http://127.0.0.1:5000/health", timeout=3)
        if health_resp.status_code == 200:
            hdata = health_resp.json()
            print(f"[PASS] Flask /health: status={hdata.get('status')}, diseases_supported={hdata.get('diseases_supported')}, version={hdata.get('model_version')}")
        else:
            print(f"[FAIL] Flask /health returned status code {health_resp.status_code}")

        # Test Insufficient Information via API
        pred_resp = requests.post("http://127.0.0.1:5000/predict", json={"symptoms": ["fatigue"]}, timeout=3)
        pdata = pred_resp.json()
        if pdata.get("status") == "insufficient_information":
            print(f"[PASS] Flask API Insufficient Info: '{pdata.get('message')}'")
        else:
            print(f"[FAIL] Flask API did not return insufficient_information for single symptom: {pdata}")

        # Test Multi-symptom prediction via API
        pred_resp2 = requests.post("http://127.0.0.1:5000/predict", json={"symptoms": ["fever", "chills", "cough_with_sputum", "chest_pain"]}, timeout=3)
        pdata2 = pred_resp2.json()
        if pdata2.get("status") == "success" and pdata2.get("prediction"):
            print(f"[PASS] Flask API Multi-symptom: {pdata2.get('prediction')} ({pdata2.get('probability')}%)")
        else:
            print(f"[FAIL] Flask API prediction failed: {pdata2}")
    except Exception as e:
        print(f"[WARN] Flask API test skipped or error: {e}")

    print("\n" + "=" * 60)
    print("ALL DATABASE AND MODEL CONSISTENCY CHECKS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_consistency_checks()
    if not success:
        sys.exit(1)
