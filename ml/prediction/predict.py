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
            
    # General disclaimers & universal advice
    guidance.append("Perform regular preventative health screenings and consult a qualified healthcare professional for personalized medical guidance.")
    return guidance


def predict_disease(disease, data_dict):
    model_path = f"ml/models/{disease}_model.joblib"
    if not os.path.exists(model_path):
        return {"error": f"Model artifact for {disease} not found."}
        
    pipeline = joblib.load(model_path)
    model = pipeline['model']
    scaler = pipeline['scaler']
    feature_names = pipeline['feature_names']
    
    # Prepare input array matching feature order
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
        
    # Get probability and prediction
    prob = float(model.predict_proba(X_proc)[0][1])
    
    if prob < 0.35:
        risk_level = "LOW"
    elif prob < 0.65:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
        
    # Compute Explainable AI feature importance weights for this model
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
            
    # Sort feature importance descending
    sorted_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True))
    
    # Recommendations
    recommendations = generate_recommendations(disease, data_dict, risk_level)
    
    return {
        "disease": "Diabetes Risk" if disease == 'diabetes' else "Heart Disease Risk",
        "risk_level": risk_level,
        "probability": round(prob * 100, 1),
        "raw_probability": round(prob, 4),
        "model_used": pipeline.get('model_name', 'Trained Classifier'),
        "feature_importance": sorted_importance,
        "recommendations": recommendations,
        "disclaimer": "This prediction is generated by an educational AI risk model for preliminary assessment only and does not constitute a medical diagnosis or treatment plan."
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Healthcare Risk Assessment Predictor")
    parser.add_argument('--disease', type=str, required=True, choices=['diabetes', 'heart'], help='Disease to assess')
    parser.add_argument('--data', type=str, required=True, help='JSON string of health parameters')
    
    args = parser.parse_args()
    try:
        data_dict = json.loads(args.data)
        result = predict_disease(args.disease, data_dict)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
