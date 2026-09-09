import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

os.makedirs('ml/datasets', exist_ok=True)
os.makedirs('ml/models', exist_ok=True)

# ----------------------------------------------------
# 1. DIABETES DATASET (Pima Indians format)
# ----------------------------------------------------
diabetes_path = 'ml/datasets/diabetes.csv'
if not os.path.exists(diabetes_path):
    np.random.seed(42)
    n_samples = 768
    pregnancies = np.random.randint(0, 15, n_samples)
    glucose = np.random.normal(120, 30, n_samples).clip(50, 200)
    bp = np.random.normal(70, 12, n_samples).clip(40, 120)
    skin = np.random.normal(20, 10, n_samples).clip(0, 99)
    insulin = np.random.normal(80, 40, n_samples).clip(0, 846)
    bmi = np.random.normal(32, 6, n_samples).clip(15, 60)
    dpf = np.random.normal(0.47, 0.3, n_samples).clip(0.08, 2.4)
    age = np.random.randint(21, 81, n_samples)
    
    z = -8.0 + 0.03*pregnancies + 0.035*glucose + 0.01*bp + 0.08*bmi + 0.9*dpf + 0.03*age
    prob = 1 / (1 + np.exp(-z))
    outcome = (prob > 0.5).astype(int)
    
    df_diabetes = pd.DataFrame({
        'Pregnancies': pregnancies,
        'Glucose': glucose.round(1),
        'BloodPressure': bp.round(1),
        'SkinThickness': skin.round(1),
        'Insulin': insulin.round(1),
        'BMI': bmi.round(1),
        'DiabetesPedigreeFunction': dpf.round(3),
        'Age': age,
        'Outcome': outcome
    })
    df_diabetes.to_csv(diabetes_path, index=False)
else:
    df_diabetes = pd.read_csv(diabetes_path)

X_d = df_diabetes.drop('Outcome', axis=1)
y_d = df_diabetes['Outcome']

X_d_train, X_d_test, y_d_train, y_d_test = train_test_split(X_d, y_d, test_size=0.2, random_state=42, stratify=y_d)

scaler_d = StandardScaler()
X_d_train_scaled = scaler_d.fit_transform(X_d_train)
X_d_test_scaled = scaler_d.transform(X_d_test)

diabetes_models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
}

best_d_model = None
best_d_score = -1
best_d_name = ""
diabetes_eval = {}

for name, model in diabetes_models.items():
    if name == 'Logistic Regression':
        model.fit(X_d_train_scaled, y_d_train)
        y_pred = model.predict(X_d_test_scaled)
    else:
        model.fit(X_d_train, y_d_train)
        y_pred = model.predict(X_d_test)
        
    acc = float(accuracy_score(y_d_test, y_pred))
    prec = float(precision_score(y_d_test, y_pred, zero_division=0))
    rec = float(recall_score(y_d_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_d_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_d_test, y_pred).tolist()
    
    diabetes_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm
    }
    
    if acc > best_d_score:
        best_d_score = acc
        best_d_model = model
        best_d_name = name

joblib.dump({
    'model': best_d_model,
    'scaler': scaler_d if best_d_name == 'Logistic Regression' else None,
    'feature_names': list(X_d.columns),
    'model_name': best_d_name
}, 'ml/models/diabetes_model.joblib')

# ----------------------------------------------------
# 2. HEART DISEASE DATASET (UCI format)
# ----------------------------------------------------
heart_path = 'ml/datasets/heart.csv'
if not os.path.exists(heart_path):
    np.random.seed(42)
    n_samples = 303
    age = np.random.randint(29, 78, n_samples)
    sex = np.random.choice([0, 1], n_samples, p=[0.32, 0.68])
    cp = np.random.choice([0, 1, 2, 3], n_samples)
    trestbps = np.random.normal(130, 17, n_samples).clip(94, 200)
    chol = np.random.normal(246, 50, n_samples).clip(126, 564)
    fbs = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    restecg = np.random.choice([0, 1, 2], n_samples)
    thalach = np.random.normal(149, 22, n_samples).clip(71, 202)
    exang = np.random.choice([0, 1], n_samples, p=[0.67, 0.33])
    oldpeak = np.random.exponential(1.0, n_samples).clip(0, 6.2)
    slope = np.random.choice([0, 1, 2], n_samples)
    ca = np.random.choice([0, 1, 2, 3, 4], n_samples)
    thal = np.random.choice([0, 1, 2, 3], n_samples)
    
    z = -4.0 + 0.03*age - 0.5*sex + 0.8*cp + 0.01*trestbps + 0.005*chol - 0.02*thalach + 1.1*exang + 0.6*oldpeak + 0.8*ca
    prob = 1 / (1 + np.exp(-z))
    target = (prob > 0.5).astype(int)
    
    df_heart = pd.DataFrame({
        'age': age,
        'sex': sex,
        'cp': cp,
        'trestbps': trestbps.round(1),
        'chol': chol.round(1),
        'fbs': fbs,
        'restecg': restecg,
        'thalach': thalach.round(1),
        'exang': exang,
        'oldpeak': oldpeak.round(1),
        'slope': slope,
        'ca': ca,
        'thal': thal,
        'target': target
    })
    df_heart.to_csv(heart_path, index=False)
else:
    df_heart = pd.read_csv(heart_path)

X_h = df_heart.drop('target', axis=1)
y_h = df_heart['target']

X_h_train, X_h_test, y_h_train, y_h_test = train_test_split(X_h, y_h, test_size=0.2, random_state=42, stratify=y_h)

scaler_h = StandardScaler()
X_h_train_scaled = scaler_h.fit_transform(X_h_train)
X_h_test_scaled = scaler_h.transform(X_h_test)

heart_models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
}

best_h_model = None
best_h_score = -1
best_h_name = ""
heart_eval = {}

for name, model in heart_models.items():
    if name == 'Logistic Regression':
        model.fit(X_h_train_scaled, y_h_train)
        y_pred = model.predict(X_h_test_scaled)
    else:
        model.fit(X_h_train, y_h_train)
        y_pred = model.predict(X_h_test)
        
    acc = float(accuracy_score(y_h_test, y_pred))
    prec = float(precision_score(y_h_test, y_pred, zero_division=0))
    rec = float(recall_score(y_h_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_h_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_h_test, y_pred).tolist()
    
    heart_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm
    }
    
    if acc > best_h_score:
        best_h_score = acc
        best_h_model = model
        best_h_name = name

joblib.dump({
    'model': best_h_model,
    'scaler': scaler_h if best_h_name == 'Logistic Regression' else None,
    'feature_names': list(X_h.columns),
    'model_name': best_h_name
}, 'ml/models/heart_model.joblib')

# ----------------------------------------------------
# 3. 25-DISEASE MULTI-SYMPTOM PREDICTION MODEL
# ----------------------------------------------------
symptom_keys = [
    'high_blood_sugar', 'frequent_urination', 'high_blood_pressure', 'chest_pain',
    'shortness_of_breath', 'cough_with_sputum', 'hemoptysis', 'fever', 'chills',
    'joint_pain', 'headache', 'seizures', 'resting_tremor', 'memory_loss',
    'wheezing', 'heartburn', 'jaundice', 'right_upper_quadrant_pain', 'flank_pain',
    'dysuria', 'fatigue', 'cold_intolerance', 'heat_intolerance', 'palpitations',
    'weight_loss', 'sweats', 'nausea', 'vomiting', 'dizziness', 'abdominal_pain'
]

diseases = [
    "Diabetes", "Hypertension", "Heart Disease", "Asthma", "Pneumonia",
    "Tuberculosis", "COVID-19", "Influenza", "Dengue", "Malaria",
    "Typhoid", "Migraine", "Epilepsy", "Parkinson's Disease", "Alzheimer's Disease",
    "COPD", "Bronchitis", "Gastritis", "Hepatitis", "Fatty Liver Disease",
    "Chronic Kidney Disease", "Urinary Tract Infection (UTI)", "Anemia",
    "Hypothyroidism", "Hyperthyroidism"
]

disease_symptom_map = {
    "Diabetes": ['high_blood_sugar', 'frequent_urination', 'fatigue', 'weight_loss'],
    "Hypertension": ['high_blood_pressure', 'headache', 'dizziness'],
    "Heart Disease": ['chest_pain', 'shortness_of_breath', 'fatigue', 'palpitations'],
    "Asthma": ['shortness_of_breath', 'wheezing', 'cough_with_sputum'],
    "Pneumonia": ['fever', 'cough_with_sputum', 'chest_pain', 'shortness_of_breath'],
    "Tuberculosis": ['cough_with_sputum', 'hemoptysis', 'fever', 'sweats', 'weight_loss'],
    "COVID-19": ['fever', 'shortness_of_breath', 'cough_with_sputum', 'fatigue'],
    "Influenza": ['fever', 'chills', 'headache', 'joint_pain', 'fatigue'],
    "Dengue": ['fever', 'joint_pain', 'headache', 'fatigue', 'nausea'],
    "Malaria": ['fever', 'chills', 'sweats', 'headache', 'nausea'],
    "Typhoid": ['fever', 'abdominal_pain', 'headache', 'fatigue', 'nausea'],
    "Migraine": ['headache', 'nausea', 'vomiting', 'dizziness'],
    "Epilepsy": ['seizures', 'dizziness', 'headache'],
    "Parkinson's Disease": ['resting_tremor', 'fatigue'],
    "Alzheimer's Disease": ['memory_loss', 'fatigue'],
    "COPD": ['shortness_of_breath', 'cough_with_sputum', 'wheezing', 'fatigue'],
    "Bronchitis": ['cough_with_sputum', 'shortness_of_breath', 'fever', 'fatigue'],
    "Gastritis": ['heartburn', 'nausea', 'vomiting', 'abdominal_pain'],
    "Hepatitis": ['jaundice', 'fatigue', 'nausea', 'abdominal_pain'],
    "Fatty Liver Disease": ['right_upper_quadrant_pain', 'fatigue', 'abdominal_pain'],
    "Chronic Kidney Disease": ['fatigue', 'flank_pain', 'frequent_urination'],
    "Urinary Tract Infection (UTI)": ['dysuria', 'frequent_urination', 'flank_pain', 'fever'],
    "Anemia": ['fatigue', 'dizziness', 'shortness_of_breath', 'palpitations'],
    "Hypothyroidism": ['fatigue', 'cold_intolerance', 'weight_loss'],
    "Hyperthyroidism": ['palpitations', 'heat_intolerance', 'weight_loss', 'sweats']
}

# Generate 5,000 synthetic patient records
np.random.seed(42)
records = []

for _ in range(5000):
    dis = np.random.choice(diseases)
    primary_syms = disease_symptom_map[dis]
    row = {sk: 0 for sk in symptom_keys}
    
    # 85% probability for primary symptoms
    for ps in primary_syms:
        if np.random.rand() < 0.85:
            row[ps] = 1
            
    # 5% probability for random noise symptoms
    for sk in symptom_keys:
        if sk not in primary_syms and np.random.rand() < 0.05:
            row[sk] = 1
            
    row['disease'] = dis
    records.append(row)

df_sym = pd.DataFrame(records)
df_sym.to_csv('ml/datasets/symptom_disease.csv', index=False)

X_s = df_sym.drop('disease', axis=1)
y_s = df_sym['disease']

X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(X_s, y_s, test_size=0.2, random_state=42, stratify=y_s)

symptom_models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
    'Decision Tree': DecisionTreeClassifier(max_depth=12, random_state=42),
    'Naive Bayes': MultinomialNB(),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
}

best_s_model = None
best_s_score = -1
best_s_name = ""
symptom_eval = {}

for name, model in symptom_models.items():
    model.fit(X_s_train, y_s_train)
    y_pred = model.predict(X_s_test)
    
    acc = float(accuracy_score(y_s_test, y_pred))
    prec = float(precision_score(y_s_test, y_pred, average='weighted', zero_division=0))
    rec = float(recall_score(y_s_test, y_pred, average='weighted', zero_division=0))
    f1 = float(f1_score(y_s_test, y_pred, average='weighted', zero_division=0))
    cm = confusion_matrix(y_s_test, y_pred, labels=diseases).tolist()
    
    symptom_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm
    }
    
    if acc > best_s_score:
        best_s_score = acc
        best_s_model = model
        best_s_name = name

joblib.dump({
    'model': best_s_model,
    'symptom_keys': symptom_keys,
    'diseases': diseases,
    'disease_symptom_map': disease_symptom_map,
    'model_name': best_s_name
}, 'ml/models/symptom_disease_model.joblib')

# Save Evaluation Metrics
evaluation_summary = {
    'diabetes': {
        'selected_model': best_d_name,
        'models': diabetes_eval
    },
    'heart_disease': {
        'selected_model': best_h_name,
        'models': heart_eval
    },
    'symptom_disease': {
        'selected_model': best_s_name,
        'dataset_source': 'Synthesized Clinical Symptom Dataset (5,000 Patient Records)',
        'num_records': len(df_sym),
        'num_features': len(symptom_keys),
        'num_classes': len(diseases),
        'models': symptom_eval
    }
}

with open('ml/evaluation_results.json', 'w') as f:
    json.dump(evaluation_summary, f, indent=4)

print("Full ML Training Complete!")
print(f"Selected Diabetes Model: {best_d_name} (Accuracy: {best_d_score*100:.2f}%)")
print(f"Selected Heart Model: {best_h_name} (Accuracy: {best_h_score*100:.2f}%)")
print(f"Selected Multi-Symptom Disease Model: {best_s_name} (Accuracy: {best_s_score*100:.2f}%)")
