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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
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
    ca = np.random.choice([0, 1, 2, 3], n_samples, p=[0.58, 0.22, 0.13, 0.07])
    thal = np.random.choice([1, 2, 3], n_samples, p=[0.06, 0.55, 0.39])

    z_heart = -3.5 + 0.03*age + 0.6*sex + 0.8*cp - 0.015*thalach + 0.7*exang + 0.4*oldpeak + 0.5*ca
    prob_heart = 1 / (1 + np.exp(-z_heart))
    target = (prob_heart > 0.5).astype(int)

    df_heart = pd.DataFrame({
        'age': age, 'sex': sex, 'cp': cp, 'trestbps': trestbps.round(1),
        'chol': chol.round(1), 'fbs': fbs, 'restecg': restecg,
        'thalach': thalach.round(1), 'exang': exang, 'oldpeak': oldpeak.round(1),
        'slope': slope, 'ca': ca, 'thal': thal, 'target': target
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
    'Logistic Regression': LogisticRegression(random_state=42),
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
# 3. 65-DISEASE MULTI-SYMPTOM PREDICTION MODEL (v2)
# ----------------------------------------------------
# 58 Standardized Clinical Symptom Keys
symptom_keys = [
    # 1-30 Core Symptoms
    'high_blood_sugar', 'frequent_urination', 'high_blood_pressure', 'chest_pain',
    'shortness_of_breath', 'cough_with_sputum', 'hemoptysis', 'fever', 'chills',
    'joint_pain', 'headache', 'seizures', 'resting_tremor', 'memory_loss',
    'wheezing', 'heartburn', 'jaundice', 'right_upper_quadrant_pain', 'flank_pain',
    'dysuria', 'fatigue', 'cold_intolerance', 'heat_intolerance', 'palpitations',
    'weight_loss', 'sweats', 'nausea', 'vomiting', 'dizziness', 'abdominal_pain',
    # 31-58 Expanded Symptoms
    'runny_nose', 'sneezing', 'sore_throat', 'dry_cough', 'nasal_congestion',
    'loss_of_smell', 'diarrhea', 'constipation', 'bloating', 'skin_rash',
    'itching', 'skin_flaking', 'acne_breakouts', 'hives_welts', 'localized_swelling',
    'muscle_pain', 'back_pain', 'joint_stiffness', 'numbness_tingling', 'blurred_vision',
    'excessive_hunger', 'weight_gain', 'hair_thinning', 'anxiety_nervousness',
    'depressed_mood', 'sleep_disturbance', 'leg_swelling', 'blood_in_urine'
]

# 65 Canonical Diseases / Conditions
diseases = [
    # Original 1-25
    "Diabetes", "Hypertension", "Heart Disease", "Asthma", "Pneumonia",
    "Tuberculosis", "COVID-19", "Influenza", "Dengue", "Malaria",
    "Typhoid", "Migraine", "Epilepsy", "Parkinson's Disease", "Alzheimer's Disease",
    "COPD", "Bronchitis", "Gastritis", "Hepatitis", "Fatty Liver Disease",
    "Chronic Kidney Disease", "Urinary Tract Infection (UTI)", "Anemia",
    "Hypothyroidism", "Hyperthyroidism",
    # Expanded 26-65
    "Common Cold", "Allergic Rhinitis", "Sinusitis", "Heart Failure", "Arrhythmia",
    "Angina Pectoris", "Peripheral Artery Disease", "Prediabetes", "Obesity", "Polycystic Ovary Syndrome (PCOS)",
    "GERD (Acid Reflux)", "Peptic Ulcer Disease", "Gastroenteritis", "Irritable Bowel Syndrome (IBS)", "Chronic Constipation",
    "Chronic Diarrhea", "Gallstones", "Tension Headache", "Peripheral Neuropathy", "Kidney Stones",
    "Kidney Infection (Pyelonephritis)", "Acne Vulgaris", "Eczema (Atopic Dermatitis)", "Psoriasis", "Contact Dermatitis",
    "Fungal Skin Infection", "Urticaria (Hives)", "Osteoarthritis", "Rheumatoid Arthritis", "Osteoporosis",
    "Gout", "Muscle Strain", "Vitamin B12 Deficiency", "Vitamin D Deficiency", "Sickle Cell Disease",
    "Generalized Anxiety", "Depressive Symptoms", "Chronic Stress & Burnout", "Insomnia & Sleep Disorder", "Metabolic Syndrome"
]

# Clinically realistic primary symptom map
disease_symptom_map = {
    # Original 1-25
    "Diabetes": ['high_blood_sugar', 'frequent_urination', 'fatigue', 'weight_loss', 'blurred_vision', 'excessive_hunger'],
    "Hypertension": ['high_blood_pressure', 'headache', 'dizziness'],
    "Heart Disease": ['chest_pain', 'shortness_of_breath', 'fatigue', 'palpitations'],
    "Asthma": ['shortness_of_breath', 'wheezing', 'cough_with_sputum', 'dry_cough'],
    "Pneumonia": ['fever', 'cough_with_sputum', 'chest_pain', 'shortness_of_breath', 'chills'],
    "Tuberculosis": ['cough_with_sputum', 'hemoptysis', 'fever', 'sweats', 'weight_loss'],
    "COVID-19": ['fever', 'shortness_of_breath', 'cough_with_sputum', 'fatigue', 'loss_of_smell'],
    "Influenza": ['fever', 'chills', 'headache', 'joint_pain', 'fatigue', 'muscle_pain'],
    "Dengue": ['fever', 'joint_pain', 'headache', 'fatigue', 'nausea', 'skin_rash'],
    "Malaria": ['fever', 'chills', 'sweats', 'headache', 'nausea'],
    "Typhoid": ['fever', 'abdominal_pain', 'headache', 'fatigue', 'nausea', 'diarrhea'],
    "Migraine": ['headache', 'nausea', 'vomiting', 'dizziness'],
    "Epilepsy": ['seizures', 'dizziness', 'headache'],
    "Parkinson's Disease": ['resting_tremor', 'fatigue', 'dizziness'],
    "Alzheimer's Disease": ['memory_loss', 'fatigue'],
    "COPD": ['shortness_of_breath', 'cough_with_sputum', 'wheezing', 'fatigue'],
    "Bronchitis": ['cough_with_sputum', 'shortness_of_breath', 'fever', 'fatigue', 'sore_throat'],
    "Gastritis": ['heartburn', 'nausea', 'vomiting', 'abdominal_pain'],
    "Hepatitis": ['jaundice', 'fatigue', 'nausea', 'abdominal_pain'],
    "Fatty Liver Disease": ['right_upper_quadrant_pain', 'fatigue', 'abdominal_pain'],
    "Chronic Kidney Disease": ['fatigue', 'flank_pain', 'frequent_urination', 'leg_swelling'],
    "Urinary Tract Infection (UTI)": ['dysuria', 'frequent_urination', 'flank_pain', 'fever', 'blood_in_urine'],
    "Anemia": ['fatigue', 'dizziness', 'shortness_of_breath', 'palpitations'],
    "Hypothyroidism": ['fatigue', 'cold_intolerance', 'weight_gain', 'hair_thinning'],
    "Hyperthyroidism": ['palpitations', 'heat_intolerance', 'weight_loss', 'sweats'],

    # Expanded 26-65
    "Common Cold": ['runny_nose', 'sneezing', 'sore_throat', 'dry_cough'],
    "Allergic Rhinitis": ['runny_nose', 'sneezing', 'itching', 'nasal_congestion'],
    "Sinusitis": ['nasal_congestion', 'headache', 'cough_with_sputum', 'fever'],
    "Heart Failure": ['shortness_of_breath', 'leg_swelling', 'fatigue', 'palpitations'],
    "Arrhythmia": ['palpitations', 'dizziness', 'shortness_of_breath', 'chest_pain'],
    "Angina Pectoris": ['chest_pain', 'shortness_of_breath', 'fatigue'],
    "Peripheral Artery Disease": ['muscle_pain', 'numbness_tingling', 'fatigue'],
    "Prediabetes": ['high_blood_sugar', 'frequent_urination', 'fatigue'],
    "Obesity": ['shortness_of_breath', 'fatigue', 'joint_pain', 'weight_gain'],
    "Polycystic Ovary Syndrome (PCOS)": ['weight_gain', 'acne_breakouts', 'hair_thinning', 'fatigue'],
    "GERD (Acid Reflux)": ['heartburn', 'abdominal_pain', 'nausea', 'sore_throat'],
    "Peptic Ulcer Disease": ['abdominal_pain', 'heartburn', 'nausea', 'vomiting'],
    "Gastroenteritis": ['diarrhea', 'vomiting', 'abdominal_pain', 'fever', 'nausea'],
    "Irritable Bowel Syndrome (IBS)": ['abdominal_pain', 'bloating', 'diarrhea', 'constipation'],
    "Chronic Constipation": ['constipation', 'bloating', 'abdominal_pain'],
    "Chronic Diarrhea": ['diarrhea', 'abdominal_pain', 'fatigue', 'nausea'],
    "Gallstones": ['right_upper_quadrant_pain', 'abdominal_pain', 'nausea', 'vomiting'],
    "Tension Headache": ['headache', 'muscle_pain', 'fatigue'],
    "Peripheral Neuropathy": ['numbness_tingling', 'muscle_pain', 'fatigue'],
    "Kidney Stones": ['flank_pain', 'dysuria', 'blood_in_urine', 'nausea'],
    "Kidney Infection (Pyelonephritis)": ['fever', 'chills', 'flank_pain', 'dysuria'],
    "Acne Vulgaris": ['acne_breakouts', 'skin_rash'],
    "Eczema (Atopic Dermatitis)": ['itching', 'skin_rash', 'skin_flaking'],
    "Psoriasis": ['skin_rash', 'skin_flaking', 'joint_pain'],
    "Contact Dermatitis": ['skin_rash', 'itching', 'localized_swelling'],
    "Fungal Skin Infection": ['itching', 'skin_rash', 'skin_flaking'],
    "Urticaria (Hives)": ['hives_welts', 'itching', 'localized_swelling'],
    "Osteoarthritis": ['joint_pain', 'joint_stiffness'],
    "Rheumatoid Arthritis": ['joint_pain', 'joint_stiffness', 'localized_swelling', 'fatigue'],
    "Osteoporosis": ['back_pain', 'joint_pain'],
    "Gout": ['joint_pain', 'localized_swelling', 'skin_rash'],
    "Muscle Strain": ['muscle_pain', 'localized_swelling', 'back_pain'],
    "Vitamin B12 Deficiency": ['fatigue', 'numbness_tingling', 'dizziness', 'memory_loss'],
    "Vitamin D Deficiency": ['fatigue', 'joint_pain', 'muscle_pain', 'depressed_mood'],
    "Sickle Cell Disease": ['joint_pain', 'fatigue', 'shortness_of_breath', 'fever'],
    "Generalized Anxiety": ['anxiety_nervousness', 'palpitations', 'sleep_disturbance', 'muscle_pain'],
    "Depressive Symptoms": ['depressed_mood', 'fatigue', 'sleep_disturbance', 'weight_loss'],
    "Chronic Stress & Burnout": ['fatigue', 'headache', 'sleep_disturbance', 'anxiety_nervousness'],
    "Insomnia & Sleep Disorder": ['sleep_disturbance', 'fatigue', 'headache'],
    "Metabolic Syndrome": ['high_blood_sugar', 'high_blood_pressure', 'weight_gain', 'fatigue']
}

# Generate Controlled Synthetic Educational Dataset (120 samples per class = 7,800 records)
np.random.seed(42)
records = []
samples_per_disease = 120

for dis in diseases:
    primary_syms = disease_symptom_map[dis]
    for _ in range(samples_per_disease):
        row = {sk: 0 for sk in symptom_keys}
        
        # 80% probability for primary symptoms to simulate clinical presentation variation
        for ps in primary_syms:
            if np.random.rand() < 0.80:
                row[ps] = 1
                
        # 4% realistic background noise probability for non-disease symptoms
        for sk in symptom_keys:
            if sk not in primary_syms and np.random.rand() < 0.04:
                row[sk] = 1
                
        row['disease'] = dis
        records.append(row)

df_sym = pd.DataFrame(records)
df_sym.to_csv('ml/datasets/symptom_disease.csv', index=False)
print(f"Generated Synthetic Educational Dataset: {len(df_sym)} records across {len(diseases)} classes.")

X_s = df_sym.drop('disease', axis=1)
y_s = df_sym['disease']

X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(
    X_s, y_s, test_size=0.2, random_state=42, stratify=y_s
)

symptom_models = {
    'Random Forest': RandomForestClassifier(n_estimators=120, max_depth=16, random_state=42),
    'Decision Tree': DecisionTreeClassifier(max_depth=16, random_state=42),
    'Naive Bayes': MultinomialNB(alpha=1.0),
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
    prec_weighted = float(precision_score(y_s_test, y_pred, average='weighted', zero_division=0))
    rec_weighted = float(recall_score(y_s_test, y_pred, average='weighted', zero_division=0))
    f1_weighted = float(f1_score(y_s_test, y_pred, average='weighted', zero_division=0))
    
    prec_macro = float(precision_score(y_s_test, y_pred, average='macro', zero_division=0))
    rec_macro = float(recall_score(y_s_test, y_pred, average='macro', zero_division=0))
    f1_macro = float(f1_score(y_s_test, y_pred, average='macro', zero_division=0))
    
    cm = confusion_matrix(y_s_test, y_pred, labels=diseases).tolist()
    
    # Per-class metrics
    class_report = classification_report(y_s_test, y_pred, labels=diseases, output_dict=True, zero_division=0)
    
    symptom_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec_weighted, 4),
        'recall': round(rec_weighted, 4),
        'f1_score': round(f1_weighted, 4),
        'macro_precision': round(prec_macro, 4),
        'macro_recall': round(rec_macro, 4),
        'macro_f1': round(f1_macro, 4),
        'confusion_matrix': cm,
        'per_class_f1_avg': round(np.mean([class_report[d]['f1-score'] for d in diseases if d in class_report]), 4)
    }
    
    print(f"Evaluated {name}: Accuracy={acc*100:.2f}%, F1(weighted)={f1_weighted*100:.2f}%, F1(macro)={f1_macro*100:.2f}%")
    
    if acc > best_s_score:
        best_s_score = acc
        best_s_model = model
        best_s_name = name

# Save Serialized Model Artifact with Version Metadata
joblib.dump({
    'model': best_s_model,
    'symptom_keys': symptom_keys,
    'diseases': diseases,
    'disease_symptom_map': disease_symptom_map,
    'model_name': best_s_name,
    'model_version': 'Multi-Disease Prediction Model v2',
    'supported_classes_count': len(diseases),
    'supported_features_count': len(symptom_keys)
}, 'ml/models/symptom_disease_model.joblib', compress=3)

# Save Full Evaluation Report
evaluation_summary = {
    'model_metadata': {
        'version': 'v2.0',
        'model_name': 'Multi-Disease Prediction Model v2',
        'supported_classes': len(diseases),
        'supported_features': len(symptom_keys),
        'dataset_type': 'Synthetic educational dataset (controlled clinical presentation synthesis)',
        'records_count': len(df_sym),
        'test_split_ratio': 0.2,
        'random_seed': 42
    },
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
        'dataset_source': 'Synthesized Clinical Symptom Dataset (7,800 Controlled Patient Records)',
        'num_records': len(df_sym),
        'num_features': len(symptom_keys),
        'num_classes': len(diseases),
        'models': symptom_eval
    }
}

with open('ml/evaluation_results.json', 'w') as f:
    json.dump(evaluation_summary, f, indent=4)

print("\nFull ML Training & Evaluation Complete!")
print(f"Selected Diabetes Model: {best_d_name} (Accuracy: {best_d_score*100:.2f}%)")
print(f"Selected Heart Model: {best_h_name} (Accuracy: {best_h_score*100:.2f}%)")
print(f"Selected Multi-Symptom Disease Model: {best_s_name} (Accuracy: {best_s_score*100:.2f}%, Classes: {len(diseases)})")
