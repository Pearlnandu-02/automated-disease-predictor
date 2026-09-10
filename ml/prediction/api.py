import os
import sys
import json
from flask import Flask, request, jsonify

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ml.prediction.predict import predict_disease, predict_symptoms
from ml.vision.scanner import compute_vision_metrics
import base64
import tempfile

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "MediSense AI Disease Prediction & Health Assistance API",
        "diseases_supported": 65,
        "model_version": "Multi-Disease Prediction Model v2",
        "features": ["symptoms_prediction", "clinical_risk", "health_simulator", "infection_injury_scanner"]
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
        else:
            result = predict_disease(disease, data_dict)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scan-image', methods=['POST'])
def scan_image():
    temp_path = None
    try:
        # Check if file sent via multipart/form-data
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "category": "Unable to Assess", "error": "No selected file"}), 400
            
            # Save temporarily
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            file.save(temp_path)
            result = compute_vision_metrics(temp_path)
            return jsonify(result)

        # Check JSON payload
        req_data = request.get_json(silent=True) or {}
        if 'image_path' in req_data and req_data['image_path']:
            image_path = req_data['image_path']
            result = compute_vision_metrics(image_path)
            return jsonify(result)
        
        if 'image_base64' in req_data and req_data['image_base64']:
            raw_b64 = req_data['image_base64']
            if ',' in raw_b64:
                raw_b64 = raw_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(raw_b64)
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            with open(temp_path, 'wb') as f:
                f.write(img_bytes)
            result = compute_vision_metrics(temp_path)
            return jsonify(result)

        return jsonify({"success": False, "category": "Unable to Assess", "error": "No image data provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "category": "Unable to Assess", "error": str(e)}), 500
    finally:
        # Ephemeral cleanup: NEVER leave temporary uploaded images on disk
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

if __name__ == '__main__':
    print("Starting MediSense AI Prediction API Service on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)

