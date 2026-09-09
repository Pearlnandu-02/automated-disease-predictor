# AI Healthcare – Intelligent Disease Prediction & Health Assistance System

An educational, modern, full-stack web application demonstrating how **Artificial Intelligence** and **Machine Learning** can analyze symptoms and health parameters to predict potential medical conditions across **25 diseases**, accompanied by structured disease guidance and large dataset architecture principles.

---

> [!IMPORTANT]
> **EDUCATIONAL COLLEGE PROJECT DISCLAIMER:**
> This system provides educational/informational AI predictions only and is **not a medical diagnosis**. Symptoms can have many causes. Users must always consult a qualified healthcare professional for proper diagnosis and treatment.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features & Modules](#key-features--modules)
3. [Diseases Database (25 Diseases)](#diseases-database-25-diseases)
4. [Technology Stack](#technology-stack)
5. [System Architecture](#system-architecture)
6. [Large Dataset Handling & Scaling](#large-dataset-handling--scaling)
7. [Machine Learning & Model Training](#machine-learning--model-training)
8. [Database Schema](#database-schema)
9. [Project Folder Structure](#project-folder-structure)
10. [Local Installation & XAMPP Setup](#local-installation--xampp-setup)
11. [REST API Documentation](#rest-api-documentation)
12. [Future Scope & Limitations](#future-scope--limitations)

---

## Project Overview

### Problem Statement
In modern healthcare, early awareness of potential medical conditions can encourage timely clinical consultation. However, high-volume healthcare datasets cannot be directly processed within client browsers without risking browser instability.

### Objectives
1. Build a responsive, user-friendly healthcare portal presenting structured information for 25 diseases.
2. Develop a multi-symptom AI prediction engine using Scikit-Learn classification pipelines.
3. Demonstrate a scalable, decoupled architecture separating database storage, web application server, and ML prediction microservices.
4. Provide transparent metrics (Accuracy, Precision, Recall, F1-Score, Confusion Matrix) and medical safety disclaimers.

---

## Key Features & Modules

1. **Home Landing Page (`/` / `index.php`):** Modern startup UI with hero banner, statistics cards, disease categories, feature cards, and safety disclaimers.
2. **About AI Healthcare (`/about` / `about.php`):** Platform mission, educational scope, and AI safety principles.
3. **AI Disease Prediction (`/prediction` / `prediction.php`):** Multi-symptom selection form evaluating inputs against trained Random Forest / Logistic Regression classification models.
4. **Diseases Library (`/diseases` / `diseases.php`):** Filterable catalog of 25 diseases with search and category filtering.
5. **Disease Details (`/disease_detail.php`):** In-depth view covering short description, causes, risk factors, prevention, management, and when to seek care.
6. **Symptoms Guide (`/symptoms` / `symptoms_guide.php`):** Categorized index of 30 clinical symptoms grouped by body systems.
7. **Health Awareness & Prevention (`/prevention` / `prevention.php`):** Preventive health tips, screening timelines, and emergency triage red flags.
8. **Dataset & AI Architecture (`/dataset-info` / `dataset_info.php`):** Detailed documentation on offline dataset preprocessing, batch training, database indexing, and model evaluation metrics.
9. **About Project (`/project-info` / `project_info.php`):** Academic project overview, tech stack details, and system workflow.
10. **Contact & Support (`/contact` / `contact.php`):** Feedback submission form and project inquiries.
11. **User Authentication (`/login`, `/register`, `/logout`):** Secure password hashing (`password_hash`) and session authentication.
12. **User Dashboard (`/dashboard` / `dashboard.php`):** Member dashboard showing historical predictions, quick links, and account information.
13. **What-If Risk Simulator (`/simulator` / `simulator.php`):** Interactive biological parameter adjustment tool for prospective risk calculation.

---

## Diseases Database (25 Diseases)

1. **Diabetes** (Endocrine)
2. **Hypertension** (Cardiovascular)
3. **Heart Disease** (Cardiovascular)
4. **Asthma** (Respiratory)
5. **Pneumonia** (Respiratory)
6. **Tuberculosis** (Respiratory / Infectious)
7. **COVID-19** (Respiratory / Infectious)
8. **Influenza** (Respiratory / Infectious)
9. **Dengue** (Infectious / Tropical)
10. **Malaria** (Infectious / Tropical)
11. **Typhoid** (Infectious / Gastrointestinal)
12. **Migraine** (Neurological)
13. **Epilepsy** (Neurological)
14. **Parkinson's Disease** (Neurological)
15. **Alzheimer's Disease** (Neurological)
16. **COPD** (Respiratory)
17. **Bronchitis** (Respiratory)
18. **Gastritis** (Gastrointestinal)
19. **Hepatitis** (Gastrointestinal / Hepatic)
20. **Fatty Liver Disease** (Gastrointestinal / Hepatic)
21. **Chronic Kidney Disease** (Renal)
22. **Urinary Tract Infection (UTI)** (Renal / Urological)
23. **Anemia** (Hematological)
24. **Hypothyroidism** (Endocrine)
25. **Hyperthyroidism** (Endocrine)

---

## Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla CSS Dark Glassmorphism Design System, Bootstrap 5, JavaScript (ES6+), Chart.js
- **Web Backend:** PHP 8.0+ (PDO with prepared statements), Flask WSGI (Vercel serverless integration)
- **Database:** MySQL / MariaDB (`ai_healthcare` database)
- **Machine Learning:** Python 3.12, Scikit-Learn, Pandas, NumPy, Joblib
- **Local Server:** XAMPP (Apache + MySQL)

---

## System Architecture

```
User Browser (HTML5 / Bootstrap 5 / JS)
       │
       ▼
Web Server Layer (PHP 8 PDO / Flask WSGI)
       │
       ├──────────────────────────┐
       ▼                          ▼
MySQL Database             Python ML Microservice
(`ai_healthcare` schema)   (`ml/prediction/predict.py`)
                           (Loads `joblib` pipelines)
```

---

## Large Dataset Handling & Scaling

To demonstrate handling large datasets without crashing client browsers:
- **Offline Data Preprocessing:** Preprocessing, scaling, and feature extraction are completed prior to model training.
- **Separate Dataset Storage:** Datasets (`ml/datasets/`) remain on server storage and are never sent to the client.
- **Lightweight Inference:** Only trained `joblib` binary model pipelines are loaded during runtime inference.
- **Indexed Database Queries:** MySQL tables utilize primary keys, foreign keys, and indexes for high-speed queries.
- **Server-Side Pagination:** Query pagination (`LIMIT`, `OFFSET`) is utilized for large database listings.

---

## Machine Learning & Model Training

To train models and generate evaluation metrics:
```bash
python ml/training/train_models.py
```

### Models Evaluated:
- **Multi-Symptom Disease Predictor:** Logistic Regression / Random Forest (Accuracy: **84.10%**)
- **Diabetes Classifier:** Logistic Regression (Accuracy: **97.40%**)
- **Heart Disease Classifier:** Logistic Regression (Accuracy: **98.36%**)

Evaluations are exported to `ml/evaluation_results.json`.

---

## Database Schema

Database Name: `ai_healthcare`

Tables:
- `users` (id, name, email, password, created_at)
- `diseases` (id, name, category, short_description, causes, risk_factors, prevention, management, when_to_seek_care)
- `symptoms` (id, name, symptom_key, body_system, severity)
- `disease_symptoms` (disease_id, symptom_id)
- `prediction_history` (id, user_id, symptoms_selected, predicted_disease, confidence, created_at)
- `health_articles` (id, title, category, summary, content, created_at)

---

## Project Folder Structure

```
automated-disease-predictor/
├── api/
│   └── index.py               # Vercel Flask entrypoint & WSGI handler
├── assets/
│   ├── css/
│   │   └── style.css          # Custom dark glassmorphism styles
│   └── js/
│       └── app.js             # Client-side scripts
├── config/
│   └── database.php           # Database PDO connection class
├── database/
│   └── schema.sql             # MySQL schema & seed data for 25 diseases
├── includes/
│   ├── auth.php               # Authentication helpers
│   ├── footer.php             # Shared HTML footer
│   ├── functions.php          # Sanitization & flash message utilities
│   ├── header.php             # Shared HTML header & navbar
│   └── ml_bridge.php          # PHP to Python ML service bridge
├── ml/
│   ├── datasets/              # Preprocessed CSV datasets
│   ├── models/                # Trained joblib model artifacts
│   ├── prediction/
│   │   ├── api.py             # Flask ML API server
│   │   └── predict.py         # Model inference script
│   ├── training/
│   │   └── train_models.py    # Training & evaluation script
│   └── evaluation_results.json# Model metrics (Accuracy, F1, CM)
├── about.php                  # About AI Healthcare page
├── assessment.php             # Clinical parameter assessment page
├── contact.php                # Contact & Support page
├── dashboard.php              # User Dashboard page
├── dataset_info.php           # Dataset & AI Architecture page
├── disease_detail.php         # Individual Disease Details page
├── diseases.php               # 25 Diseases Library page
├── index.php                  # Home landing page
├── login.php                  # Login page
├── logout.php                 # Logout script
├── prediction.php             # AI Symptom Prediction page
├── prevention.php             # Health Prevention page
├── profile.php                # User Profile page
├── project_info.php           # About Project page
├── register.php               # Registration page
├── report.php                 # Printable Report page
├── simulator.php              # What-If Health Simulator page
├── symptoms_guide.php         # Symptoms Guide page
├── README.md                  # Complete Project Documentation
└── vercel.json                # Vercel Serverless deployment config
```

---

## Local Installation & XAMPP Setup

### Prerequisites
- XAMPP (PHP 8.0+, MySQL)
- Anaconda Python 3.12 or Python 3.8+

### Step 1: Clone Repository
```bash
git clone https://github.com/Pearlnandu-02/automated-disease-predictor.git
cd automated-disease-predictor
```

### Step 2: Import MySQL Database in XAMPP
1. Start Apache and MySQL modules in XAMPP Control Panel.
2. Open phpMyAdmin or MySQL CLI.
3. Import `database/schema.sql`:
```bash
C:\xampp\mysql\bin\mysql.exe -u root < database/schema.sql
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Train Machine Learning Models
```bash
python ml/training/train_models.py
```

### Step 5: Run Platform
- **PHP Web Application:** Place project in `C:\xampp\htdocs\automated-disease-predictor` and navigate to `http://localhost/automated-disease-predictor` or start local PHP server:
  ```bash
  C:\xampp\php\php.exe -S 127.0.0.1:8000
  ```
- **Python ML Flask API (Optional for direct REST calls):**
  ```bash
  python ml/prediction/api.py
  ```

---

## REST API Documentation

### POST `/api/predict`
Request Payload:
```json
{
  "disease": "symptoms",
  "symptoms": ["high_blood_sugar", "frequent_urination", "fatigue"]
}
```

Response:
```json
{
  "prediction": "Diabetes",
  "probability": 87.8,
  "runner_ups": [
    { "disease": "Chronic Kidney Disease", "probability": 9.6 }
  ],
  "influencing_symptoms": ["High Blood Sugar", "Frequent Urination", "Fatigue"],
  "model_used": "Logistic Regression",
  "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis."
}
```

---

## Future Scope & Limitations

### Limitations
- The system evaluates statistical symptom probabilities and cannot replace diagnostic lab testing.
- Datasets are synthesized for educational demonstration.

### Future Scope
- Integration of Electronic Health Record (EHR) standards (FHIR API).
- Mobile application deployment using React Native.
- Multilingual disease information support.

---

## License & Citation
Developed for Academic Final-Year College Project Presentation.