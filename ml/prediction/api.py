import os
import json
from flask import Flask, request, jsonify
from predict import predict_disease

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Healthcare Risk ML API"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        req_data = request.get_json(force=True)
        disease = req_data.get('disease')
        data_dict = req_data.get('data', {})
        
        if not disease or disease not in ['diabetes', 'heart']:
            return jsonify({"error": "Invalid disease specified. Must be 'diabetes' or 'heart'."}), 400
            
        result = predict_disease(disease, data_dict)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting ML Prediction Flask API Service on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)
