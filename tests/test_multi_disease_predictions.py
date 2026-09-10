import os
import sys
import json

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_symptoms

def run_prediction_tests():
    test_cases = [
        {
            "category": "Insufficient Input Gate",
            "name": "Single symptom (fever)",
            "symptoms": ["fever"],
            "expected_prediction": "Insufficient Information"
        },
        {
            "category": "Insufficient Input Gate",
            "name": "Empty symptoms list",
            "symptoms": [],
            "expected_prediction": "Insufficient Information"
        },
        {
            "category": "Respiratory",
            "name": "Asthma presentation",
            "symptoms": ["shortness_of_breath", "wheezing", "cough_with_sputum"],
            "expected_prediction": "Asthma"
        },
        {
            "category": "Respiratory",
            "name": "Common Cold presentation",
            "symptoms": ["runny_nose", "sneezing", "sore_throat", "dry_cough"],
            "expected_prediction": "Common Cold"
        },
        {
            "category": "Neurological",
            "name": "Migraine presentation",
            "symptoms": ["headache", "nausea", "vomiting", "dizziness"],
            "expected_prediction": "Migraine"
        },
        {
            "category": "Dermatological",
            "name": "Eczema presentation",
            "symptoms": ["itching", "skin_rash", "skin_flaking"],
            "expected_prediction": "Eczema (Atopic Dermatitis)"
        },
        {
            "category": "Musculoskeletal",
            "name": "Gout presentation",
            "symptoms": ["joint_pain", "localized_swelling", "skin_rash"],
            "expected_prediction": "Gout"
        },
        {
            "category": "Endocrine",
            "name": "Diabetes presentation",
            "symptoms": ["high_blood_sugar", "frequent_urination", "fatigue", "weight_loss", "blurred_vision"],
            "expected_prediction": "Diabetes"
        },
        {
            "category": "Gastrointestinal",
            "name": "Gastroenteritis presentation",
            "symptoms": ["diarrhea", "vomiting", "abdominal_pain", "fever", "nausea"],
            "expected_prediction": "Gastroenteritis"
        },
        {
            "category": "Urinary",
            "name": "Kidney Stones presentation",
            "symptoms": ["flank_pain", "dysuria", "blood_in_urine", "nausea"],
            "expected_prediction": "Kidney Stones"
        },
        {
            "category": "Psychological",
            "name": "Generalized Anxiety presentation",
            "symptoms": ["anxiety_nervousness", "palpitations", "sleep_disturbance", "muscle_pain"],
            "expected_prediction": "Generalized Anxiety"
        }
    ]

    print("Running Multi-Disease Category Prediction Tests...\n")
    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        res = predict_symptoms(tc["symptoms"])
        pred = res.get("prediction")
        prob = res.get("probability", 0.0)
        status = res.get("status")
        runners = res.get("runner_ups", [])

        is_match = (pred == tc["expected_prediction"])
        status_icon = "PASS" if is_match else "WARN"
        if is_match:
            passed += 1

        print(f"[{status_icon}] [{tc['category']}] {tc['name']}")
        print(f"       Symptoms: {tc['symptoms']}")
        print(f"       Prediction: {pred} ({prob}%) | Status: {status}")
        if runners:
            runner_str = ", ".join([f"{r['disease']} ({r['probability']}%)" for r in runners])
            print(f"       Runner-ups: {runner_str}")
        print()

    print(f"Tests Completed: {passed}/{total} Passed.")
    return passed == total

if __name__ == '__main__':
    success = run_prediction_tests()
    sys.exit(0 if success else 1)
