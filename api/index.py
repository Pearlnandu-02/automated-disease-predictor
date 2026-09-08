import os
import sys
import json
from flask import Flask, request, jsonify

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI Healthcare Risk Assessment API (Vercel Serverless)",
        "supported_diseases": ["diabetes", "heart"]
    })

@app.route('/api/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'GET':
        return jsonify({"message": "Send a POST request with JSON payload: {'disease': 'diabetes', 'data': {...}}"})
    
    try:
        req_data = request.get_json(force=True, silent=True)
        if not req_data:
            req_data = request.form.to_dict()
            
        disease = req_data.get('disease')
        data_dict = req_data.get('data', {})
        
        if isinstance(data_dict, str):
            data_dict = json.loads(data_dict)
            
        if not disease or disease not in ['diabetes', 'heart']:
            return jsonify({"error": "Invalid disease. Must be 'diabetes' or 'heart'."}), 400
            
        result = predict_disease(disease, data_dict)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel Serverless Export
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
