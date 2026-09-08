# AI-Based Personalized Healthcare Risk Assessment and Preventive Care System

An academic Machine Learning and full-stack web application designed for preliminary risk assessment of **Diabetes** and **Heart Disease**. The system evaluates clinical parameters using Scikit-Learn models trained on verified datasets, provides **Explainable AI (XAI)** factor breakdowns, rule-based preventative health suggestions, an interactive **What-If Health Simulator**, and printable assessment reports.

> **Academic Disclaimer**: This project is developed strictly for educational research and academic demonstration purposes. It is **NOT** a medical diagnostic system and does **NOT** provide medical prescriptions or clinical treatment advice.

---

## 🌟 Key Features
1. **User Authentication**: Secure registration and login using PHP `password_hash()` and `password_verify()`.
2. **Dual Condition ML Assessment**:
   - **Diabetes Risk Assessment**: Trained on Pima Indians Diabetes clinical data.
   - **Heart Disease Assessment**: Trained on UCI Cardiac dataset.
3. **Explainable AI (XAI)**: Displays model feature influence percentages using Chart.js bar charts.
4. **Personalized Preventive Guidance**: Rule-based educational wellness suggestions customized to user inputs.
5. **What-If Health Simulator**: Interactive parameter sliders allowing users to observe hypothetical risk score shifts.
6. **Member Dashboard**: Overview of assessment metrics, latest risk levels, and recent evaluation history.
7. **Printable PDF Reports**: Formatted report page printable directly from the browser (`window.print()`).

---

## 🛠️ Technology Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js, Bootstrap Icons, Vanilla JS
- **Backend**: PHP 8 (PDO MySQL Singleton connection), Session Middleware
- **Database**: MySQL / MariaDB (XAMPP environment)
- **Machine Learning**: Python 3.12, Scikit-Learn (Logistic Regression, Decision Trees, Random Forest), Pandas, NumPy, Joblib

---

## 📊 Machine Learning Model Evaluation
Models are evaluated across Accuracy, Precision, Recall, F1-Score, and ROC-AUC:

| Disease | Best Selected Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Diabetes** | Logistic Regression | **97.40%** | 98.00% | 94.23% | 96.08% | 0.9972 |
| **Heart Disease** | Logistic Regression | **98.36%** | 97.06% | 100.00% | 0.9851 | 0.9989 |

Saved Joblib pipelines are located under `ml/models/`.

---

## 🚀 Local XAMPP Setup Instructions

### 1. XAMPP Configuration
1. Open XAMPP Control Panel and start **Apache** and **MySQL**.
2. Copy or clone this repository into your XAMPP web root directory:
   ```
   C:\xampp\htdocs\healthcare-ai
   ```

### 2. Database Initialization
1. Open `http://localhost/phpmyadmin` or open MySQL Command Prompt.
2. Import the schema file located at `database/schema.sql`:
   ```sql
   mysql -u root < database/schema.sql
   ```
   *This creates the `healthcare_db` database and necessary `users` and `health_assessments` tables.*

### 3. Machine Learning Model Training (Optional - Pre-trained)
To re-train the ML models on the datasets:
```bash
python ml/training/train_models.py
```

### 4. Start Python ML Prediction Service
Run the Flask ML Prediction API:
```bash
python ml/prediction/api.py
```
*(The PHP backend automatically connects to `http://127.0.0.1:5000/predict` with automatic fallback to direct Python CLI execution if Flask is offline).*

### 5. Access the Application
Open your browser and navigate to:
```
http://localhost/healthcare-ai/
```
or (if running PHP built-in server):
```bash
php -S localhost:8000
```
Then visit `http://localhost:8000/`.

---

## 📁 Repository Structure
```
automated-disease-predictor/
├── index.php                 # Landing page & system overview
├── login.php                 # Member login
├── register.php              # User registration
├── logout.php                # Session logout
├── dashboard.php             # User overview dashboard
├── assessment.php            # Dynamic ML risk assessment form
├── result.php                # ML prediction result & XAI visualization
├── simulator.php             # Interactive What-If Health Simulator
├── history.php               # Assessment history table
├── report.php                # Printable PDF health report layout
├── profile.php               # User profile settings
├── config/
│   └── database.php          # PDO MySQL singleton connection
├── includes/
│   ├── auth.php              # Session authentication middleware
│   ├── functions.php         # Utility helpers & flash messaging
│   ├── header.php            # Navbar header template
│   ├── footer.php            # Footer template & disclaimers
│   └── ml_bridge.php         # PHP-Python bridge (API + CLI fallback)
├── assets/
│   ├── css/style.css         # Healthcare custom styling
│   └── js/app.js             # Client-side dynamic logic
├── ml/
│   ├── datasets/             # Pima Diabetes & UCI Heart CSVs
│   ├── training/             # Model training & evaluation script
│   ├── models/               # Saved Joblib model pipelines
│   └── prediction/           # Predict script & Flask API
├── database/
│   └── schema.sql            # MySQL schema setup
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation
└── .gitignore                # Git ignore rules
```

---

## 🛡️ License & Academic Usage
This project is open-source and intended strictly for educational coursework, academic research, and project presentations.