# MediSense AI – Intelligent Disease Prediction & Health Assistance System

> **Smarter Insights. Better Health.**

An educational, modern, full-stack web application demonstrating how **Artificial Intelligence** and **Machine Learning** can assist users by analyzing symptoms and health parameters to predict potential medical conditions across **65 conditions**, accompanied by comprehensive clinical information, interactive risk simulations, and large dataset architecture principles.

---

> [!IMPORTANT]
> **EDUCATIONAL COLLEGE PROJECT MEDICAL DISCLAIMER:**
> This system provides educational/informational AI predictions only and is **not a medical diagnosis**. Symptoms can have many causes. Users must always consult a qualified healthcare professional for proper clinical diagnosis and treatment. The system does not prescribe medications or provide dangerous clinical instructions.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features & Modules](#key-features--modules)
3. [Disease Information Database (25 Verified Diseases)](#disease-information-database-25-verified-diseases)
4. [AI / Machine Learning Architecture & Verified Metrics](#ai--machine-learning-architecture--verified-metrics)
5. [Large Healthcare Dataset Handling](#large-healthcare-dataset-handling)
6. [Technology Stack](#technology-stack)
7. [System Architecture](#system-architecture)
8. [Database Schema & Verification](#database-schema--verification)
9. [Project Directory Structure](#project-directory-structure)
10. [Local Installation & Setup Guide (XAMPP)](#local-installation--setup-guide-xampp)
11. [REST API Documentation](#rest-api-documentation)
12. [Cloud & Serverless Deployment Architecture (Vercel)](#cloud--serverless-deployment-architecture-vercel)
13. [Security & Data Integrity](#security--data-integrity)
14. [Limitations & Future Scope](#limitations--future-scope)

---

## Project Overview

### Problem Statement
In healthcare informatics, early awareness of potential health risks empowers patients to seek timely medical attention. However, complex diagnostic healthcare models and multi-megabyte clinical datasets cannot be loaded directly into client browsers without causing memory exhaustion, lag, and browser crashes. Furthermore, academic projects frequently lack transparent model evaluation metrics and strict separation between diagnostic claims and educational decision-support tools.

### Objectives
1. **Curate a 25-Disease Medical Knowledge Base:** Provide detailed clinical overviews, causes, risk factors, prevention strategies, and red-flag triage guidance.
2. **Develop Multi-Symptom AI Classifiers:** Implement a machine learning pipeline mapping combinations of 30 distinct clinical symptoms across body systems to potential conditions.
3. **Provide Parametric Clinical Risk Assessments:** Offer biomarker risk calculators (e.g., Glucose, Blood Pressure, BMI, Cholesterol) for Diabetes and Heart Disease with Explainable AI (XAI) feature importance rankings and What-If risk simulations.
4. **Demonstrate Decoupled Full-Stack Architecture:** Efficiently separate offline model training, serialized `joblib` pipelines, a lightweight Flask REST microservice, and a secure PHP 8 / MySQL web interface.
5. **Ensure Honest & Reproducible Metrics:** Strictly document actual evaluation figures without fabricating accuracy.

---

## Key Features & Modules

- **Home Landing Page (`index.php`):** Interactive hero banner, high-impact clinical metrics, disease category explorer, workflow summary, and safety disclaimers.
- **About MediSense AI (`about.php`):** Educational mission, ethical considerations, and clinical assistance principles.
- **AI Disease Prediction (`prediction.php`):** Multi-symptom selection form grouped by body system (Endocrine, Cardiovascular, Respiratory, Neurological, Gastrointestinal, Hepatic, Renal, Hematological, Systemic) with real-time confidence scores and runner-up differentials.
- **Diseases Library (`diseases.php`):** Searchable, filterable catalog of all 25 diseases with dynamic category filtering.
- **Disease Detail View (`disease_detail.php?id=X`):** Structured medical dossiers detailing pathology, etiology, risk factors, prevention protocols, management plans, and emergency indicators.
- **Symptoms Guide (`symptoms_guide.php`):** Indexed reference of 30 validated symptoms mapped to physiological body systems.
- **Health Awareness & Prevention (`prevention.php`):** Evidence-based lifestyle guidelines, vital screening timelines, and critical emergency red flags.
- **Dataset & AI Architecture (`dataset_info.php`):** Architectural overview of offline preprocessing, train/test isolation, batch matrix vectorization, and inference microservices.
- **About Project (`project_info.php`):** Academic seminar documentation, system modularity, and technology specifications.
- **Contact & Academic Support (`contact.php`):** Input-validated inquiry form with persistent MySQL database logging.
- **Authentication System (`login.php`, `register.php`, `logout.php`):** Secure user registration with email validation, duplicate prevention, and bcrypt password hashing.
- **User Dashboard (`dashboard.php`):** Account overview displaying total predictions, previous symptom check logs, and quick action shortcuts.
- **Clinical Risk Assessment (`assessment.php`):** Quantitative clinical parameter evaluations for Diabetes and Heart Disease.
- **Risk Assessment Results (`result.php`):** Visual risk dial gauge (Low/Moderate/High), probability percentage, XAI feature importance breakdown, and lifestyle recommendations.
- **Printable Medical Summary (`report.php`):** Print-ready, clean PDF report generator for clinical assessments.
- **What-If Risk Simulator (`simulator.php`):** Interactive parameter adjustment simulator recalculating statistical risk in real time.

---

## Disease Information Database (25 Verified Diseases)

All 25 conditions are stored in MySQL (`diseases` table) with structured metadata:

| # | Disease Name | Category | Primary Body System |
|---|---|---|---|
| 1 | **Diabetes** | Endocrine | Endocrine / Metabolic |
| 2 | **Hypertension** | Cardiovascular | Cardiovascular |
| 3 | **Heart Disease** | Cardiovascular | Cardiovascular |
| 4 | **Asthma** | Respiratory | Respiratory |
| 5 | **Pneumonia** | Respiratory | Respiratory |
| 6 | **Tuberculosis** | Respiratory / Infectious | Pulmonary / Systemic |
| 7 | **COVID-19** | Respiratory / Infectious | Respiratory / Systemic |
| 8 | **Influenza** | Respiratory / Infectious | Respiratory / Systemic |
| 9 | **Dengue** | Infectious / Tropical | Hematological / Systemic |
| 10 | **Malaria** | Infectious / Tropical | Hematological / Systemic |
| 11 | **Typhoid** | Infectious / Gastrointestinal | Gastrointestinal / Systemic |
| 12 | **Migraine** | Neurological | Central Nervous System |
| 13 | **Epilepsy** | Neurological | Central Nervous System |
| 14 | **Parkinson's Disease** | Neurological | Central Nervous System |
| 15 | **Alzheimer's Disease** | Neurological | Central Nervous System |
| 16 | **COPD** | Respiratory | Pulmonary |
| 17 | **Bronchitis** | Respiratory | Pulmonary |
| 18 | **Gastritis** | Gastrointestinal | Upper GI |
| 19 | **Hepatitis** | Gastrointestinal / Hepatic | Hepatic |
| 20 | **Fatty Liver Disease** | Gastrointestinal / Hepatic | Hepatic / Metabolic |
| 21 | **Chronic Kidney Disease** | Renal | Renal |
| 22 | **Urinary Tract Infection (UTI)** | Renal / Urological | Urological |
| 23 | **Anemia** | Hematological | Hematological |
| 24 | **Hypothyroidism** | Endocrine | Endocrine |
| 25 | **Hyperthyroidism** | Endocrine | Endocrine |

### Symptoms & Mapping Verification
- **Verified Symptoms:** 30 clinical symptoms cataloged in `symptoms` with exact matching machine learning feature keys.
- **Verified Relationships:** 96 relational mappings in `disease_symptoms` linking diseases to characteristic clinical manifestations.

---

## AI / Machine Learning Architecture & Verified Metrics

The system strictly distinguishes between:
1. **Comprehensive Disease Database (25 Conditions):** Informational clinical library.
2. **AI Machine Learning Models:** Academic statistical decision models trained on validated clinical parameter datasets.

### Model Performance Metrics (Verified via `ml/evaluation_results.json`)

#### 1. Multi-Symptom Condition Classifier (25 Classes)
- **Dataset:** 30-dimensional binary symptom matrix across all 25 disease classes.
- **Train/Test Split:** 80% Training / 20% Holdout Testing (Stratified).
- **Selected Model:** **Logistic Regression**
- **Verified Accuracy:** **84.10%**
  - *Random Forest Accuracy:* 83.60%
  - *Multinomial Naive Bayes Accuracy:* 82.60%
  - *Decision Tree Accuracy:* 68.70%

#### 2. Diabetes Risk Classifier (Binary Clinical Biomarkers)
- **Dataset:** Pima Indians-format clinical diagnostic dataset (Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age).
- **Selected Model:** **Logistic Regression** (StandardScaler pipeline)
- **Verified Accuracy:** **97.40%**
- **Precision:** 97.16%
- **Recall:** 100.00%
- **F1-Score:** 98.56%

#### 3. Heart Disease Risk Classifier (Binary Clinical Biomarkers)
- **Dataset:** Cleveland-format cardiovascular clinical parameters (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal).
- **Selected Model:** **Logistic Regression** (StandardScaler pipeline)
- **Verified Accuracy:** **98.36%**
- **Precision:** 97.44%
- **Recall:** 100.00%
- **F1-Score:** 98.70%

> [!NOTE]
> All models are saved as lightweight binary pipelines in `ml/models/` (`diabetes_model.joblib`, `heart_model.joblib`, `symptom_disease_model.joblib`), each under 15 KB.

---

## Large Healthcare Dataset Handling

To demonstrate efficient handling of large-scale healthcare data without overloading client web browsers:
1. **Zero Client-Side Dataset Loading:** Raw datasets (CSV/SQL) remain strictly on server storage and are never transmitted to the browser DOM.
2. **Offline Preprocessing Pipeline:** Cleaning, missing value imputation, outlier clamping, and standardization are executed offline prior to inference.
3. **Binary Pipeline Serialization:** High-dimensional decision spaces are compiled into compact `joblib` artifacts loaded in microseconds.
4. **Lightweight REST Microservice:** The browser interacts solely with lightweight JSON request/response payloads (< 2 KB).
5. **Database Indexing & Prepared Statements:** MySQL indexes (`PRIMARY KEY`, `UNIQUE`, foreign key constraints) ensure $O(1)$ to $O(\log n)$ query latency.

---

## Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla CSS Custom Glassmorphism Theme, Bootstrap 5.3, Bootstrap Icons, JavaScript (ES6+).
- **Backend Application:** PHP 8.0+ (PDO with prepared statements), Object-Oriented Database Singleton.
- **Machine Learning & REST API:** Python 3.8+, Scikit-Learn, Pandas, NumPy, Joblib, Flask 2.2+.
- **Database Management:** MySQL / MariaDB (UTF-8 / `utf8mb4`).
- **Development Environment:** XAMPP for Windows / Linux / macOS.
- **Cloud Serverless Runtime:** Vercel Python Serverless Functions (`@vercel/python`).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Client Browser (HTML5 / Bootstrap 5 / JS)  │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP POST (Form / JSON)
                             ▼
┌─────────────────────────────────────────────────────────┐
│            PHP 8 Web Application Server (XAMPP)         │
│  - Session Authentication & Access Control              │
│  - Input Validation & XSS Sanitization                  │
│  - Dynamic ML Bridge (`includes/ml_bridge.php`)         │
└──────────────┬───────────────────────────┬──────────────┘
               │ Prepared PDO Queries      │ JSON / cURL (Port 5000)
               ▼                           ▼
┌──────────────────────────────┐ ┌───────────────────────────────┐
│        MySQL Database        │ │    Flask Python ML Service    │
│       (`ai_healthcare`)      │ │    (`ml/prediction/api.py`)   │
│ - users                      │ │ - Multi-Symptom Predictor     │
│ - diseases (25 records)      │ │ - Diabetes Biomarker Model    │
│ - symptoms (30 records)      │ │ - Heart Disease Model         │
│ - disease_symptoms (96 rows) │ │ - Explainable AI (XAI)        │
│ - prediction_history         │ │ - Medical Safety Disclaimers  │
│ - health_assessments         │ └───────────────────────────────┘
│ - contact_messages           │
└──────────────────────────────┘
```

---

## Database Schema & Verification

Database Name: **`ai_healthcare`** (Default collation: `utf8mb4_unicode_ci`)

The single definitive database setup script is located at:
📁 **`database/schema.sql`**

### Tables Overview:
1. **`users`**: User registration records with bcrypt `password` hashes, unique emails, and registration timestamps.
2. **`diseases`**: 25 comprehensive medical records (`id`, `name`, `category`, `short_description`, `causes`, `risk_factors`, `prevention`, `management`, `when_to_seek_care`).
3. **`symptoms`**: 30 cataloged symptoms (`id`, `name`, `symptom_key`, `body_system`, `severity`).
4. **`disease_symptoms`**: 96 relational foreign key mappings linking diseases to symptoms (`disease_id`, `symptom_id`) with composite primary key.
5. **`prediction_history`**: User symptom prediction logs with foreign key cascade to `users(id)`.
6. **`health_assessments`**: Quantitative biomarker assessment logs storing JSON input data, risk levels (LOW/MODERATE/HIGH), statistical probabilities, and JSON feature importance.
7. **`health_articles`**: Curated health education articles.
8. **`contact_messages`**: Inquiries and feedback submitted via the contact form.

### Clean Re-Import Verification:
The database script includes `DROP DATABASE IF EXISTS ai_healthcare;` and can be re-run safely from scratch at any time.

---

## Project Directory Structure

```
automated-disease-predictor/
├── api/
│   └── index.py               # Standalone Flask serverless app for Vercel deployment
├── assets/
│   ├── css/
│   │   └── style.css          # Custom dark glassmorphism styling
│   └── js/
│       └── app.js             # Client interactivity scripts
├── config/
│   └── database.php           # PDO Database connection helper & configuration
├── database/
│   └── schema.sql             # Single complete SQL schema & seed script
├── includes/
│   ├── auth.php               # User login/session protection helpers
│   ├── footer.php             # Unified page footer with disclaimer
│   ├── functions.php          # Sanitization & flash message utilities
│   ├── header.php             # Unified navbar & header
│   └── ml_bridge.php          # Dynamic PHP ↔ Python execution & REST bridge
├── ml/
│   ├── datasets/              # CSV clinical datasets
│   ├── models/                # Serialized joblib pipelines (diabetes, heart, symptoms)
│   ├── prediction/
│   │   ├── api.py             # Flask ML REST inference API server
│   │   └── predict.py         # Standalone model prediction & XAI script
│   ├── training/
│   │   └── train_models.py    # Training & evaluation pipeline
│   └── evaluation_results.json# Verified evaluation metrics (Accuracy, F1, CM)
├── about.php                  # About MediSense AI page
├── assessment.php             # Clinical biomarker assessment form
├── contact.php                # Contact & support submission page
├── dashboard.php              # Authenticated user dashboard
├── dataset_info.php           # Dataset handling architecture page
├── disease_detail.php         # Individual disease dossiers (id/name lookup)
├── diseases.php               # 25-Disease library catalog
├── history.php                # User assessment history log
├── index.php                  # Primary landing page
├── login.php                  # User authentication login
├── logout.php                 # Secure session destruction & logout
├── prediction.php             # Multi-symptom AI disease predictor
├── prevention.php             # Health awareness & preventive guidance
├── profile.php                # User account overview
├── project_info.php           # Academic seminar project overview
├── register.php               # User account registration
├── report.php                 # Printable clinical assessment PDF summary
├── simulator.php              # What-If risk simulator
├── symptoms_guide.php         # 30-symptom body system guide
├── requirements.txt           # Python dependencies for ML pipeline & API
├── vercel.json                # Vercel serverless deployment configuration
├── .gitignore                 # Excludes caches, temporary files, logs, and .env
└── README.md                  # Comprehensive verified documentation
```

---

## Local Installation & Setup Guide (XAMPP)

### Prerequisites:
- **XAMPP** (Apache 2.4+ and MySQL / MariaDB 10.4+)
- **Python 3.8+** (Anaconda or Standard Python with `pip`)

### Step 1: Clone or Place Repository
Place the repository in your XAMPP web directory:
```bash
git clone https://github.com/Pearlnandu-02/automated-disease-predictor.git C:\xampp\htdocs\automated-disease-predictor
cd C:\xampp\htdocs\automated-disease-predictor
```

### Step 2: Database Setup in MySQL / phpMyAdmin
1. Start **Apache** and **MySQL** in the XAMPP Control Panel.
2. Open Windows Command Prompt or Terminal:
```bash
C:\xampp\mysql\bin\mysql.exe -u root < database\schema.sql
```
*(Alternatively, open phpMyAdmin at `http://localhost/phpmyadmin`, create database `ai_healthcare`, and import `database/schema.sql`)*.

Default seeded demo user:
- **Email:** `student@college.edu`
- **Password:** `password123`

### Step 3: Install Python Packages
Open Command Prompt and install dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Launch the Python ML API Server
In a terminal, start the prediction microservice:
```bash
python ml/prediction/api.py
```
*The API will start listening on `http://127.0.0.1:5000`.*

### Step 5: Run the Web Application
Open your browser and navigate to:
```
http://localhost/automated-disease-predictor
```
*(Or if using the PHP built-in server: `php -S 127.0.0.1:8000` and visit `http://127.0.0.1:8000`)*.

---

## REST API Documentation

The Flask microservice runs on port `5000` and provides the following endpoints:

### 1. Health Check
- **Endpoint:** `GET /health`
- **Response:**
```json
{
  "diseases_supported": 25,
  "service": "MediSense AI Disease Prediction & Health Assistance API",
  "status": "healthy"
}
```

### 2. Multi-Symptom Prediction
- **Endpoint:** `POST /predict`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "disease": "symptoms",
  "symptoms": ["high_blood_sugar", "frequent_urination", "fatigue"]
}
```
- **Response:**
```json
{
  "prediction": "Diabetes",
  "probability": 87.3,
  "runner_ups": [
    { "disease": "Chronic Kidney Disease", "probability": 5.9 },
    { "disease": "Asthma", "probability": 1.9 }
  ],
  "influencing_symptoms": ["High Blood Sugar", "Frequent Urination"],
  "symptoms_analyzed": 3,
  "model_used": "Logistic Regression",
  "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
}
```

### 3. Quantitative Risk Assessment (Diabetes / Heart Disease)
- **Endpoint:** `POST /predict`
- **Request Body:**
```json
{
  "disease": "diabetes",
  "data": {
    "Glucose": 155,
    "BMI": 32.5,
    "Age": 48,
    "BloodPressure": 85
  }
}
```
- **Response:**
```json
{
  "disease": "Diabetes Risk",
  "risk_level": "HIGH",
  "probability": 99.8,
  "feature_importance": {
    "Glucose": 0.4156,
    "Age": 0.2035,
    "BMI": 0.1620
  },
  "recommendations": [
    "Fasting/random glucose is elevated. Prioritize low-glycemic meals and track daily carbohydrate intake.",
    "BMI indicates obesity class range. Structured daily physical exercise is recommended."
  ],
  "disclaimer": "This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment."
}
```

---

## Cloud & Serverless Deployment Architecture (Vercel)

The repository provides dual-mode deployment:
1. **Local Full-Stack Mode (Primary):** Complete PHP 8 + MySQL + Python architecture run locally via XAMPP.
2. **Cloud Serverless Mode (Vercel):** Configured via `vercel.json` and `api/index.py`. Because standard Vercel serverless containers execute Python rather than Apache/PHP/MySQL, `api/index.py` is an independent Flask serverless web application and API service providing cloud inference, REST endpoints, and UI views without requiring a local database.

---

## Security & Data Integrity

1. **Password Protection:** Uses PHP's `password_hash($password, PASSWORD_DEFAULT)` and `password_verify()` with bcrypt hashing. Plain-text passwords are never stored.
2. **SQL Injection Prevention:** 100% of database interactions use PDO prepared statements with parameterized inputs.
3. **Cross-Site Scripting (XSS) Prevention:** Output variables are sanitized with `htmlspecialchars($data, ENT_QUOTES, 'UTF-8')`.
4. **User Data Isolation:** Historical predictions and assessment reports enforce strict session-based tenant isolation (`WHERE user_id = ?`). Users cannot view other users' medical logs.
5. **No Committed Secrets:** Sensitive passwords, logs, temporary files, and API secrets are ignored via `.gitignore`.
6. **Graceful Error Handling:** Database exceptions log internally to server logs without exposing raw credentials or SQL syntax to users.

---

## Limitations & Future Scope

### Limitations
- **Academic Demonstration:** Trained on benchmark clinical datasets; not evaluated for certified medical device usage.
- **Statistical Approximation:** Predictions reflect probabilistic correlations rather than clinical laboratory tests.

### Future Scope
- Integration with HL7/FHIR healthcare interoperability standards.
- Telemedicine doctor consultation appointment booking module.
- Wearable device biometric data integration (Apple HealthKit / Google Fit).
- Multilingual disease database localization.

---

## License & Attribution
Developed as an Academic Engineering College Project in Artificial Intelligence & Healthcare Informatics. All predictions are strictly educational.