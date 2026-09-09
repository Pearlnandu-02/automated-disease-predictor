import os
import sys
import json
from flask import Flask, request, jsonify

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ml.prediction.predict import predict_disease, predict_symptoms

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI Healthcare Disease Prediction & Health Assistance API",
        "diseases_supported": 25
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        req_data = request.get_json(force=True)
        disease = req_data.get('disease', 'symptoms')
        data_dict = req_data.get('data', {})
        symptoms = req_data.get('symptoms', [])
        
        if disease == 'symptoms' or symptoms:
            if not symptoms and isinstance(data_dict, list):
                symptoms = data_dict
            elif not symptoms and isinstance(data_dict, dict) and 'symptoms' in data_dict:
                symptoms = data_dict['symptoms']
            result = predict_symptoms(symptoms)
        elif disease in ['diabetes', 'heart']:
            result = predict_disease(disease, data_dict)
        else:
            return jsonify({"error": "Invalid disease mode specified. Choose 'symptoms', 'diabetes', or 'heart'."}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting AI Healthcare Prediction API Service on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)
