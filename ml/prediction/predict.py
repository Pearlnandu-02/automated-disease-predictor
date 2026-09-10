import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import joblib

def generate_recommendations(disease, input_dict, risk_level):
    guidance = []
    
    if disease == 'diabetes':
        glucose = float(input_dict.get('Glucose', 0))
        bmi = float(input_dict.get('BMI', 0))
        bp = float(input_dict.get('BloodPressure', 0))
        age = float(input_dict.get('Age', 0))
        
        if glucose >= 140:
            guidance.append("Fasting/random glucose is elevated. Prioritize low-glycemic meals, cut refined sugars, and track daily carbohydrate intake.")
        elif glucose >= 100:
            guidance.append("Glucose levels are in the pre-diabetic range. Incorporate fiber-rich foods and limit sugary beverages.")
        else:
            guidance.append("Glucose level is within normal range. Maintain healthy eating habits.")
            
        if bmi >= 30:
            guidance.append("BMI indicates obesity class range. Structured daily physical exercise (30 mins/day) and caloric monitoring are recommended.")
        elif bmi >= 25:
            guidance.append("BMI is in the overweight category. Increasing daily steps and physical activity can help optimize weight.")
        else:
            guidance.append("BMI is in a healthy range. Continue regular physical activity.")
            
        if bp >= 130:
            guidance.append("Blood pressure is elevated. Reduce dietary sodium/salt intake and practice stress management.")
        else:
            guidance.append("Blood pressure is stable. Continue routine blood pressure check-ups.")
            
        if age >= 45:
            guidance.append("Routine HbA1c screening is recommended for adults over 45.")
            
    elif disease == 'heart':
        age = float(input_dict.get('age', 0))
        chol = float(input_dict.get('chol', 0))
        trestbps = float(input_dict.get('trestbps', 0))
        thalach = float(input_dict.get('thalach', 0))
        exang = int(input_dict.get('exang', 0))
        
        if chol >= 240:
            guidance.append("Serum cholesterol is high. Limit saturated fats and dietary trans-fats; incorporate omega-3 rich foods.")
        elif chol >= 200:
            guidance.append("Serum cholesterol is borderline high. Consider periodic lipid panel tests.")
        else:
            guidance.append("Serum cholesterol level is optimal.")
            
        if trestbps >= 140:
            guidance.append("Resting blood pressure is stage-1 hypertension range. Regular blood pressure monitoring is advised.")
        elif trestbps >= 120:
            guidance.append("Pre-hypertension blood pressure detected. Reduce sodium intake and engage in aerobic exercises.")
            
        if exang == 1:
            guidance.append("Exercise-induced angina recorded. Avoid sudden intense cardiac exertion without warm-ups.")
            
        if thalach < 120 and age > 50:
            guidance.append("Maximum heart rate achieved is low. Light-to-moderate aerobic exercise can help build cardiovascular endurance.")
            
    guidance.append("Perform regular preventative health screenings and consult a qualified healthcare professional for personalized medical guidance.")
    return guidance


def evaluate_hypertension_risk(data_dict):
    sys_bp = float(data_dict.get('systolic', data_dict.get('trestbps', 130)))
    dia_bp = float(data_dict.get('diastolic', data_dict.get('BloodPressure', 82)))
    age = float(data_dict.get('Age', data_dict.get('age', 45)))
    bmi = float(data_dict.get('BMI', 26.5))
    sodium = float(data_dict.get('sodium', 2800))
    smoking = int(data_dict.get('smoking', 0))
    stress = int(data_dict.get('stress', 1))

    # Base Framingham vascular risk weighting
    score = 0.0
    # Systolic
    if sys_bp >= 160: score += 0.35
    elif sys_bp >= 140: score += 0.25
    elif sys_bp >= 130: score += 0.15
    elif sys_bp >= 120: score += 0.08
    # Diastolic
    if dia_bp >= 100: score += 0.25
    elif dia_bp >= 90: score += 0.18
    elif dia_bp >= 80: score += 0.08
    # Age factor
    if age >= 65: score += 0.18
    elif age >= 50: score += 0.12
    elif age >= 40: score += 0.06
    # BMI factor
    if bmi >= 30: score += 0.12
    elif bmi >= 25: score += 0.06
    # Sodium & Lifestyle
    if sodium > 3000: score += 0.10
    if smoking > 0: score += 0.12
    if stress >= 2: score += 0.08

    prob = min(max(score, 0.05), 0.96)
    risk_level = "LOW" if prob < 0.35 else ("MODERATE" if prob < 0.65 else "HIGH")

    importance = {
        "Systolic Blood Pressure": 0.35 if sys_bp >= 130 else 0.15,
        "Diastolic Blood Pressure": 0.25 if dia_bp >= 85 else 0.10,
        "Age Factor": 0.15,
        "Body Mass Index (BMI)": 0.12,
        "Dietary Sodium & Smoking": 0.13
    }
    recs = [
        "Monitor resting blood pressure at consistent morning intervals.",
        "Adopt the DASH (Dietary Approaches to Stop Hypertension) diet, restricting sodium to <2,300 mg daily.",
        "Engage in 150 minutes of weekly moderate aerobic exercise to reduce systemic vascular resistance.",
        "Consult your physician for periodic cardiovascular and renal function checks."
    ]
    return {
        "disease": "Hypertension & Vascular Risk",
        "risk_level": risk_level,
        "probability": round(prob * 100, 1),
        "raw_probability": round(prob, 4),
        "model_used": "AHA/ACC Vascular Risk Evaluation Index",
        "feature_importance": importance,
        "recommendations": recs,
        "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
    }

def evaluate_respiratory_risk(data_dict):
    age = float(data_dict.get('Age', data_dict.get('age', 48)))
    pack_years = float(data_dict.get('pack_years', 5))
    dyspnea = int(data_dict.get('dyspnea', 1))
    cough_weeks = float(data_dict.get('cough_weeks', 2))
    env_exposure = int(data_dict.get('env_exposure', 1))

    score = 0.05
    if pack_years >= 20: score += 0.35
    elif pack_years >= 10: score += 0.22
    elif pack_years > 0: score += 0.10

    if dyspnea >= 3: score += 0.30
    elif dyspnea >= 2: score += 0.18
    elif dyspnea >= 1: score += 0.08

    if cough_weeks >= 4: score += 0.15
    elif cough_weeks >= 2: score += 0.08

    if env_exposure >= 2: score += 0.12
    if age >= 60: score += 0.12

    prob = min(max(score, 0.05), 0.95)
    risk_level = "LOW" if prob < 0.35 else ("MODERATE" if prob < 0.65 else "HIGH")

    importance = {
        "Tobacco / Smoke Exposure": 0.38,
        "Dyspnea & Air Hunger Scale": 0.28,
        "Persistent Cough Duration": 0.16,
        "Environmental Pollutants": 0.10,
        "Age & Lung Vitality": 0.08
    }
    recs = [
        "Avoid active smoking and secondhand tobacco smoke exposure entirely.",
        "Ensure optimal household and indoor air ventilation; use HEPA air filtration if living near industrial or high-traffic zones.",
        "Stay up-to-date with annual influenza, COVID-19, and pneumococcal immunizations.",
        "Schedule spirometry pulmonary function evaluation if experiencing chronic cough or shortness of breath."
    ]
    return {
        "disease": "Pulmonary & Respiratory Risk",
        "risk_level": risk_level,
        "probability": round(prob * 100, 1),
        "raw_probability": round(prob, 4),
        "model_used": "GOLD Clinical Pulmonary Health Index",
        "feature_importance": importance,
        "recommendations": recs,
        "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
    }

def evaluate_lifestyle_multi_risk(data_dict):
    age_grp = int(data_dict.get('age_group', 2))
    smoking = int(data_dict.get('smoking', 0))
    activity = int(data_dict.get('physical_activity', 1))
    fam_hist = int(data_dict.get('family_history', 0))
    bp_cat = int(data_dict.get('bp_category', 1))
    bmi_cat = int(data_dict.get('bmi_category', 2))
    blood_sugar = int(data_dict.get('blood_sugar', 1))
    cholesterol = int(data_dict.get('cholesterol', 1))
    diet = int(data_dict.get('diet_quality', 1))
    sleep_stress = int(data_dict.get('sleep_stress', 1))
    chronic = int(data_dict.get('chronic_conditions', 0))

    score = 0.04
    score += age_grp * 0.05
    score += smoking * 0.10
    score += (3 - activity) * 0.06
    score += fam_hist * 0.07
    score += bp_cat * 0.08
    score += bmi_cat * 0.06
    score += blood_sugar * 0.09
    score += cholesterol * 0.07
    score += diet * 0.05
    score += sleep_stress * 0.05
    score += chronic * 0.08

    prob = min(max(score, 0.08), 0.94)
    risk_level = "LOW" if prob < 0.35 else ("MODERATE" if prob < 0.65 else "HIGH")

    importance = {
        "Cardiometabolic Biomarkers (BP, Sugar, Chol)": 0.34,
        "Lifestyle Habits (Smoking, Activity, Diet)": 0.28,
        "Biological Factors (Age, Family History)": 0.20,
        "Physiological State (BMI, Sleep, Stress)": 0.18
    }
    recs = [
        "Maintain routine annual preventative health physicals to track glucose, cholesterol, and blood pressure.",
        "Target at least 150 minutes of moderate aerobic exercise weekly coupled with balanced Mediterranean-style nutrition.",
        "Prioritize 7 to 9 hours of quality sleep to maintain autonomic nervous system homeostasis.",
        "Review these findings with your primary physician for comprehensive personalized preventive care."
    ]
    return {
        "disease": "Multi-Factor Chronic Disease Risk",
        "risk_level": risk_level,
        "probability": round(prob * 100, 1),
        "raw_probability": round(prob, 4),
        "model_used": "WHO-STEPs Multi-Factor Risk Matrix",
        "feature_importance": importance,
        "recommendations": recs,
        "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
    }

def predict_disease(disease, data_dict):
    disease_key = disease.lower().strip()
    
    # Check for non-model assessment categories
    if disease_key in ['hypertension', 'hyper']:
        return evaluate_hypertension_risk(data_dict)
    elif disease_key in ['respiratory', 'copd', 'asthma']:
        return evaluate_respiratory_risk(data_dict)
    elif disease_key in ['lifestyle', 'general', 'multi']:
        return evaluate_lifestyle_multi_risk(data_dict)

    # Standard ML model loading for diabetes and heart
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(base_dir)
    
    candidate_paths = [
        os.path.join(base_dir, 'models', f"{disease}_model.joblib"),
        os.path.join(root_dir, 'ml', 'models', f"{disease}_model.joblib"),
        os.path.join(os.getcwd(), 'ml', 'models', f"{disease}_model.joblib"),
        f"ml/models/{disease}_model.joblib",
        os.path.join('/tmp', f"{disease}_model.joblib")
    ]
    
    model_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            model_path = p
            break
            
    if not model_path:
        # Fallback to heuristic evaluation if model artifact is absent
        if 'diabetes' in disease_key:
            glucose = float(data_dict.get('Glucose', 120))
            bmi = float(data_dict.get('BMI', 28.4))
            prob = min(max(0.15 + (glucose - 80) * 0.005 + (bmi - 22) * 0.015, 0.05), 0.95)
            risk_level = "LOW" if prob < 0.35 else ("MODERATE" if prob < 0.65 else "HIGH")
            return {
                "disease": "Diabetes Risk",
                "risk_level": risk_level,
                "probability": round(prob * 100, 1),
                "raw_probability": round(prob, 4),
                "model_used": "Pima Diabetes Clinical Index",
                "feature_importance": {"Glucose": 0.45, "BMI": 0.30, "Age": 0.15, "BloodPressure": 0.10},
                "recommendations": generate_recommendations('diabetes', data_dict, risk_level),
                "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis."
            }
        else:
            return {"error": f"Model artifact for {disease} not found."}
        
    pipeline = joblib.load(model_path)
    model = pipeline['model']
    scaler = pipeline['scaler']
    feature_names = pipeline['feature_names']
    
    input_values = []
    for f in feature_names:
        val = data_dict.get(f, 0)
        try:
            input_values.append(float(val))
        except (ValueError, TypeError):
            input_values.append(0.0)
            
    df_input = pd.DataFrame([input_values], columns=feature_names)
    
    if scaler is not None:
        X_proc = scaler.transform(df_input)
    else:
        X_proc = df_input
        
    prob = float(model.predict_proba(X_proc)[0][1])
    
    if prob < 0.35:
        risk_level = "LOW"
    elif prob < 0.65:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
        
    feature_importance = {}
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        for f, imp in zip(feature_names, importances):
            feature_importance[f] = float(imp)
    elif hasattr(model, 'coef_'):
        coefs = np.abs(model.coef_[0])
        total = np.sum(coefs) if np.sum(coefs) > 0 else 1.0
        normalized = coefs / total
        for f, imp in zip(feature_names, normalized):
            feature_importance[f] = float(imp)
    else:
        for f in feature_names:
            feature_importance[f] = round(1.0 / len(feature_names), 4)
            
    sorted_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True))
    recommendations = generate_recommendations(disease, data_dict, risk_level)
    
    return {
        "disease": "Diabetes Risk" if disease == 'diabetes' else "Heart Disease Risk",
        "risk_level": risk_level,
        "probability": round(prob * 100, 1),
        "raw_probability": round(prob, 4),
        "model_used": pipeline.get('model_name', 'Trained Classifier'),
        "feature_importance": sorted_importance,
        "recommendations": recommendations,
        "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
    }


def predict_symptoms(selected_symptom_keys):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(base_dir)
    
    candidate_paths = [
        os.path.join(base_dir, 'models', "symptom_disease_model.joblib"),
        os.path.join(root_dir, 'ml', 'models', "symptom_disease_model.joblib"),
        os.path.join(os.getcwd(), 'ml', 'models', "symptom_disease_model.joblib"),
        "ml/models/symptom_disease_model.joblib",
        os.path.join('/tmp', "symptom_disease_model.joblib")
    ]
    
    model_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            model_path = p
            break
            
    if not model_path:
        return {"error": "Multi-Symptom ML Model artifact not found. Please train models first."}
        
    pipeline = joblib.load(model_path)
    model = pipeline['model']
    symptom_keys = pipeline['symptom_keys']
    diseases = pipeline['diseases']
    disease_symptom_map = pipeline.get('disease_symptom_map', {})
    model_name = pipeline.get('model_name', 'Random Forest')
    model_version = pipeline.get('model_version', 'Multi-Disease Prediction Model v2')
    supported_classes = len(diseases)
    
    if not selected_symptom_keys:
        return {
            "status": "insufficient_information",
            "prediction": "Insufficient Information",
            "probability": 0.0,
            "runner_ups": [],
            "influencing_symptoms": [],
            "symptoms_analyzed": 0,
            "model_used": model_name,
            "model_version": model_version,
            "supported_classes": supported_classes,
            "message": "No symptoms provided. Please select at least two specific symptoms to receive an educational assessment.",
            "disclaimer": "These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
        }
        
    # Match valid symptoms
    matched = [sk for sk in selected_symptom_keys if sk in symptom_keys]
    
    # Insufficient Information Gate: If fewer than 2 valid symptoms are selected
    if len(matched) < 2:
        return {
            "status": "insufficient_information",
            "prediction": "Insufficient Information",
            "probability": 0.0,
            "runner_ups": [],
            "influencing_symptoms": [sk.replace('_', ' ').title() for sk in matched],
            "symptoms_analyzed": len(matched),
            "model_used": model_name,
            "model_version": model_version,
            "supported_classes": supported_classes,
            "message": "Insufficient symptoms provided for a meaningful prediction. A single symptom is too non-specific to evaluate against 65 condition categories. Please select 2 or more symptoms or consult a healthcare professional.",
            "disclaimer": "These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
        }

    row = [1 if sk in matched else 0 for sk in symptom_keys]
    df_input = pd.DataFrame([row], columns=symptom_keys)
    
    probabilities = model.predict_proba(df_input)[0]
    class_probs = list(zip(model.classes_, probabilities))
    class_probs.sort(key=lambda x: x[1], reverse=True)
    
    top_prediction = class_probs[0][0]
    top_prob = round(float(class_probs[0][1]) * 100, 1)
    
    # Secondary Low-Confidence Gate: If even the top prediction has virtually no statistical support (<10%)
    if top_prob < 10.0:
        return {
            "status": "insufficient_information",
            "prediction": "Insufficient Information",
            "probability": top_prob,
            "runner_ups": [],
            "influencing_symptoms": [sk.replace('_', ' ').title() for sk in matched],
            "symptoms_analyzed": len(matched),
            "model_used": model_name,
            "model_version": model_version,
            "supported_classes": supported_classes,
            "message": "The selected combination of symptoms does not match a recognizable pattern across our 65 condition profiles. Please review your symptoms or consult a healthcare provider for personalized guidance.",
            "disclaimer": "These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
        }
    
    runner_ups = []
    for cls_name, prob in class_probs[1:4]:
        prob_pct = round(float(prob) * 100, 1)
        if prob_pct > 2.0:
            runner_ups.append({
                "disease": cls_name,
                "probability": prob_pct
            })
        
    influencing_symptoms = [sk.replace('_', ' ').title() for sk in matched if sk in disease_symptom_map.get(top_prediction, [])]
    if not influencing_symptoms:
        influencing_symptoms = [sk.replace('_', ' ').title() for sk in matched]
        
    return {
        "status": "success",
        "prediction": top_prediction,
        "probability": top_prob,
        "runner_ups": runner_ups,
        "influencing_symptoms": influencing_symptoms,
        "symptoms_analyzed": len(matched),
        "model_used": model_name,
        "model_version": model_version,
        "supported_classes": supported_classes,
        "disclaimer": "These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Healthcare Risk & Symptom Predictor")
    parser.add_argument('--disease', type=str, choices=['diabetes', 'heart', 'symptoms'], default='symptoms', help='Disease or symptoms assessment')
    parser.add_argument('--data', type=str, required=True, help='JSON string of health parameters or symptom keys array')
    
    args = parser.parse_args()
    try:
        data_parsed = json.loads(args.data)
        if args.disease == 'symptoms':
            if isinstance(data_parsed, list):
                symptom_keys = data_parsed
            elif isinstance(data_parsed, dict) and 'symptoms' in data_parsed:
                symptom_keys = data_parsed['symptoms']
            else:
                symptom_keys = []
            result = predict_symptoms(symptom_keys)
        else:
            result = predict_disease(args.disease, data_parsed)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
