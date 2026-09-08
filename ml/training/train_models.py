import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib

os.makedirs('ml/datasets', exist_ok=True)
os.makedirs('ml/models', exist_ok=True)

# ----------------------------------------------------
# 1. GENERATE / LOAD DIABETES DATASET (Pima Indians format)
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
    
    # Calculate realistic log-odds outcome
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

# Train Diabetes Models
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
        y_proba = model.predict_proba(X_d_test_scaled)[:, 1]
    else:
        model.fit(X_d_train, y_d_train)
        y_pred = model.predict(X_d_test)
        y_proba = model.predict_proba(X_d_test)[:, 1]
        
    acc = float(accuracy_score(y_d_test, y_pred))
    prec = float(precision_score(y_d_test, y_pred, zero_division=0))
    rec = float(recall_score(y_d_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_d_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_d_test, y_proba))
    cm = confusion_matrix(y_d_test, y_pred).tolist()
    
    diabetes_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'confusion_matrix': cm
    }
    
    if acc > best_d_score:
        best_d_score = acc
        best_d_model = model
        best_d_name = name

# Save best Diabetes pipeline
joblib.dump({
    'model': best_d_model,
    'scaler': scaler_d if best_d_name == 'Logistic Regression' else None,
    'feature_names': list(X_d.columns),
    'model_name': best_d_name
}, 'ml/models/diabetes_model.joblib')


# ----------------------------------------------------
# 2. GENERATE / LOAD HEART DISEASE DATASET (UCI format)
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
    
    # Calculate realistic log-odds outcome
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

# Train Heart Models
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
        y_proba = model.predict_proba(X_h_test_scaled)[:, 1]
    else:
        model.fit(X_h_train, y_h_train)
        y_pred = model.predict(X_h_test)
        y_proba = model.predict_proba(X_h_test)[:, 1]
        
    acc = float(accuracy_score(y_h_test, y_pred))
    prec = float(precision_score(y_h_test, y_pred, zero_division=0))
    rec = float(recall_score(y_h_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_h_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_h_test, y_proba))
    cm = confusion_matrix(y_h_test, y_pred).tolist()
    
    heart_eval[name] = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'confusion_matrix': cm
    }
    
    if acc > best_h_score:
        best_h_score = acc
        best_h_model = model
        best_h_name = name

# Save best Heart pipeline
joblib.dump({
    'model': best_h_model,
    'scaler': scaler_h if best_h_name == 'Logistic Regression' else None,
    'feature_names': list(X_h.columns),
    'model_name': best_h_name
}, 'ml/models/heart_model.joblib')

# Save Evaluation Metrics
evaluation_summary = {
    'diabetes': {
        'selected_model': best_d_name,
        'models': diabetes_eval
    },
    'heart_disease': {
        'selected_model': best_h_name,
        'models': heart_eval
    }
}

with open('ml/evaluation_results.json', 'w') as f:
    json.dump(evaluation_summary, f, indent=4)

print("ML Training Complete!")
print(f"Selected Diabetes Model: {best_d_name} (Accuracy: {best_d_score*100:.2f}%)")
print(f"Selected Heart Model: {best_h_name} (Accuracy: {best_h_score*100:.2f}%)")
