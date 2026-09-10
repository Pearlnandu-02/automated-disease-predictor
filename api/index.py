import os
import sys
import json
import secrets
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease, predict_symptoms
from ml.vision.scanner import compute_vision_metrics
import base64
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Prevent caching on Vercel
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

DISEASES_DB = [
    {"id": 1, "name": "Diabetes", "category": "Endocrine", "short_description": "A chronic metabolic disease characterized by elevated blood glucose levels leading to vascular and organ complications.", "causes": "Insulin resistance or insufficient insulin production by pancreatic beta cells.", "risk_factors": "Obesity, physical inactivity, genetic predisposition, high-refined sugar diets.", "prevention": "Maintain healthy body weight, engage in 150 mins/week exercise, consume fiber-rich foods.", "management": "Blood glucose monitoring, dietary management, insulin therapy under physician guidance.", "when_to_seek_care": "Seek immediate care for severe confusion, rapid breathing, or blood glucose > 300 mg/dL."},
    {"id": 2, "name": "Hypertension", "category": "Cardiovascular", "short_description": "Long-term high blood pressure against arterial walls causing increased cardiac workload.", "causes": "Arterial stiffening, genetic factors, excessive sodium intake, renal dysfunction.", "risk_factors": "High sodium diet, chronic stress, smoking, excessive alcohol, family history.", "prevention": "Reduce salt intake, exercise regularly, manage stress, avoid tobacco.", "management": "Periodic blood pressure tracking, DASH diet, anti-hypertensive medications.", "when_to_seek_care": "Seek urgent care for blood pressure > 180/120 mm Hg or sudden severe headache/chest pain."},
    {"id": 3, "name": "Heart Disease", "category": "Cardiovascular", "short_description": "Range of cardiac conditions including coronary artery disease and heart muscle dysfunction.", "causes": "Atherosclerotic plaque accumulation narrowing coronary arteries.", "risk_factors": "High cholesterol, smoking, diabetes, hypertension, sedentary lifestyle.", "prevention": "Cardio-healthy diet, smoking cessation, lipid monitoring, regular physical activity.", "management": "Cardiac rehabilitation, lipid-lowering medication, lifestyle modification.", "when_to_seek_care": "Seek emergency care immediately for crushing chest pain, arm radiation, or severe shortness of breath."},
    {"id": 4, "name": "Asthma", "category": "Respiratory", "short_description": "Chronic inflammatory disease of airway passages causing episodic wheezing and bronchospasm.", "causes": "Environmental allergens, airway hyper-responsiveness, respiratory viral infections.", "risk_factors": "Family history, allergen exposure, air pollution, secondhand smoke.", "prevention": "Identify and avoid allergen triggers, use prophylactic inhalers as directed.", "management": "Inhaled corticosteroids, quick-relief bronchodilators, asthma action plan.", "when_to_seek_care": "Seek emergency care for severe chest tightness, inability to speak full sentences, or blue lips."},
    {"id": 5, "name": "Pneumonia", "category": "Respiratory", "short_description": "Inflammatory infection of pulmonary alveoli filled with fluid or purulent exudate.", "causes": "Bacterial (Streptococcus pneumoniae), viral (Influenza, RSV), or fungal pathogens.", "risk_factors": "Advanced age, immunocompromised status, chronic lung disease, smoking.", "prevention": "Pneumococcal vaccination, annual flu vaccine, hand hygiene.", "management": "Targeted antibiotic or antiviral therapy, adequate hydration, fever management.", "when_to_seek_care": "Seek urgent medical attention for high fever, chest pain during breathing, or severe oxygen drop."},
    {"id": 6, "name": "Tuberculosis", "category": "Respiratory / Infectious", "short_description": "Contagious bacterial infection affecting pulmonary tissue caused by Mycobacterium tuberculosis.", "causes": "Inhalation of airborne droplet nuclei containing M. tuberculosis.", "risk_factors": "Immunosuppression (HIV), close contact with active TB cases, malnutrition.", "prevention": "BCG vaccination where indicated, infection control in crowded environments.", "management": "Strict 6-month anti-tubercular drug regimen (DOTS protocol).", "when_to_seek_care": "Seek immediate evaluation for coughing up blood, persistent night sweats, or unexplained weight loss."},
    {"id": 7, "name": "COVID-19", "category": "Respiratory / Infectious", "short_description": "Acute infectious disease caused by the SARS-CoV-2 coronavirus variant.", "causes": "Respiratory transmission of SARS-CoV-2 viral particles.", "risk_factors": "Unvaccinated status, older age, underlying pulmonary/cardiac comorbidities.", "prevention": "Vaccination, indoor ventilation, mask usage during outbreaks, hand hygiene.", "management": "Symptomatic control, hydration, antiviral drugs for high-risk patients.", "when_to_seek_care": "Seek emergency care for persistent chest pressure, oxygen saturation < 94%, or confusion."},
    {"id": 8, "name": "Influenza", "category": "Respiratory / Infectious", "short_description": "Acute viral infection of upper and lower respiratory tracts caused by influenza viruses.", "causes": "Infection by Influenza A or B viral strains.", "risk_factors": "Seasonal outbreaks, immunocompromised health, extreme ages.", "prevention": "Annual influenza vaccination, hand washing, avoiding close contact with sick persons.", "management": "Rest, fluid intake, antiviral treatment (Oseltamivir) within 48 hours of onset.", "when_to_seek_care": "Seek medical attention if fever persists over 4 days or severe breathing difficulty develops."},
    {"id": 9, "name": "Dengue", "category": "Infectious / Tropical", "short_description": "Mosquito-borne viral infection causing severe flu-like illness and low blood platelets.", "causes": "Transmission of Dengue virus (DENV-1-4) by infected Aedes aegypti mosquitoes.", "risk_factors": "Living in tropical endemic areas, standing water reservoirs.", "prevention": "Mosquito repellent usage, eliminating standing water containers, wearing long clothing.", "management": "Supportive care, continuous hydration, monitoring blood platelet count.", "when_to_seek_care": "Seek emergency care for severe abdominal pain, persistent vomiting, or mucosal bleeding."},
    {"id": 10, "name": "Malaria", "category": "Infectious / Tropical", "short_description": "Life-threatening parasitic infection transmitted by female Anopheles mosquitoes.", "causes": "Plasmodium parasite infection (P. falciparum, P. vivax).", "risk_factors": "Travel to endemic tropical regions, lack of bednet protection.", "prevention": "Prophylactic antimalarial medication, insecticide-treated mosquito nets.", "management": "Artemisinin-based combination therapies (ACT) prescribed by physicians.", "when_to_seek_care": "Seek immediate medical attention for high cyclical fever, severe chills, or jaundice."},
    {"id": 11, "name": "Typhoid", "category": "Infectious / Gastrointestinal", "short_description": "Systemic bacterial fever caused by Salmonella enterica serovar Typhi.", "causes": "Ingestion of food or water contaminated with S. Typhi bacteria.", "risk_factors": "Poor sanitation, unhygienic street food, lack of clean drinking water.", "prevention": "Typhoid vaccination, drinking boiled/filtered water, hygienic food preparation.", "management": "Targeted oral/intravenous antibiotics and fever control.", "when_to_seek_care": "Seek medical care for continuous high fever, Rose spots on abdomen, or severe lethargy."},
    {"id": 12, "name": "Migraine", "category": "Neurological", "short_description": "Recurrent neurological headache disorder characterized by moderate-to-severe throbbing pain.", "causes": "Neurovascular reactivity, trigeminal nerve activation, serotonin level fluctuations.", "risk_factors": "Stress, hormonal changes, sleep disruption, dietary triggers.", "prevention": "Maintain consistent sleep schedules, stress reduction, trigger diary tracking.", "management": "Acute triptan therapy, preventive medications, dark room rest.", "when_to_seek_care": "Seek urgent evaluation for sudden thunderclap headache or facial numbness."},
    {"id": 13, "name": "Epilepsy", "category": "Neurological", "short_description": "Central nervous system disorder characterized by recurrent unprovoked electrical seizures.", "causes": "Abnormal brain electrical activity due to genetics, head trauma, stroke.", "risk_factors": "Family history, prior head injury, CNS infections.", "prevention": "Head injury prevention (helmets), consistent medication adherence.", "management": "Antiepileptic drugs (AEDs), regular neurological monitoring.", "when_to_seek_care": "Seek emergency services if a seizure lasts longer than 5 minutes."},
    {"id": 14, "name": "Parkinson's Disease", "category": "Neurological", "short_description": "Progressive neurodegenerative disorder characterized by loss of dopamine-producing brain cells.", "causes": "Degeneration of substantia nigra dopaminergic neurons.", "risk_factors": "Advanced age, male sex, pesticide/toxin exposure.", "prevention": "Regular aerobic exercise, neuroprotective lifestyle habits.", "management": "Levodopa/Carbidopa medication, physical therapy.", "when_to_seek_care": "Seek medical advice upon noticing resting hand tremors or gait disturbance."},
    {"id": 15, "name": "Alzheimer's Disease", "category": "Neurological", "short_description": "Progressive neurodegenerative disease causing memory impairment and cognitive decline.", "causes": "Accumulation of extracellular amyloid-beta plaques and tau tangles.", "risk_factors": "Age over 65, APOE-e4 gene, cardiovascular comorbidities.", "prevention": "Cardiovascular health management, lifelong mental stimulation.", "management": "Cholinesterase inhibitors, supportive cognitive care.", "when_to_seek_care": "Seek neurological assessment for progressive memory loss interfering with daily living."},
    {"id": 16, "name": "COPD", "category": "Respiratory", "short_description": "Progressive airflow limitation caused by emphysema and chronic bronchitis.", "causes": "Long-term exposure to irritating gases, primarily cigarette smoke.", "risk_factors": "Cigarette smoking, occupational dust exposure.", "prevention": "Complete smoking cessation, avoiding workplace irritants.", "management": "Inhaled bronchodilators, pulmonary rehabilitation.", "when_to_seek_care": "Seek immediate emergency care for severe breathlessness and cyanosis."},
    {"id": 17, "name": "Bronchitis", "category": "Respiratory", "short_description": "Inflammation of bronchial mucosal lining leading to productive cough.", "causes": "Viral respiratory infections or acute chemical irritants.", "risk_factors": "Smoking exposure, air pollution, weakened immunity.", "prevention": "Avoid smoking exposure, hand hygiene, vaccination.", "management": "Expectorants, hydration, rest.", "when_to_seek_care": "Seek medical consultation if cough persists over 3 weeks or sputum contains blood."},
    {"id": 18, "name": "Gastritis", "category": "Gastrointestinal", "short_description": "Inflammation or erosion of the protective gastric mucosal lining.", "causes": "Helicobacter pylori bacterial infection, chronic NSAID use, excessive alcohol.", "risk_factors": "Frequent painkiller use, severe physiological stress.", "prevention": "Limit NSAID usage, avoid excessive alcohol and spicy trigger foods.", "management": "Proton pump inhibitors (PPIs), antacids, H. pylori eradication.", "when_to_seek_care": "Seek immediate care for vomiting blood or dark tarry stools."},
    {"id": 19, "name": "Hepatitis", "category": "Gastrointestinal / Hepatic", "short_description": "Inflammation of liver tissue caused primarily by viral pathogens or toxins.", "causes": "Hepatitis viruses (A, B, C, D, E), heavy alcohol consumption.", "risk_factors": "Unprotected exposure to bodily fluids, contaminated water.", "prevention": "Hepatitis A & B vaccination, clean water consumption.", "management": "Antiviral medications, supportive liver care, complete alcohol abstinence.", "when_to_seek_care": "Seek urgent medical attention for yellowing skin/eyes (jaundice)."},
    {"id": 20, "name": "Fatty Liver Disease", "category": "Gastrointestinal / Hepatic", "short_description": "Excessive accumulation of triglycerides within hepatic cells.", "causes": "Metabolic dysfunction, insulin resistance, high fructose intake.", "risk_factors": "Obesity, type 2 diabetes, high cholesterol.", "prevention": "Weight reduction (7-10%), low-carb diet, regular exercise.", "management": "Dietary modification, lifestyle intervention.", "when_to_seek_care": "Seek medical evaluation for persistent right upper quadrant discomfort."},
    {"id": 21, "name": "Chronic Kidney Disease", "category": "Renal", "short_description": "Gradual loss of renal filtration function over months to years.", "causes": "Uncontrolled diabetes mellitus, long-standing hypertension.", "risk_factors": "Diabetes, hypertension, family history of renal disease.", "prevention": "Strict blood sugar and blood pressure control.", "management": "ACE inhibitors, renal diet, dialysis in advanced stages.", "when_to_seek_care": "Seek medical evaluation for swelling in legs/ankles or decreased urine output."},
    {"id": 22, "name": "Urinary Tract Infection (UTI)", "category": "Renal / Urological", "short_description": "Infection of urinary structures, most commonly the urinary bladder.", "causes": "Bacterial colonization (E. coli) ascending through urethra.", "risk_factors": "Female anatomy, inadequate hydration, catheterization.", "prevention": "Adequate fluid intake, personal hygiene.", "management": "Targeted antibiotic therapy, increased water intake.", "when_to_seek_care": "Seek urgent medical attention for high fever or flank pain."},
    {"id": 23, "name": "Anemia", "category": "Hematological", "short_description": "Deficiency in healthy red blood cells or hemoglobin concentration.", "causes": "Iron deficiency, vitamin B12 deficiency, chronic blood loss.", "risk_factors": "Inadequate iron diet, heavy menstrual bleeding.", "prevention": "Iron-rich balanced diet, vitamin C intake.", "management": "Iron/vitamin supplementation.", "when_to_seek_care": "Seek immediate care for severe shortness of breath or dizziness."},
    {"id": 24, "name": "Hypothyroidism", "category": "Endocrine", "short_description": "Underactive thyroid gland producing insufficient thyroid hormones.", "causes": "Hashimoto autoimmune thyroiditis, iodine deficiency.", "risk_factors": "Female sex, middle age, autoimmune conditions.", "prevention": "Adequate dietary iodine intake, TSH screening.", "management": "Daily levothyroxine hormone replacement therapy.", "when_to_seek_care": "Seek medical review for unexplained weight gain, extreme fatigue."},
    {"id": 25, "name": "Hyperthyroidism", "category": "Endocrine", "short_description": "Overactive thyroid gland producing excessive thyroid hormones.", "causes": "Graves autoimmune disease, toxic goiter.", "risk_factors": "Female sex, family history of Graves disease.", "prevention": "Regular thyroid monitoring.", "management": "Anti-thyroid medications, beta-blockers.", "when_to_seek_care": "Seek immediate medical attention for rapid irregular heart rate (palpitations)."}
]

def render_page(content_html, **kwargs):
    user = session.get('user')
    base_template = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Healthcare - Intelligent Disease Prediction & Health Assistance System</title>
    <!-- Early theme initializer to prevent FOUC -->
    <script>
        (function() {
            var saved = localStorage.getItem('ai_healthcare_theme');
            var systemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            var theme = saved ? saved : (systemDark ? 'dark' : 'dark');
            document.documentElement.setAttribute('data-theme', theme);
        })();
    </script>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0f1d;
            --bg-secondary: #0f172a;
            --card-bg: #131d33;
            --card-border: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-primary: #06b6d4;
            --accent-secondary: #0d9488;
            --tile-bg-matte: #0e1626;
            --tile-border-matte: #1e293b;
            --tile-selected-bg: linear-gradient(135deg, rgba(6, 182, 212, 0.18) 0%, rgba(13, 148, 136, 0.28) 100%);
            --tile-selected-border: #06b6d4;
            --tile-selected-shadow: 0 8px 24px -4px rgba(6, 182, 212, 0.35);
            --gloss-reflection: linear-gradient(180deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.03) 50%, rgba(255, 255, 255, 0) 100%);
            --navbar-bg: rgba(10, 15, 29, 0.92);
            --footer-bg: #070a14;
        }

        [data-theme="light"] {
            --bg-primary: #f1f5f9;
            --bg-secondary: #e2e8f0;
            --card-bg: #ffffff;
            --card-border: #cbd5e1;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --accent-primary: #0284c7;
            --accent-secondary: #0d9488;
            --tile-bg-matte: #f8fafc;
            --tile-border-matte: #cbd5e1;
            --tile-selected-bg: linear-gradient(135deg, rgba(2, 132, 199, 0.12) 0%, rgba(13, 148, 136, 0.18) 100%);
            --tile-selected-border: #0284c7;
            --tile-selected-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.25);
            --gloss-reflection: linear-gradient(180deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0) 100%);
            --navbar-bg: rgba(255, 255, 255, 0.95);
            --footer-bg: #e2e8f0;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            transition: background-color 0.25s ease, color 0.25s ease;
        }

        .navbar-custom {
            background: var(--navbar-bg);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--card-border);
        }

        [data-theme="light"] .navbar-custom .nav-link {
            color: #1e293b !important;
        }

        [data-theme="light"] .navbar-brand {
            color: #0f172a !important;
        }

        .card-custom {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            transition: background 0.25s ease, border 0.25s ease;
        }

        .btn-info, .btn-primary, .btn-danger, .btn-success {
            color: #ffffff !important;
            font-weight: 600;
        }

        /* AI Scanner styles */
        .scanner-dropzone {
            border: 2px dashed var(--card-border);
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .scanner-dropzone:hover, .scanner-dropzone.dragover {
            border-color: var(--accent-primary);
            background: rgba(6, 182, 212, 0.08);
        }
        .scanner-preview-wrapper {
            position: relative;
            max-width: 480px;
            margin: 0 auto;
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid var(--card-border);
            background: #000;
        }
        .scanner-preview-img {
            width: 100%;
            max-height: 400px;
            object-fit: contain;
            display: block;
        }
        .scanner-laser-beam {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent 0%, #06b6d4 25%, #22d3ee 50%, #06b6d4 75%, transparent 100%);
            box-shadow: 0 0 16px 4px rgba(6, 182, 212, 0.85);
            z-index: 10;
            display: none;
        }
        .scanning-active .scanner-laser-beam {
            display: block;
            animation: laserScanSweep 2.2s ease-in-out infinite alternate;
        }
        @keyframes laserScanSweep {
            0% { top: 0%; }
            100% { top: calc(100% - 4px); }
        }
        .badge-category {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 18px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .badge-category-infection { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.35); }
        .badge-category-inflammation { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.35); }
        .badge-category-injury { background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.35); }
        .badge-category-rash { background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.35); }
        .badge-category-swelling { background: rgba(13, 148, 136, 0.15); color: #0d9488; border: 1px solid rgba(13, 148, 136, 0.35); }
        .badge-category-unable { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.35); }
        .metric-pill-card {
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 12px 14px;
            text-align: center;
        }
        .metric-pill-val { font-size: 1.3rem; font-weight: 800; color: var(--text-primary); }
        .metric-pill-lbl { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }
        .warning-sign-card {
            background: rgba(239, 68, 68, 0.05);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 4px solid #ef4444;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.88rem;
        }

        [data-theme="dark"] .bg-light {
            background-color: #131d33 !important;
            color: #f8fafc !important;
        }

        [data-theme="dark"] .form-control,
        [data-theme="dark"] .form-select {
            background-color: #0e1626;
            border-color: #1e293b;
            color: #f8fafc;
        }

        [data-theme="dark"] .form-control:focus,
        [data-theme="dark"] .form-select:focus {
            background-color: #131d33;
            color: #ffffff;
            border-color: #06b6d4;
            box-shadow: 0 0 0 0.25rem rgba(6, 182, 212, 0.25);
        }

        [data-theme="dark"] .form-select option {
            background-color: #0f172a;
            color: #f8fafc;
        }

        [data-theme="light"] .form-control,
        [data-theme="light"] .form-select {
            background-color: #ffffff;
            border-color: #cbd5e1;
            color: #0f172a;
        }

        [data-theme="light"] .form-select option {
            background-color: #ffffff;
            color: #0f172a;
        }

        .btn-primary-custom {
            background: var(--accent-secondary);
            color: #fff;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            padding: 10px 24px;
            transition: all 0.2s ease;
        }

        .btn-primary-custom:hover {
            background: #0f766e;
            color: #fff;
        }

        .disclaimer-banner {
            background: rgba(245, 158, 11, 0.12);
            border-left: 4px solid #f59e0b;
            color: #d97706;
            padding: 14px 18px;
            border-radius: 10px;
            font-size: 0.875rem;
        }

        [data-theme="dark"] .disclaimer-banner {
            color: #fbbf24;
        }

        .symptom-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
            gap: 12px;
        }

        /* Pure Tile Design (No Checkmarks, Matte to Glossy) */
        .symptom-tile {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 14px 16px;
            min-height: 54px;
            border-radius: 12px;
            cursor: pointer;
            background: var(--tile-bg-matte);
            border: 1.5px solid var(--tile-border-matte);
            overflow: hidden;
            user-select: none;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            outline: none;
        }

        .symptom-tile:hover {
            border-color: rgba(6, 182, 212, 0.5);
            transform: translateY(-1px);
        }

        .symptom-tile:focus-visible {
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.4);
            border-color: var(--accent-primary);
        }

        .symptom-tile input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
            pointer-events: none;
        }

        .symptom-tile-gloss {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 48%;
            background: var(--gloss-reflection);
            opacity: 0;
            pointer-events: none;
            border-radius: 10px 10px 0 0;
            transition: opacity 0.25s ease;
        }

        .symptom-tile-name {
            position: relative;
            z-index: 2;
            font-size: 0.90rem;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.3;
            transition: color 0.2s ease, font-weight 0.2s ease;
        }

        /* Selected State (Glossy + Elevated + Prominent Border, NO Checkmarks) */
        .symptom-tile.selected {
            background: var(--tile-selected-bg) !important;
            border-color: var(--tile-selected-border) !important;
            box-shadow: var(--tile-selected-shadow);
            transform: translateY(-2px);
        }

        .symptom-tile.selected .symptom-tile-gloss {
            opacity: 1;
        }

        .symptom-tile.selected .symptom-tile-name {
            font-weight: 700;
            color: var(--accent-primary);
        }

        /* Custom Range Slider */
        .form-range {
            cursor: pointer;
        }
        .form-range::-webkit-slider-thumb {
            background: var(--accent-primary);
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.6);
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }

        .slider-val-badge {
            display: inline-block;
            min-width: 48px;
            text-align: center;
            font-weight: 700;
            border-radius: 6px;
            padding: 2px 8px;
        }

        .counter-animating {
            display: inline-block;
            transition: transform 0.05s ease;
        }

        footer {
            margin-top: auto;
            background: var(--footer-bg);
            color: var(--text-muted);
            padding: 35px 0 20px;
            border-top: 1px solid var(--card-border);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-xl navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center me-4" href="/">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4 fw-bold">AI Healthcare<span class="text-info">.</span></span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-1 small fw-medium">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
                    <li class="nav-item"><a class="nav-link" href="/prediction">AI Prediction</a></li>
                    <li class="nav-item"><a class="nav-link" href="/scanner"><i class="bi bi-camera me-1"></i>Injury Scanner</a></li>
                    <li class="nav-item"><a class="nav-link" href="/assessment">Clinical Risk</a></li>
                    <li class="nav-item"><a class="nav-link" href="/simulator">Simulator</a></li>
                    <li class="nav-item"><a class="nav-link" href="/diseases">Diseases Library</a></li>
                    <li class="nav-item"><a class="nav-link" href="/symptoms">Symptoms Guide</a></li>
                    <li class="nav-item"><a class="nav-link" href="/prevention">Prevention</a></li>
                    <li class="nav-item"><a class="nav-link" href="/dataset-info">Dataset & AI</a></li>
                    
                    <!-- Theme Toggle Button -->
                    <li class="nav-item mx-xl-2">
                        <button type="button" class="btn btn-outline-secondary btn-sm rounded-pill px-3 theme-toggle-btn d-flex align-items-center gap-1" id="themeToggleBtn">
                            <i class="bi bi-moon-stars-fill theme-icon-dark text-info"></i>
                            <i class="bi bi-sun-fill theme-icon-light text-warning d-none"></i>
                            <span class="theme-text small fw-semibold">Dark</span>
                        </button>
                    </li>

                    {% if user %}
                        <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item ms-xl-1">
                            <a class="btn btn-outline-danger btn-sm rounded-pill px-3" href="/logout">Logout ({{ user.name }})</a>
                        </li>
                    {% else %}
                        <li class="nav-item ms-xl-1"><a class="btn btn-outline-info btn-sm rounded-pill px-3" href="/login">Login</a></li>
                        <li class="nav-item ms-xl-1"><a class="btn btn-info text-white btn-sm rounded-pill px-3" href="/register">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="py-4">
        <div class="container">
            """ + content_html + """
        </div>
    </main>

    <footer>
        <div class="container text-center">
            <p class="small text-muted mb-1">&copy; 2026 AI Healthcare – Intelligent Disease Prediction & Health Assistance System.</p>
            <p class="small text-warning">Educational College Project — Not a Medical Diagnosis System.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Theme Engine
        function initTheme() {
            var btn = document.getElementById('themeToggleBtn');
            if (!btn) return;
            var darkIcon = btn.querySelector('.theme-icon-dark');
            var lightIcon = btn.querySelector('.theme-icon-light');
            var text = btn.querySelector('.theme-text');

            function syncUI(theme) {
                if (theme === 'light') {
                    if (darkIcon) darkIcon.classList.add('d-none');
                    if (lightIcon) lightIcon.classList.remove('d-none');
                    if (text) text.textContent = 'Light';
                } else {
                    if (darkIcon) darkIcon.classList.remove('d-none');
                    if (lightIcon) lightIcon.classList.add('d-none');
                    if (text) text.textContent = 'Dark';
                }
            }

            var current = document.documentElement.getAttribute('data-theme') || 'dark';
            syncUI(current);

            btn.addEventListener('click', function(e) {
                e.preventDefault();
                var active = document.documentElement.getAttribute('data-theme') || 'dark';
                var next = active === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('ai_healthcare_theme', next);
                syncUI(next);
            });
        }

        // Accessible Symptom Tiles Interaction (No Checkmarks)
        function initTiles() {
            var tiles = document.querySelectorAll('.symptom-tile');
            var urlParams = new URLSearchParams(window.location.search);
            var pre = urlParams.get('symptom');

            tiles.forEach(function(tile) {
                var cb = tile.querySelector('input[type="checkbox"]');
                if (!cb) return;

                if (pre && cb.value.toLowerCase() === pre.toLowerCase()) {
                    cb.checked = true;
                }

                if (cb.checked) {
                    tile.classList.add('selected');
                    tile.setAttribute('aria-checked', 'true');
                } else {
                    tile.classList.remove('selected');
                    tile.setAttribute('aria-checked', 'false');
                }

                function toggleTile(e) {
                    if (e.target !== cb) {
                        e.preventDefault();
                        cb.checked = !cb.checked;
                    }
                    if (cb.checked) {
                        tile.classList.add('selected');
                        tile.setAttribute('aria-checked', 'true');
                    } else {
                        tile.classList.remove('selected');
                        tile.setAttribute('aria-checked', 'false');
                    }
                }

                tile.addEventListener('click', toggleTile);
                tile.addEventListener('keydown', function(e) {
                    if (e.key === ' ' || e.key === 'Enter') {
                        e.preventDefault();
                        toggleTile(e);
                    }
                });
            });
        }

        // Interactive Live Sliders with Badges (Touch & Mouse)
        function initSliders() {
            var sliders = document.querySelectorAll('.form-range');
            sliders.forEach(function(slider) {
                var targetId = 'val_' + (slider.getAttribute('data-target') || slider.name || slider.id);
                var badge = document.getElementById(targetId);
                function update() {
                    if (badge) {
                        badge.textContent = slider.value;
                    }
                }
                slider.addEventListener('input', update);
                slider.addEventListener('change', update);
                slider.addEventListener('touchmove', update);
                update();
            });
        }

        // Upward Digital Counter Animation
        function animateCounter(el, target, durationMs) {
            if (!el || isNaN(target)) return;
            var start = 0.0;
            var startTime = performance.now();
            function step(time) {
                var elapsed = time - startTime;
                var progress = Math.min(elapsed / durationMs, 1.0);
                var ease = 1 - Math.pow(1 - progress, 3);
                var cur = start + (target - start) * ease;
                el.textContent = cur.toFixed(1) + '%';
                if (progress < 1.0) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = target.toFixed(1) + '%';
                }
            }
            requestAnimationFrame(step);
        }

        document.addEventListener('DOMContentLoaded', function() {
            initTheme();
            initTiles();
            initSliders();
            var counters = document.querySelectorAll('.animate-counter');
            counters.forEach(function(c) {
                var tgt = parseFloat(c.getAttribute('data-target'));
                if (!isNaN(tgt)) {
                    animateCounter(c, tgt, 1300);
                }
            });
        });
    </script>
</body>
</html>
    """
    return render_template_string(base_template, **kwargs)

@app.route('/')
@app.route('/index.php')
@app.route('/api')
@app.route('/api/')
def home():
    content = """
    <div class="row align-items-center my-4 py-5 px-4 rounded-4 hero-banner shadow-lg">
        <div class="col-lg-7">
            <span class="badge bg-info text-dark fw-bold px-3 py-2 rounded-pill mb-3">AI & Machine Learning Platform</span>
            <h1 class="display-4 fw-extrabold text-white mb-3">Smarter Healthcare Powered by Artificial Intelligence</h1>
            <p class="lead text-light mb-4 opacity-90">
                Analyze symptoms and assess potential conditions across <strong>25 diseases</strong> using trained classification models.
            </p>
            <div class="d-flex flex-wrap gap-3">
                <a href="/prediction" class="btn btn-primary-custom btn-lg rounded-pill px-4">Check Symptoms Now</a>
                <a href="/diseases" class="btn btn-outline-light btn-lg rounded-pill px-4">Explore Diseases</a>
            </div>
        </div>
        <div class="col-lg-5 text-center mt-4 mt-lg-0">
            <div class="card-custom p-4 border-info">
                <i class="bi bi-heart-pulse-fill display-1 text-info mb-3"></i>
                <h4 class="fw-bold text-white mb-2">25 Disease Records</h4>
                <p class="small text-muted">Multi-symptom classification engine & structured medical database.</p>
            </div>
        </div>
    </div>

    <div class="disclaimer-banner my-4 p-4 text-center">
        <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
        <strong>Educational Disclaimer:</strong> This system provides educational/informational AI predictions only and is not a medical diagnosis. Please consult a qualified healthcare professional for diagnosis and treatment.
    </div>
    """
    return render_page(content)

@app.route('/about')
@app.route('/about.php')
@app.route('/api/about')
def about():
    content = """
    <div class="card-custom p-5 text-center my-4">
        <span class="badge bg-info text-dark px-3 py-1 rounded-pill mb-3">ABOUT PLATFORM</span>
        <h2 class="fw-bold text-white mb-3">AI Healthcare Platform Overview</h2>
        <p class="lead text-muted max-w-xl mx-auto mb-4">
            Demonstrating how Machine Learning assists healthcare users by analyzing symptoms and evaluating statistical likelihoods of 25 medical conditions.
        </p>
    </div>
    """
    return render_page(content)

@app.route('/prediction', methods=['GET', 'POST'])
@app.route('/prediction.php', methods=['GET', 'POST'])
@app.route('/api/prediction', methods=['GET', 'POST'])
def prediction():
    result = None
    selected_symptoms = []
    
    # Preselection via URL query string
    pre_symptom = request.args.get('symptom', '').strip()
    if pre_symptom:
        selected_symptoms.append(pre_symptom)
        
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        if selected_symptoms:
            result = predict_symptoms(selected_symptoms)

    symptoms_catalog = [
        ("General & Systemic", [
            ("fatigue", "Chronic Lethargy & Fatigue"),
            ("fever", "Fever (>100.4°F)"),
            ("chills", "Severe Chills & Rigors"),
            ("weight_loss", "Unexplained Rapid Weight Loss"),
            ("sweats", "Drenching Night Sweats"),
            ("joint_pain", "Severe Joint / Bone Pain")
        ]),
        ("Respiratory System", [
            ("shortness_of_breath", "Shortness of Breath (Dyspnea)"),
            ("cough_with_sputum", "Persistent Productive Cough"),
            ("wheezing", "Respiratory Wheezing"),
            ("hemoptysis", "Hemoptysis (Coughing Blood)")
        ]),
        ("Cardiovascular System", [
            ("chest_pain", "Chest Pain / Tightness"),
            ("high_blood_pressure", "Hypertension Indicators"),
            ("palpitations", "Rapid Heart Palpitations")
        ]),
        ("Neurological System", [
            ("headache", "Severe Throbbing Headache"),
            ("seizures", "Involuntary Seizures"),
            ("resting_tremor", "Resting Hand / Limb Tremor"),
            ("memory_loss", "Progressive Memory Decline")
        ]),
        ("Endocrine & Metabolic", [
            ("high_blood_sugar", "High Blood Sugar & Thirst"),
            ("cold_intolerance", "Cold Intolerance"),
            ("heat_intolerance", "Heat Intolerance / Sweating")
        ]),
        ("Gastrointestinal & Hepatic", [
            ("heartburn", "Heartburn / Acid Reflux"),
            ("jaundice", "Jaundice (Yellowing Eyes/Skin)"),
            ("right_upper_quadrant_pain", "Right Upper Quadrant Pain")
        ]),
        ("Renal & Urinary", [
            ("frequent_urination", "Frequent Urination"),
            ("dysuria", "Dysuria (Painful Urination)"),
            ("flank_pain", "Flank / Low Back Pain")
        ])
    ]

    tiles_html = ""
    for category, syms in symptoms_catalog:
        tiles_html += f'<div class="mb-4"><h6 class="text-info text-uppercase fw-bold small tracking-wider mb-3 pb-1 border-bottom border-secondary border-opacity-25"><i class="bi bi-activity me-1"></i> {category}</h6><div class="symptom-grid">'
        for key, name in syms:
            checked = "checked" if key in selected_symptoms else ""
            selected_cls = "selected" if key in selected_symptoms else ""
            aria_checked = "true" if key in selected_symptoms else "false"
            tiles_html += f"""
            <label class="symptom-tile {selected_cls}" tabindex="0" role="checkbox" aria-checked="{aria_checked}">
                <input type="checkbox" name="symptoms" value="{key}" class="symptom-checkbox" {checked}>
                <div class="symptom-tile-gloss"></div>
                <div class="symptom-tile-content">
                    <span class="symptom-tile-name">{name}</span>
                </div>
            </label>
            """
        tiles_html += '</div></div>'

    res_card = ""
    if result:
        prob = result.get('probability', 0.0)
        influencing = "".join([f'<span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 px-2 py-1 me-1">{s}</span>' for s in result.get('influencing_symptoms', [])])
        runner_ups_html = ""
        if result.get('runner_ups'):
            ru_items = "".join([f'<li class="d-flex justify-content-between py-1 border-bottom border-secondary border-opacity-10 text-muted"><span>{r.get("disease")}</span><span class="fw-bold text-white">{r.get("probability")}%</span></li>' for r in result.get('runner_ups', [])])
            runner_ups_html = f'<div class="p-3 bg-dark bg-opacity-40 rounded border border-secondary border-opacity-25 my-3 text-start small"><strong class="text-white d-block mb-2"><i class="bi bi-bar-chart me-1 text-warning"></i> Alternative Possibilities:</strong><ul class="list-unstyled mb-0">{ru_items}</ul></div>'

        res_card = f"""
        <div class="card-custom p-4 text-center border-info mt-4">
            <span class="badge bg-secondary mb-2 px-3 py-1">AI MODEL OUTPUT</span>
            <h5 class="text-muted text-uppercase fw-bold small">Possible condition based on AI model</h5>
            <h2 class="display-6 fw-bold text-white my-2">{result.get('prediction')}</h2>
            
            <div class="my-3 py-2 border-top border-bottom border-secondary border-opacity-25">
                <span class="display-3 fw-extrabold text-info counter-text animate-counter" data-target="{prob}">00.0%</span>
                <p class="small text-muted mb-0 mt-1">Model confidence (AI model output)</p>
            </div>

            <div class="p-3 bg-dark bg-opacity-60 rounded border border-secondary border-opacity-25 my-3 text-start small">
                <strong class="text-white d-block mb-1"><i class="bi bi-bounding-box-circles me-1 text-info"></i> Influencing Indicators:</strong>
                <div class="d-flex flex-wrap gap-1 mt-1">{influencing}</div>
            </div>

            {runner_ups_html}

            <div class="disclaimer-banner small text-start my-3">
                <h6 class="fw-bold mb-1 text-warning"><i class="bi bi-shield-exclamation me-1"></i> Medical Disclaimer</h6>
                {result.get('disclaimer')}
            </div>
        </div>
        """

    content = f"""
    <div class="row py-3">
        <div class="col-lg-12 text-center mb-4">
            <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">AI SYMPTOM CHECKER</span>
            <h1 class="display-5 fw-extrabold text-white">Intelligent Multi-Symptom Disease Prediction</h1>
            <p class="lead text-muted mx-auto" style="max-width: 750px;">
                Select your experienced indicators using our tactile symptom tiles. Unselected tiles are matte; selected tiles become glossy with real-time feedback.
            </p>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-7">
            <div class="card-custom p-4 p-md-5">
                <h4 class="fw-bold text-white mb-3 d-flex align-items-center">
                    <i class="bi bi-grid-3x3-gap-fill text-info me-2"></i> Select Present Symptoms
                </h4>
                <p class="small text-muted mb-4">Click tiles to toggle symptom presence:</p>
                <form method="POST" action="/prediction">
                    {tiles_html}
                    <div class="disclaimer-banner my-4">
                        <i class="bi bi-info-circle-fill me-1 text-info"></i> Predictions are generated using an automated Random Forest classifier. Results are strictly educational.
                    </div>
                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                        <i class="bi bi-cpu-fill me-2"></i> Submit Symptoms & Predict Condition
                    </button>
                </form>
            </div>
        </div>
        <div class="col-lg-5">
            {res_card if res_card else '''
            <div class="card-custom p-5 text-center h-100 d-flex flex-column justify-content-center align-items-center">
                <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                <h4 class="text-white fw-bold">Awaiting Symptom Selection</h4>
                <p class="text-muted small max-w-sm mb-0">
                    Click on the symptom tiles on the left to select your active indicators, then click "Submit Symptoms" to evaluate with our AI diagnostic model.
                </p>
            </div>
            '''}
        </div>
    </div>
    """
    return render_page(content)

@app.route('/assessment', methods=['GET', 'POST'])
@app.route('/assessment.php', methods=['GET', 'POST'])
@app.route('/api/assessment', methods=['GET', 'POST'])
def assessment():
    result = None
    disease_type = request.form.get('disease_type', 'diabetes') if request.method == 'POST' else request.args.get('type', 'diabetes')
    
    if request.method == 'POST':
        if disease_type == 'diabetes':
            input_data = {
                'Pregnancies': float(request.form.get('Pregnancies', 1)),
                'Glucose': float(request.form.get('Glucose', 120)),
                'BloodPressure': float(request.form.get('BloodPressure', 75)),
                'SkinThickness': float(request.form.get('SkinThickness', 22)),
                'Insulin': float(request.form.get('Insulin', 80)),
                'BMI': float(request.form.get('BMI', 28.4)),
                'DiabetesPedigreeFunction': float(request.form.get('DiabetesPedigreeFunction', 0.47)),
                'Age': float(request.form.get('Age', 42))
            }
        elif disease_type == 'heart':
            input_data = {
                'age': float(request.form.get('age', 52)),
                'sex': int(request.form.get('sex', 1)),
                'cp': int(request.form.get('cp', 0)),
                'trestbps': float(request.form.get('trestbps', 132)),
                'chol': float(request.form.get('chol', 235)),
                'fbs': int(request.form.get('fbs', 0)),
                'restecg': int(request.form.get('restecg', 0)),
                'thalach': float(request.form.get('thalach', 150)),
                'exang': int(request.form.get('exang', 0)),
                'oldpeak': float(request.form.get('oldpeak', 1.2)),
                'slope': int(request.form.get('slope', 1)),
                'ca': int(request.form.get('ca', 0)),
                'thal': int(request.form.get('thal', 2))
            }
        elif disease_type == 'hypertension':
            input_data = {
                'systolic': float(request.form.get('systolic', 135)),
                'diastolic': float(request.form.get('diastolic', 88)),
                'Age': float(request.form.get('Age', 48)),
                'BMI': float(request.form.get('BMI', 27.2)),
                'sodium': float(request.form.get('sodium', 2800)),
                'smoking': int(request.form.get('smoking', 0)),
                'stress': int(request.form.get('stress', 1))
            }
        elif disease_type == 'respiratory':
            input_data = {
                'Age': float(request.form.get('Age', 50)),
                'pack_years': float(request.form.get('pack_years', 8)),
                'dyspnea': int(request.form.get('dyspnea', 1)),
                'cough_weeks': float(request.form.get('cough_weeks', 3)),
                'env_exposure': int(request.form.get('env_exposure', 1))
            }
        else: # lifestyle
            input_data = {
                'age_group': int(request.form.get('age_group', 2)),
                'smoking': int(request.form.get('smoking', 0)),
                'physical_activity': int(request.form.get('physical_activity', 1)),
                'family_history': int(request.form.get('family_history', 0)),
                'bp_category': int(request.form.get('bp_category', 1)),
                'bmi_category': int(request.form.get('bmi_category', 2)),
                'blood_sugar': int(request.form.get('blood_sugar', 1)),
                'cholesterol': int(request.form.get('cholesterol', 1)),
                'diet_quality': int(request.form.get('diet_quality', 1)),
                'sleep_stress': int(request.form.get('sleep_stress', 1)),
                'chronic_conditions': int(request.form.get('chronic_conditions', 0))
            }
            
        result = predict_disease(disease_type, input_data)
        result['input_data'] = input_data
        result['disease_type'] = disease_type
        session['latest_assessment'] = result
        history = session.get('history', [])
        history.append({
            'disease': result.get('disease'),
            'risk_level': result.get('risk_level'),
            'probability': result.get('probability'),
            'timestamp': 'Recent'
        })
        session['history'] = history

    result_card = ""
    if result:
        risk_color = "success" if result.get('risk_level') == "LOW" else ("warning" if result.get('risk_level') == "MODERATE" else "danger")
        recs_html = "".join([f"<li class='mb-2'>{r}</li>" for r in result.get('recommendations', [])])
        feat_html = "".join([
            f"<div class='mb-2'><div class='d-flex justify-content-between small text-muted'><span>{k}</span><span>{round(v*100, 1)}%</span></div><div class='progress' style='height:6px;'><div class='progress-bar bg-info' style='width:{min(100, v*100)}%'></div></div></div>"
            for k, v in list(result.get('feature_importance', {}).items())[:5]
        ])
        
        result_card = f"""
        <div class="card-custom p-4 p-md-5 my-4 border-{risk_color}">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="badge bg-secondary">{result.get('disease')}</span>
                <span class="badge bg-{risk_color} fs-6 px-3 py-1">Risk Level: {result.get('risk_level')}</span>
            </div>
            <div class="text-center my-4">
                <h1 class="display-3 fw-extrabold text-{risk_color} mb-1">{result.get('probability')}%</h1>
                <p class="text-muted small">AI Model Statistical Risk Probability</p>
            </div>
            <div class="row g-4 my-2">
                <div class="col-md-6">
                    <h5 class="fw-bold text-white mb-3"><i class="bi bi-bar-chart-line text-info me-2"></i>Explainable AI (Top Risk Drivers)</h5>
                    {feat_html}
                </div>
                <div class="col-md-6">
                    <h5 class="fw-bold text-white mb-3"><i class="bi bi-check-circle text-success me-2"></i>Personalized Guidance</h5>
                    <ul class="text-muted small ps-3 mb-0">{recs_html}</ul>
                </div>
            </div>
            <div class="disclaimer-banner small my-3">{result.get('disclaimer')}</div>
            <div class="d-flex flex-wrap gap-2 mt-4">
                <a href="/simulator?type={disease_type}" class="btn btn-outline-info rounded-pill px-4">
                    <i class="bi bi-sliders me-1"></i> Open in What-If Simulator
                </a>
                <a href="/report" class="btn btn-outline-secondary rounded-pill px-4">
                    <i class="bi bi-printer me-1"></i> View Printable Summary
                </a>
                <a href="/assessment" class="btn btn-primary-custom rounded-pill px-4 ms-auto">New Assessment</a>
            </div>
        </div>
        """

    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <div class="card-custom p-4 p-md-5">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="bg-info bg-opacity-10 p-3 rounded-circle text-info me-3">
                        <i class="bi bi-clipboard-pulse fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold text-white mb-0">Clinical Health Risk Assessment</h3>
                        <p class="text-muted small mb-0">Evaluate quantitative biomarkers against trained Scikit-Learn classification pipelines</p>
                    </div>
                </div>

                <form method="POST" action="/assessment">
                    <div class="mb-4 bg-dark bg-opacity-50 p-3 rounded-3 border border-secondary border-opacity-25">
                        <label class="form-label fw-bold text-white fs-6 mb-2">
                            <i class="bi bi-activity text-info me-2"></i>Select Assessment Target Condition
                        </label>
                        <select class="form-select" id="disease_type" name="disease_type" onchange="toggleFields(this.value)">
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>1. Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>2. Heart Disease Risk Assessment (Cleveland Cardiac Model)</option>
                            <option value="hypertension" {'selected' if disease_type == 'hypertension' else ''}>3. Hypertension Risk Assessment (Hemodynamic Model)</option>
                            <option value="respiratory" {'selected' if disease_type == 'respiratory' else ''}>4. Chronic Respiratory Risk Assessment (Spirometry & Exposure)</option>
                            <option value="lifestyle" {'selected' if disease_type == 'lifestyle' else ''}>5. Comprehensive 11-Factor Health & Lifestyle Assessment</option>
                        </select>
                    </div>

                    <!-- 1. Diabetes Fields -->
                    <div id="diabetes_fields" class="condition-section" style="display: {'block' if disease_type == 'diabetes' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Biomarkers (Pima Clinical Model)</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">Glucose Level (mg/dL)</label>
                                <input type="number" step="0.1" name="Glucose" class="form-control" value="120">
                                <small class="text-muted">Normal fasting: 70-140 mg/dL</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="28.4">
                                <small class="text-muted">Normal: 18.5-24.9</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="BloodPressure" class="form-control" value="75">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Age (Years)</label>
                                <input type="number" name="Age" class="form-control" value="42">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Pregnancies</label>
                                <input type="number" name="Pregnancies" class="form-control" value="1">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Insulin Level (mu U/ml)</label>
                                <input type="number" step="0.1" name="Insulin" class="form-control" value="80">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Skin Thickness (mm)</label>
                                <input type="number" step="0.1" name="SkinThickness" class="form-control" value="22">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Diabetes Pedigree Function</label>
                                <input type="number" step="0.001" name="DiabetesPedigreeFunction" class="form-control" value="0.47">
                            </div>
                        </div>
                    </div>

                    <!-- 2. Heart Fields -->
                    <div id="heart_fields" class="condition-section" style="display: {'block' if disease_type == 'heart' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Cardiovascular Biomarkers (Cleveland Cardiac Model)</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">Age (Years)</label>
                                <input type="number" name="age" class="form-control" value="52">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Sex</label>
                                <select name="sex" class="form-select"><option value="1">Male</option><option value="0">Female</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Chest Pain Type</label>
                                <select name="cp" class="form-select"><option value="0">Typical Angina (0)</option><option value="1">Atypical Angina (1)</option><option value="2">Non-anginal Pain (2)</option><option value="3">Asymptomatic (3)</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Resting Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="trestbps" class="form-control" value="132">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Serum Cholesterol (mg/dL)</label>
                                <input type="number" step="0.1" name="chol" class="form-control" value="235">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Max Heart Rate Achieved</label>
                                <input type="number" step="0.1" name="thalach" class="form-control" value="150">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Exercise-Induced Angina</label>
                                <select name="exang" class="form-select"><option value="0">No</option><option value="1">Yes</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">ST Depression (Oldpeak)</label>
                                <input type="number" step="0.1" name="oldpeak" class="form-control" value="1.2">
                            </div>
                        </div>
                    </div>

                    <!-- 3. Hypertension Fields -->
                    <div id="hypertension_fields" class="condition-section" style="display: {'block' if disease_type == 'hypertension' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-speedometer2 me-2 text-warning"></i>Hypertension & Hemodynamic Biomarkers</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">Systolic Blood Pressure (mm Hg)</label>
                                <input type="number" step="1" name="systolic" class="form-control" value="135">
                                <small class="text-muted">Target: &lt;120 mm Hg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Diastolic Blood Pressure (mm Hg)</label>
                                <input type="number" step="1" name="diastolic" class="form-control" value="88">
                                <small class="text-muted">Target: &lt;80 mm Hg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="27.2">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Daily Dietary Sodium (mg/day)</label>
                                <input type="number" step="50" name="sodium" class="form-control" value="2800">
                                <small class="text-muted">AHA recommendation: &lt;2,300 mg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Smoking Status</label>
                                <select name="smoking" class="form-select">
                                    <option value="0">Non-Smoker</option>
                                    <option value="1">Occasional / Former</option>
                                    <option value="2">Regular Smoker</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Perceived Stress Level</label>
                                <select name="stress" class="form-select">
                                    <option value="0">Low Stress</option>
                                    <option value="1" selected>Moderate Stress</option>
                                    <option value="2">High / Chronic Stress</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- 4. Respiratory Fields -->
                    <div id="respiratory_fields" class="condition-section" style="display: {'block' if disease_type == 'respiratory' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-wind me-2 text-primary"></i>Respiratory & Pulmonary Risk Profile</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">Smoking Pack-Years</label>
                                <input type="number" step="0.5" name="pack_years" class="form-control" value="8">
                                <small class="text-muted">Packs per day &times; years smoked</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Dyspnea / Breathlessness Scale</label>
                                <select name="dyspnea" class="form-select">
                                    <option value="0">Grade 0: None except strenuous exercise</option>
                                    <option value="1" selected>Grade 1: Short of breath when hurrying</option>
                                    <option value="2">Grade 2: Walks slower than peers due to breathlessness</option>
                                    <option value="3">Grade 3: Stops for breath after 100 meters</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Chronic Cough Duration (Weeks)</label>
                                <input type="number" step="1" name="cough_weeks" class="form-control" value="3">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Environmental / Dust Exposure</label>
                                <select name="env_exposure" class="form-select">
                                    <option value="0">Low / Clean indoor</option>
                                    <option value="1" selected>Moderate (Urban traffic / occasional dust)</option>
                                    <option value="2">High (Occupational chemical, fumes, heavy biomass)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- 5. Lifestyle Multi-Risk Fields (11 Factors) -->
                    <div id="lifestyle_fields" class="condition-section" style="display: {'block' if disease_type == 'lifestyle' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-person-lines-fill me-2 text-success"></i>11-Factor Health &amp; Lifestyle Multi-Risk Assessment</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">1. Age Group</label>
                                <select name="age_group" class="form-select">
                                    <option value="0">Under 30 years</option>
                                    <option value="1">30 - 45 years</option>
                                    <option value="2" selected>46 - 60 years</option>
                                    <option value="3">Over 60 years</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">2. Smoking &amp; Tobacco</label>
                                <select name="smoking" class="form-select">
                                    <option value="0">Never smoked</option>
                                    <option value="1">Former smoker</option>
                                    <option value="2">Current smoker (&lt; 1 pack/day)</option>
                                    <option value="3">Heavy smoker (&gt; 1 pack/day)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">3. Physical Activity Level</label>
                                <select name="physical_activity" class="form-select">
                                    <option value="3">Active (&gt; 150 mins/week)</option>
                                    <option value="2">Moderate (60 - 150 mins/week)</option>
                                    <option value="1" selected>Light (&lt; 60 mins/week)</option>
                                    <option value="0">Sedentary (No regular exercise)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">4. Family History of Chronic Disease</label>
                                <select name="family_history" class="form-select">
                                    <option value="0">No known family history</option>
                                    <option value="1">One first-degree relative</option>
                                    <option value="2">Multiple first-degree relatives</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">5. Blood Pressure Category</label>
                                <select name="bp_category" class="form-select">
                                    <option value="0">Optimal (&lt; 120/80 mm Hg)</option>
                                    <option value="1" selected>Elevated (120-129 / &lt;80)</option>
                                    <option value="2">Stage 1 Hypertension (130-139 / 80-89)</option>
                                    <option value="3">Stage 2 Hypertension (&ge; 140/90)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">6. BMI / Weight Category</label>
                                <select name="bmi_category" class="form-select">
                                    <option value="0">Normal weight (18.5 - 24.9)</option>
                                    <option value="1">Overweight (25.0 - 29.9)</option>
                                    <option value="2" selected>Obesity Class I (30.0 - 34.9)</option>
                                    <option value="3">Obesity Class II/III (&ge; 35.0)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">7. Blood Sugar Level</label>
                                <select name="blood_sugar" class="form-select">
                                    <option value="0">Normal (&lt; 100 mg/dL fasting)</option>
                                    <option value="1" selected>Impaired / Prediabetic (100 - 125 mg/dL)</option>
                                    <option value="2">Elevated / Diabetic range (&ge; 126 mg/dL)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">8. Cholesterol Profile</label>
                                <select name="cholesterol" class="form-select">
                                    <option value="0">Desirable (&lt; 200 mg/dL)</option>
                                    <option value="1" selected>Borderline high (200 - 239 mg/dL)</option>
                                    <option value="2">High (&ge; 240 mg/dL)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">9. Diet &amp; Nutritional Quality</label>
                                <select name="diet_quality" class="form-select">
                                    <option value="0">Healthy / Whole-food balanced</option>
                                    <option value="1" selected>Average / Mixed diet</option>
                                    <option value="2">High in processed foods &amp; sugar</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">10. Stress &amp; Sleep Health</label>
                                <select name="sleep_stress" class="form-select">
                                    <option value="0">Restful sleep (7-9h) &amp; low stress</option>
                                    <option value="1" selected>Occasional insomnia / moderate stress</option>
                                    <option value="2">Chronic short sleep (&lt; 6h) &amp; high stress</option>
                                </select>
                            </div>
                            <div class="col-md-12">
                                <label class="form-label text-light small">11. Existing Chronic Conditions</label>
                                <select name="chronic_conditions" class="form-select">
                                    <option value="0">None diagnosed</option>
                                    <option value="1">One chronic condition managed</option>
                                    <option value="2">Multiple chronic conditions</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="disclaimer-banner my-3 small">
                        <i class="bi bi-info-circle-fill me-1"></i> Data will be evaluated using our trained machine learning pipeline. Results are informational and educational only.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                        <i class="bi bi-cpu-fill me-2"></i> Compute AI Health Risk Assessment
                    </button>
                </form>

                <script>
                function toggleFields(val) {{
                    var ids = ['diabetes_fields', 'heart_fields', 'hypertension_fields', 'respiratory_fields', 'lifestyle_fields'];
                    ids.forEach(function(id) {{
                        var el = document.getElementById(id);
                        if (el) {{
                            el.style.display = (id === val + '_fields') ? 'block' : 'none';
                        }}
                    }});
                }}
                </script>
            </div>
            {result_card}
        </div>
    </div>
    """
    return render_page(content)

@app.route('/simulator', methods=['GET', 'POST'])
@app.route('/simulator.php', methods=['GET', 'POST'])
@app.route('/api/simulator', methods=['GET', 'POST'])
def simulator():
    disease_type = request.form.get('disease_type', 'diabetes') if request.method == 'POST' else request.args.get('type', 'diabetes')
    
    # 5 Models Support with Fixed Sliders & Exact Case Matching
    if disease_type == 'diabetes':
        glucose = float(request.form.get('Glucose', 145))
        bmi = float(request.form.get('BMI', 31.0))
        bp = float(request.form.get('BloodPressure', 82))
        age = float(request.form.get('Age') or request.form.get('age', 45))
        input_data = {
            'Pregnancies': 2,
            'Glucose': glucose,
            'BloodPressure': bp,
            'SkinThickness': 25,
            'Insulin': 90,
            'BMI': bmi,
            'DiabetesPedigreeFunction': 0.52,
            'Age': age
        }
    elif disease_type == 'heart':
        chol = float(request.form.get('chol', 250))
        trestbps = float(request.form.get('trestbps', 140))
        thalach = float(request.form.get('thalach', 130))
        age = float(request.form.get('age') or request.form.get('Age', 58))
        input_data = {
            'age': age,
            'sex': 1,
            'cp': 0,
            'trestbps': trestbps,
            'chol': chol,
            'fbs': 0,
            'restecg': 0,
            'thalach': thalach,
            'exang': 0,
            'oldpeak': 1.0,
            'slope': 1,
            'ca': 0,
            'thal': 2
        }
    elif disease_type == 'hypertension':
        systolic = float(request.form.get('systolic', 145))
        diastolic = float(request.form.get('diastolic', 92))
        bmi = float(request.form.get('BMI', 29.5))
        sodium = float(request.form.get('sodium', 3400))
        age = float(request.form.get('Age') or request.form.get('age', 52))
        input_data = {
            'systolic': systolic,
            'diastolic': diastolic,
            'BMI': bmi,
            'sodium': sodium,
            'Age': age,
            'smoking': 0,
            'stress': 1
        }
    elif disease_type == 'respiratory':
        pack_years = float(request.form.get('pack_years', 18))
        dyspnea = int(request.form.get('dyspnea', 2))
        cough_weeks = float(request.form.get('cough_weeks', 4))
        age = float(request.form.get('Age') or request.form.get('age', 56))
        input_data = {
            'Age': age,
            'pack_years': pack_years,
            'dyspnea': dyspnea,
            'cough_weeks': cough_weeks,
            'env_exposure': 1
        }
    else: # lifestyle
        activity = int(request.form.get('physical_activity', 1))
        sleep_stress = int(request.form.get('sleep_stress', 2))
        diet = int(request.form.get('diet_quality', 1))
        age = float(request.form.get('Age') or request.form.get('age', 46))
        input_data = {
            'age_group': 2 if age < 55 else 3,
            'smoking': 0,
            'physical_activity': activity,
            'family_history': 1,
            'bp_category': 1,
            'bmi_category': 2,
            'blood_sugar': 1,
            'cholesterol': 1,
            'diet_quality': diet,
            'sleep_stress': sleep_stress,
            'chronic_conditions': 0
        }

    sim_result = predict_disease(disease_type, input_data)
    risk_color = "success" if sim_result['risk_level'] == "LOW" else ("warning" if sim_result['risk_level'] == "MODERATE" else "danger")
    
    # Sliders markup based on selected model
    if disease_type == 'diabetes':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Fasting Glucose (mg/dL)</label>
                <span id="val_Glucose" class="slider-val-badge bg-info text-dark">{int(glucose)}</span>
            </div>
            <input type="range" class="form-range" name="Glucose" id="slider_glucose" data-target="Glucose" min="70" max="250" value="{int(glucose)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Body Mass Index (BMI)</label>
                <span id="val_BMI" class="slider-val-badge bg-info text-dark">{bmi:.1f}</span>
            </div>
            <input type="range" class="form-range" name="BMI" id="slider_bmi" data-target="BMI" min="15" max="50" step="0.5" value="{bmi}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Blood Pressure (mm Hg)</label>
                <span id="val_BloodPressure" class="slider-val-badge bg-info text-dark">{int(bp)}</span>
            </div>
            <input type="range" class="form-range" name="BloodPressure" id="slider_bp" data-target="BloodPressure" min="50" max="130" value="{int(bp)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'heart':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Serum Cholesterol (mg/dL)</label>
                <span id="val_chol" class="slider-val-badge bg-info text-dark">{int(chol)}</span>
            </div>
            <input type="range" class="form-range" name="chol" id="slider_chol" data-target="chol" min="120" max="400" value="{int(chol)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Resting Blood Pressure (mm Hg)</label>
                <span id="val_trestbps" class="slider-val-badge bg-info text-dark">{int(trestbps)}</span>
            </div>
            <input type="range" class="form-range" name="trestbps" id="slider_trestbps" data-target="trestbps" min="90" max="200" value="{int(trestbps)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Max Heart Rate (bpm)</label>
                <span id="val_thalach" class="slider-val-badge bg-info text-dark">{int(thalach)}</span>
            </div>
            <input type="range" class="form-range" name="thalach" id="slider_thalach" data-target="thalach" min="80" max="210" value="{int(thalach)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'hypertension':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Systolic Blood Pressure (mm Hg)</label>
                <span id="val_systolic" class="slider-val-badge bg-info text-dark">{int(systolic)}</span>
            </div>
            <input type="range" class="form-range" name="systolic" id="slider_systolic" data-target="systolic" min="90" max="200" value="{int(systolic)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Diastolic Blood Pressure (mm Hg)</label>
                <span id="val_diastolic" class="slider-val-badge bg-info text-dark">{int(diastolic)}</span>
            </div>
            <input type="range" class="form-range" name="diastolic" id="slider_diastolic" data-target="diastolic" min="60" max="120" value="{int(diastolic)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Daily Sodium Intake (mg)</label>
                <span id="val_sodium" class="slider-val-badge bg-info text-dark">{int(sodium)}</span>
            </div>
            <input type="range" class="form-range" name="sodium" id="slider_sodium" data-target="sodium" min="1000" max="5000" step="50" value="{int(sodium)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'respiratory':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Smoking Pack-Years</label>
                <span id="val_pack_years" class="slider-val-badge bg-info text-dark">{int(pack_years)}</span>
            </div>
            <input type="range" class="form-range" name="pack_years" id="slider_pack_years" data-target="pack_years" min="0" max="50" value="{int(pack_years)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Dyspnea Breathlessness Grade (0-3)</label>
                <span id="val_dyspnea" class="slider-val-badge bg-info text-dark">{int(dyspnea)}</span>
            </div>
            <input type="range" class="form-range" name="dyspnea" id="slider_dyspnea" data-target="dyspnea" min="0" max="3" value="{int(dyspnea)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Chronic Cough Duration (Weeks)</label>
                <span id="val_cough_weeks" class="slider-val-badge bg-info text-dark">{int(cough_weeks)}</span>
            </div>
            <input type="range" class="form-range" name="cough_weeks" id="slider_cough_weeks" data-target="cough_weeks" min="0" max="12" value="{int(cough_weeks)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    else: # lifestyle
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Physical Activity Grade (0=Sedentary, 3=High)</label>
                <span id="val_physical_activity" class="slider-val-badge bg-info text-dark">{int(activity)}</span>
            </div>
            <input type="range" class="form-range" name="physical_activity" id="slider_activity" data-target="physical_activity" min="0" max="3" value="{int(activity)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Sleep &amp; Stress Scale (0=Optimal, 2=Poor)</label>
                <span id="val_sleep_stress" class="slider-val-badge bg-info text-dark">{int(sleep_stress)}</span>
            </div>
            <input type="range" class="form-range" name="sleep_stress" id="slider_sleep_stress" data-target="sleep_stress" min="0" max="2" value="{int(sleep_stress)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Diet Quality (0=Balanced, 2=Unhealthy)</label>
                <span id="val_diet_quality" class="slider-val-badge bg-info text-dark">{int(diet)}</span>
            </div>
            <input type="range" class="form-range" name="diet_quality" id="slider_diet" data-target="diet_quality" min="0" max="2" value="{int(diet)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label text-white small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """

    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <div class="card-custom p-4 p-md-5 mb-4">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="bg-success bg-opacity-10 p-3 rounded-circle text-success me-3">
                        <i class="bi bi-sliders fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold text-white mb-0">What-If Clinical Risk Simulator</h3>
                        <p class="text-muted small mb-0">Simulate lifestyle or biometric adjustments to observe real-time risk score changes</p>
                    </div>
                </div>

                <form method="POST" action="/simulator">
                    <div class="mb-4">
                        <label class="form-label text-white fw-bold">Select Target Condition Model:</label>
                        <select name="disease_type" class="form-select" onchange="this.form.submit()">
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>1. Diabetes Risk Simulator (Pima Clinical Model)</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>2. Heart Disease Risk Simulator (Cleveland Cardiac Model)</option>
                            <option value="hypertension" {'selected' if disease_type == 'hypertension' else ''}>3. Hypertension Risk Simulator (Hemodynamic Model)</option>
                            <option value="respiratory" {'selected' if disease_type == 'respiratory' else ''}>4. Chronic Respiratory Risk Simulator</option>
                            <option value="lifestyle" {'selected' if disease_type == 'lifestyle' else ''}>5. Multi-Factor Lifestyle Risk Simulator</option>
                        </select>
                    </div>

                    <div class="row g-4 my-2">
                        {sliders_markup}
                    </div>

                    <button type="submit" class="btn btn-primary-custom w-100 py-3 mt-3">
                        <i class="bi bi-arrow-repeat me-2"></i> Recalculate Simulated Risk Score
                    </button>
                </form>

                <div class="card-custom p-4 text-center border-{risk_color} mt-4">
                    <span class="badge bg-secondary mb-2">SIMULATED RISK OUTPUT</span>
                    <h3 class="fw-bold text-white">{sim_result.get('disease')}</h3>
                    <h1 class="display-3 fw-extrabold text-{risk_color} my-2">{sim_result.get('probability')}%</h1>
                    <span class="badge bg-{risk_color} fs-6 px-3 py-1">Risk Category: {sim_result.get('risk_level')}</span>
                    <div class="disclaimer-banner small text-start my-3">{sim_result.get('disclaimer')}</div>
                </div>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/result')
@app.route('/result.php')
def result():
    return redirect('/assessment')

@app.route('/history')
@app.route('/history.php')
def history():
    records = session.get('history', [])
    rows = "".join([f"<tr><td>{r['disease']}</td><td><span class='badge bg-info'>{r['risk_level']}</span></td><td>{r['probability']}%</td><td>{r['timestamp']}</td></tr>" for r in records])
    if not rows:
        rows = "<tr><td colspan='4' class='text-center text-muted'>No previous assessments recorded in this session.</td></tr>"
    content = f"""
    <div class="card-custom p-4 p-md-5 my-4">
        <h3 class="fw-bold text-white mb-3">Assessment History Log</h3>
        <table class="table table-dark table-hover"><thead><tr><th>Condition</th><th>Risk Level</th><th>Probability</th><th>Time</th></tr></thead><tbody>{rows}</tbody></table>
        <a href="/assessment" class="btn btn-primary-custom rounded-pill mt-3">New Assessment</a>
    </div>
    """
    return render_page(content)

@app.route('/report')
@app.route('/report.php')
def report():
    res = session.get('latest_assessment', {
        'disease': 'Diabetes Risk Assessment',
        'risk_level': 'HIGH',
        'probability': 97.4,
        'recommendations': ['Maintain low glycemic diet.', 'Regular physical activity (30 mins/day).', 'Periodic blood glucose screening.'],
        'disclaimer': 'Educational informational report only. Consult a qualified medical practitioner.'
    })
    recs = "".join([f"<li class='mb-2'>{r}</li>" for r in res.get('recommendations', [])])
    return f"""
    <!DOCTYPE html><html><head><title>Health Assessment Report</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-4 p-md-5 bg-light text-dark">
        <div class="container" style="max-width:800px;background:#fff;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <h2 class="fw-bold mb-0">AI Healthcare Clinical Assessment Report</h2>
                <button onclick="window.print()" class="btn btn-primary rounded-pill px-4">Print / Save PDF</button>
            </div>
            <h4>Condition: {res.get('disease')}</h4>
            <p><strong>Predicted Risk Level:</strong> <span class="badge bg-danger">{res.get('risk_level')}</span></p>
            <p><strong>Statistical Probability Score:</strong> {res.get('probability')}%</p>
            <h5 class="mt-4">Personalized Recommendations:</h5>
            <ul>{recs}</ul>
            <div class="alert alert-warning mt-4">{res.get('disclaimer')}</div>
            <a href="/assessment" class="btn btn-outline-secondary mt-3">Back to Platform</a>
        </div>
    </body></html>
    """

@app.route('/diseases')
@app.route('/diseases.php')
@app.route('/api/diseases')
def diseases():
    items_html = "".join([f'<div class="col-md-6 col-lg-4"><div class="card-custom p-4 h-100"><span class="badge bg-info bg-opacity-20 text-info mb-2">{d["category"]}</span><h4 class="fw-bold text-white mb-2">{d["name"]}</h4><p class="small text-muted mb-3">{d["short_description"][:90]}...</p><a href="/disease/{d["id"]}" class="btn btn-outline-info btn-sm rounded-pill w-100">View Details</a></div></div>' for d in DISEASES_DB])
    content = f"""
    <h2 class="fw-bold text-white mb-4 text-center">Disease Information Database (25 Diseases)</h2>
    <div class="row g-4">{items_html}</div>
    """
    return render_page(content)

@app.route('/disease/<int:did>')
@app.route('/disease_detail.php')
@app.route('/api/disease/<int:did>')
def disease_detail(did=1):
    if not did or did == 1:
        did = request.args.get('id', type=int) or 1
    disease = next((d for d in DISEASES_DB if d['id'] == did), DISEASES_DB[0])
    content = f"""
    <div class="card-custom p-4 p-md-5 my-3">
        <span class="badge bg-info text-dark mb-2">{disease['category']}</span>
        <h1 class="display-5 fw-bold text-white mb-3">{disease['name']}</h1>
        <p class="lead text-muted mb-4">{disease['short_description']}</p>
        
        <h5 class="fw-bold text-white mb-2">Causes</h5>
        <p class="text-muted small mb-4">{disease['causes']}</p>
        
        <h5 class="fw-bold text-white mb-2">Risk Factors</h5>
        <p class="text-muted small mb-4">{disease['risk_factors']}</p>

        <h5 class="fw-bold text-white mb-2">Prevention</h5>
        <p class="text-muted small mb-4">{disease['prevention']}</p>

        <h5 class="fw-bold text-white mb-2">Management & Care</h5>
        <p class="text-muted small mb-4">{disease['management']}</p>
    </div>
    """
    return render_page(content)

@app.route('/symptoms')
@app.route('/symptoms_guide.php')
@app.route('/api/symptoms')
def symptoms_guide():
    symptoms_list = [
        {"key": "fatigue", "name": "Chronic Lethargy & Fatigue", "cat": "General", "icon": "bi-battery-half", "desc": "Persistent extreme physical exhaustion not resolved by rest.", "cond": "Anemia, Chronic Kidney Disease, Diabetes, Hypothyroidism"},
        {"key": "fever", "name": "Fever (>100.4°F / 38°C)", "cat": "General", "icon": "bi-thermometer-high", "desc": "Elevated core temperature signaling acute immune response or infection.", "cond": "Pneumonia, COVID-19, Malaria, Typhoid, UTI"},
        {"key": "chills", "name": "Severe Chills & Rigors", "cat": "General", "icon": "bi-snow", "desc": "Involuntary muscular shivering accompanied by intense cold sensations.", "cond": "Pneumonia, Malaria, Sepsis, Pyelonephritis"},
        {"key": "weight_loss", "name": "Unexplained Rapid Weight Loss", "cat": "General", "icon": "bi-graph-down-arrow", "desc": "Losing >5% body weight unintentionally without dietary changes.", "cond": "Type 1 Diabetes, Hyperthyroidism, Tuberculosis"},
        {"key": "shortness_of_breath", "name": "Shortness of Breath (Dyspnea)", "cat": "Respiratory", "icon": "bi-wind", "desc": "Labored respiration, air hunger, or inability to complete a breath.", "cond": "Asthma, COPD, Pneumonia, Heart Failure"},
        {"key": "cough_with_sputum", "name": "Persistent Productive Cough", "cat": "Respiratory", "icon": "bi-lungs", "desc": "Cough producing phlegm or mucus lasting longer than two weeks.", "cond": "Bacterial Pneumonia, Chronic Bronchitis, Asthma"},
        {"key": "wheezing", "name": "Respiratory Wheezing", "cat": "Respiratory", "icon": "bi-soundwave", "desc": "Whistling expiratory sound caused by narrowed bronchial passages.", "cond": "Bronchial Asthma, COPD, Allergic Bronchospasm"},
        {"key": "hemoptysis", "name": "Hemoptysis (Coughing Blood)", "cat": "Respiratory", "icon": "bi-exclamation-octagon", "desc": "Expectoration of blood or blood-tinged sputum from airways.", "cond": "Tuberculosis, Severe Pneumonia, Bronchiectasis"},
        {"key": "chest_pain", "name": "Chest Pain / Tightness", "cat": "Cardiovascular", "icon": "bi-heart-pulse-fill", "desc": "Retrosternal pressure, squeezing, or discomfort in the chest.", "cond": "Coronary Artery Disease, Myocardial Infarction, Angina"},
        {"key": "high_blood_pressure", "name": "Hypertension Indicators", "cat": "Cardiovascular", "icon": "bi-speedometer2", "desc": "Sustained arterial pressure >= 130/80 mmHg or acute elevations.", "cond": "Essential Hypertension, Chronic Kidney Disease"},
        {"key": "palpitations", "name": "Rapid Heart Palpitations", "cat": "Cardiovascular", "icon": "bi-activity", "desc": "Awareness of pounding, fluttering, or rapid irregular heartbeats.", "cond": "Arrhythmias, Hyperthyroidism, Severe Anemia, Anxiety"},
        {"key": "headache", "name": "Severe Throbbing Headache", "cat": "Neurological", "icon": "bi-headset-vr", "desc": "Intense cranial or temporal throbbing or pressure.", "cond": "Migraine, Severe Hypertension, Tension Cephalea"},
        {"key": "resting_tremor", "name": "Resting Hand / Limb Tremor", "cat": "Neurological", "icon": "bi-hand-index-thumb", "desc": "Rhythmic oscillatory movement of limbs while relaxed and resting.", "cond": "Parkinson's Disease, Essential Tremor, Hyperthyroidism"},
        {"key": "seizures", "name": "Involuntary Seizures", "cat": "Neurological", "icon": "bi-lightning-charge", "desc": "Uncontrolled cerebral electrical activity causing convulsions.", "cond": "Epilepsy, Severe Metabolic Disturbance, Stroke"},
        {"key": "memory_loss", "name": "Progressive Memory Decline", "cat": "Neurological", "icon": "bi-journal-medical", "desc": "Progressive short-term memory impairment and spatial disorientation.", "cond": "Alzheimer's Disease, Vascular Dementia, Vitamin B12 Deficiency"},
        {"key": "high_blood_sugar", "name": "High Blood Sugar & Polydipsia", "cat": "Endocrine", "icon": "bi-droplet", "desc": "Elevated blood glucose causing extreme thirst and frequent urination.", "cond": "Type 1 & Type 2 Diabetes, Metabolic Syndrome"},
        {"key": "cold_intolerance", "name": "Cold Intolerance", "cat": "Endocrine", "icon": "bi-thermometer-snow", "desc": "Abnormal extreme sensitivity to cool ambient temperatures.", "cond": "Hypothyroidism (Hashimoto's), Severe Anemia"},
        {"key": "heat_intolerance", "name": "Heat Intolerance / Sweating", "cat": "Endocrine", "icon": "bi-thermometer-sun", "desc": "Excessive sweating and distress in moderately warm environments.", "cond": "Hyperthyroidism (Graves' Disease), Autonomic Dysfunction"},
        {"key": "frequent_urination", "name": "Frequent Urination (Polyuria)", "cat": "Renal", "icon": "bi-clock-history", "desc": "Increased voiding frequency throughout the day and night.", "cond": "Diabetes Mellitus, UTI, Chronic Kidney Disease"},
        {"key": "dysuria", "name": "Dysuria (Painful Urination)", "cat": "Renal", "icon": "bi-shield-exclamation", "desc": "Burning or stinging discomfort in urethra while passing urine.", "cond": "Urinary Tract Infection (UTI), Nephrolithiasis"},
        {"key": "flank_pain", "name": "Flank / Low Back Pain", "cat": "Renal", "icon": "bi-activity", "desc": "Colicky or dull pain in lateral abdominal wall or lower back.", "cond": "Kidney Stones (Nephrolithiasis), Pyelonephritis"},
        {"key": "heartburn", "name": "Heartburn & Acid Reflux", "cat": "Digestive", "icon": "bi-fire", "desc": "Retrosternal burning sensation from stomach acid regurgitation.", "cond": "GERD, Gastritis, Peptic Ulcer Disease"},
        {"key": "jaundice", "name": "Jaundice (Yellowing Eyes/Skin)", "cat": "Digestive", "icon": "bi-eye-fill", "desc": "Yellowish skin and scleral discoloration from elevated bilirubin.", "cond": "Hepatitis (A, B, C), Cirrhosis, Gallstone Obstruction"},
        {"key": "right_upper_quadrant_pain", "name": "Right Upper Quadrant Pain", "cat": "Digestive", "icon": "bi-bandaid", "desc": "Ache or sharp spasms beneath the right lower ribcage.", "cond": "Cholecystitis, Gallstones, Acute Hepatitis"}
    ]

    cards_html = ""
    for s in symptoms_list:
        cards_html += f"""
        <div class="col-md-6 col-lg-4">
            <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between border border-secondary border-opacity-25">
                <div>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="p-2 bg-info bg-opacity-10 text-info rounded-circle"><i class="bi {s['icon']} fs-4"></i></div>
                        <span class="badge bg-secondary bg-opacity-40 text-info border border-info border-opacity-25">{s['cat']}</span>
                    </div>
                    <h5 class="fw-bold text-white mb-2">{s['name']}</h5>
                    <p class="small text-muted mb-3">{s['desc']}</p>
                    <div class="p-2 bg-dark bg-opacity-40 rounded small mb-3">
                        <strong class="text-white d-block mb-1">Commonly Associated:</strong>
                        <span class="text-muted">{s['cond']}</span>
                    </div>
                </div>
                <a href="/prediction?symptom={s['key']}" class="btn btn-outline-info btn-sm rounded-pill w-100 mt-2">
                    <i class="bi bi-cpu me-1"></i> Use this symptom in AI checker
                </a>
            </div>
        </div>
        """

    content = f"""
    <div class="row py-3 text-center">
        <div class="col-12 mb-4">
            <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">CLINICAL DIRECTORY</span>
            <h1 class="display-5 fw-extrabold text-white">Interactive Symptoms Guide & Clinical Index</h1>
            <p class="lead text-muted mx-auto" style="max-width: 780px;">
                Explore our clinically organized index of symptoms aligned directly with our machine learning classification model.
            </p>
        </div>
    </div>
    <div class="row g-4">{cards_html}</div>
    """
    return render_page(content)

@app.route('/prevention')
@app.route('/prevention.php')
@app.route('/api/prevention')
def prevention():
    lifestyle_cards = [
        ("bi-egg-fried", "Nutritional Balance", "Diet & Fuel", "Prioritize whole grains, colorful vegetables, lean proteins, and unsaturated fats while reducing sodium to <2,300 mg/day."),
        ("bi-lightning-charge-fill", "Physical Activity", "Movement", "Target at least 150 minutes of moderate aerobic exercise or 75 minutes of vigorous activity weekly with strength training."),
        ("bi-moon-stars-fill", "Restorative Sleep", "Recovery", "Aim for 7 to 9 hours of uninterrupted nocturnal sleep in a cool, dark room. Maintain regular circadian rhythms."),
        ("bi-droplet-fill", "Optimal Hydration", "Vital Fluids", "Drink 2 to 3 liters of fresh water daily to support kidney filtration, blood pressure homeostasis, and joint lubrication."),
        ("bi-heart-half", "Stress Management", "Nervous System", "Practice diaphragmatic breathing, mindfulness, and regular outdoor recreation to reduce chronic sympathetic cortisol elevation."),
        ("bi-shield-shaded", "Hygiene & Sanitation", "Infection Control", "Wash hands for at least 20 seconds with soap and water before meals and after transit to block microbial transmission."),
        ("bi-capsule", "Vaccination Awareness", "Immunization", "Keep routine vaccines current, including annual influenza boosters, COVID-19 immunizations, and tetanus toxoid boosters."),
        ("bi-clipboard2-pulse", "Regular Screenings", "Proactive Care", "Schedule annual health checkups to monitor fasting blood glucose, lipid panels, and resting blood pressure.")
    ]

    lifestyle_html = "".join([f"""
    <div class="col-md-6 col-lg-3">
        <div class="card-custom p-4 h-100 border border-secondary border-opacity-25">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <i class="bi {icon} text-info fs-3"></i>
                <span class="badge bg-secondary bg-opacity-40 text-info">{badge}</span>
            </div>
            <h5 class="fw-bold text-white mb-2">{title}</h5>
            <p class="small text-muted mb-0">{tip}</p>
        </div>
    </div>
    """ for icon, title, badge, tip in lifestyle_cards])

    content = f"""
    <div class="row py-3 text-center">
        <div class="col-12 mb-4">
            <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">PREVENTATIVE HEALTH</span>
            <h1 class="display-5 fw-extrabold text-white">Health Awareness & Disease Prevention</h1>
            <p class="lead text-muted mx-auto" style="max-width: 780px;">
                Evidence-based preventative practices, lifestyle foundations, and organ-specific risk reduction strategies.
            </p>
        </div>
    </div>

    <h3 class="fw-bold text-white mb-4"><i class="bi bi-compass text-info me-2"></i> Foundations of Healthy Living</h3>
    <div class="row g-4 mb-5">{lifestyle_html}</div>

    <!-- Emergency Triage Guidance -->
    <div class="card-custom p-4 p-md-5 my-4 border-danger" style="border-width: 2px;">
        <h4 class="fw-bold text-danger mb-3 d-flex align-items-center">
            <i class="bi bi-exclamation-octagon-fill me-2 fs-3"></i> Red-Flag Warning Signs: When to Seek Immediate Emergency Medical Care
        </h4>
        <div class="row g-3 text-muted small">
            <div class="col-md-3">
                <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Cardiac Symptoms:</strong> Crushing chest pressure, pain radiating to left arm or jaw, sudden cold sweat.
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Respiratory Distress:</strong> Inability to speak full sentences, severe shortness of breath, cyanosis (blue lips/fingertips).
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Neurological Emergencies:</strong> Sudden facial drooping, arm weakness, slurred speech (FAST stroke signs) or seizure > 5 mins.
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Systemic Sepsis:</strong> High fever > 103°F with confusion, drenching rigors, and rapid heart rate.
                </div>
            </div>
        </div>
        <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded mt-3 text-center">
            <span class="text-danger fw-bold small"><i class="bi bi-telephone-fill me-1"></i> If you experience severe emergency signs, call 911 / 112 or visit the nearest emergency room immediately.</span>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/dataset-info')
@app.route('/dataset_info.php')
@app.route('/api/dataset-info')
def dataset_info():
    content = """
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-3">Dataset & Large Data Handling Architecture</h2>
        <p class="text-muted small mb-4">Offline data preprocessing, separate dataset storage, lightweight joblib pipelines, and REST API inference microservices.</p>
    </div>
    """
    return render_page(content)

@app.route('/project-info')
@app.route('/project_info.php')
@app.route('/api/project-info')
def project_info():
    content = """
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-3">About College Project</h2>
        <p class="text-muted small">AI Healthcare – Intelligent Disease Prediction & Health Assistance System built with HTML5, CSS3, Bootstrap 5, JavaScript, PHP, MySQL, Python Scikit-Learn.</p>
    </div>
    """
    return render_page(content)

@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact.php', methods=['GET', 'POST'])
@app.route('/api/contact', methods=['GET', 'POST'])
def contact():
    content = """
    <div class="card-custom p-5 max-w-lg mx-auto my-4">
        <h2 class="fw-bold text-white mb-3">Contact & Academic Support</h2>
        <p class="text-muted small">Reach out to our project development team regarding academic submissions.</p>
    </div>
    """
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.php', methods=['GET', 'POST'])
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = {"name": "Academic Student", "email": "student@college.edu"}
        return redirect('/dashboard')
    content = """
    <div class="card-custom p-4 max-w-md mx-auto my-5">
        <h3 class="fw-bold text-white mb-3 text-center">Platform Login</h3>
        <form method="POST" action="/login">
            <div class="mb-3"><label class="form-label text-white">Email</label><input type="email" name="email" class="form-control" value="student@college.edu" required></div>
            <div class="mb-3"><label class="form-label text-white">Password</label><input type="password" name="password" class="form-control" value="password123" required></div>
            <button type="submit" class="btn btn-primary-custom w-100 py-2">Login to Dashboard</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.php', methods=['GET', 'POST'])
@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user'] = {"name": request.form.get('name', 'Student User'), "email": request.form.get('email', 'user@college.edu')}
        return redirect('/dashboard')
    content = """
    <div class="card-custom p-4 max-w-md mx-auto my-5">
        <h3 class="fw-bold text-white mb-3 text-center">User Registration</h3>
        <form method="POST" action="/register">
            <div class="mb-3"><label class="form-label text-white">Full Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="mb-3"><label class="form-label text-white">Email</label><input type="email" name="email" class="form-control" required></div>
            <div class="mb-3"><label class="form-label text-white">Password</label><input type="password" name="password" class="form-control" required></div>
            <button type="submit" class="btn btn-primary-custom w-100 py-2">Create Account</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/logout')
@app.route('/logout.php')
@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
@app.route('/dashboard.php')
@app.route('/api/dashboard')
def dashboard():
    user = session.get('user', {"name": "Academic Student", "email": "student@college.edu"})
    content = f"""
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-2">Welcome, {user['name']}!</h2>
        <p class="text-muted small mb-4">Access your previous AI disease predictions and explore health information.</p>
        <a href="/prediction" class="btn btn-primary-custom rounded-pill">Run Symptom Prediction</a>
    </div>
    """
    return render_page(content)

@app.route('/predict', methods=['POST', 'GET'])
@app.route('/api/predict', methods=['POST', 'GET'])
def api_predict():
    if request.method == 'GET':
        return jsonify({"message": "Send POST request with JSON payload: {'disease': 'symptoms', 'symptoms': [...]}"})
    try:
        req_data = request.get_json(force=True, silent=True) or request.form.to_dict()
        disease = req_data.get('disease', 'symptoms')
        symptoms = req_data.get('symptoms', [])
        data_dict = req_data.get('data', {})
        
        if disease == 'symptoms' or symptoms:
            if not symptoms and isinstance(data_dict, list):
                symptoms = data_dict
            result_data = predict_symptoms(symptoms)
        else:
            result_data = predict_disease(disease, data_dict)
        return jsonify(result_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scanner')
@app.route('/image_scanner.php')
@app.route('/api/scanner')
def scanner_page():
    content = """
    <!-- Page Header & Hero -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card-custom p-4 p-md-5 mb-3" style="background: linear-gradient(135deg, #0b1120 0%, #151f32 50%, #0f766e 100%);">
                <span class="badge bg-white text-dark fw-bold px-3 py-2 rounded-pill mb-3">
                    <i class="bi bi-camera-fill text-info me-1"></i> Computer Vision Pipeline
                </span>
                <h1 class="display-6 fw-bold text-white mb-2">AI Infection & Injury Scanner</h1>
                <p class="lead mb-0 text-white-50">
                    Upload a clear image of a skin injury, wound, rash, swelling, or redness for an AI-assisted preliminary visual assessment.
                </p>
            </div>

            <!-- Mandatory Educational Disclaimer -->
            <div class="alert alert-warning border-0 p-3 mb-3 shadow-sm" style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b !important;">
                <i class="bi bi-exclamation-triangle-fill fs-5 me-2"></i>
                <strong>Important Medical Notice:</strong> This AI scanner provides an <em>educational preliminary visual assessment</em> and is not a medical diagnosis. For concerning, worsening, infected, or serious injuries, consult a qualified healthcare professional.
            </div>

            <!-- Privacy Assurance Banner -->
            <div class="alert alert-secondary py-2 px-3 small border d-flex align-items-center gap-2 mb-4">
                <i class="bi bi-shield-lock-fill text-success fs-5"></i>
                <div>
                    <strong>Privacy Assurance:</strong> Uploaded images are processed ephemerally in memory and permanently deleted immediately after visual metric extraction. Photos are <strong>never stored</strong> in our database. <em>Do not upload identifying personal documents or faces.</em>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Scanner Layout -->
    <div class="row g-4 mb-5">
        <div class="col-lg-6">
            <div class="card-custom h-100 p-4">
                <h4 class="fw-bold mb-1 d-flex align-items-center gap-2">
                    <i class="bi bi-cloud-arrow-up text-info"></i> Scan an Infection or Injury
                </h4>
                <p class="text-muted small mb-3">Upload a clear, well-lit image of the affected skin area for preliminary analysis.</p>

                <div id="scannerErrorAlert" class="alert alert-danger d-none mb-3 py-2 px-3 small">
                    <i class="bi bi-exclamation-circle-fill me-1"></i> <span id="scannerErrorMsg"></span>
                </div>

                <div id="dropZone" class="scanner-dropzone mb-3">
                    <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle d-inline-block mb-3">
                        <i class="bi bi-image fs-1"></i>
                    </div>
                    <h5 class="fw-bold mb-1">Drag & Drop Image Here</h5>
                    <p class="text-muted small mb-3">or choose from your device</p>
                    <div class="d-flex flex-wrap justify-content-center gap-2">
                        <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnBrowseFiles">
                            <i class="bi bi-folder2-open me-1"></i> Upload Image
                        </button>
                        <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnTakePhoto">
                            <i class="bi bi-camera me-1"></i> Take Photo
                        </button>
                    </div>
                    <div class="mt-3 text-muted small">
                        <span class="badge bg-secondary-subtle text-secondary me-1">JPG</span>
                        <span class="badge bg-secondary-subtle text-secondary me-1">PNG</span>
                        <span class="badge bg-secondary-subtle text-secondary">WEBP</span>
                        <span class="ms-2">Max 8 MB</span>
                    </div>
                    <input type="file" id="imageFileInput" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" class="d-none">
                    <input type="file" id="cameraFileInput" accept="image/*" capture="environment" class="d-none">
                </div>

                <div id="previewContainer" class="d-none mt-2">
                    <div class="scanner-preview-wrapper mb-3" id="previewFrame">
                        <img id="previewImage" class="scanner-preview-img" alt="Skin Preview">
                        <div class="scanner-laser-beam"></div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center p-2 px-3 rounded-3 mb-3 border" style="background: var(--bg-secondary);">
                        <span id="previewFilename" class="small fw-semibold text-truncate me-2">image.jpg</span>
                        <span id="previewFilesize" class="badge bg-secondary rounded-pill">0 KB</span>
                    </div>
                    <div class="d-flex gap-2" id="previewActions">
                        <button type="button" class="btn btn-outline-danger flex-fill py-2 rounded-3" id="btnRemoveImage">
                            <i class="bi bi-trash3 me-1"></i> Remove Image
                        </button>
                        <button type="button" class="btn btn-primary-custom flex-fill py-2" id="btnScanImage">
                            <i class="bi bi-cpu me-1"></i> Scan Image
                        </button>
                    </div>
                    <div id="scanningState" class="d-none text-center py-3">
                        <strong class="text-info fs-5 d-block mb-2">Analyzing image...</strong>
                        <p id="scanningStatusText" class="text-muted small mb-2">Evaluating visual characteristics...</p>
                        <div class="progress" style="height: 6px;">
                            <div id="scanProgressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-info" style="width: 50%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-6">
            <div class="card-custom h-100 p-4" id="resultCardContainer">
                <div id="idleState" class="text-center py-5 my-auto">
                    <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                    <h4 class="fw-bold mb-2">Preliminary Assessment Output</h4>
                    <p class="text-muted small mb-0">Select or capture a photo and click <strong>"Scan Image"</strong>. The computer vision analyzer evaluates erythema index, edge gradients, and textural dispersion.</p>
                </div>

                <div id="resultContent" class="d-none">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="text-muted small fw-bold text-uppercase"><i class="bi bi-clipboard2-pulse me-1"></i> Visual Assessment</span>
                        <span class="small text-muted">Just now</span>
                    </div>
                    <div class="mb-3">
                        <span id="resultCategoryBadge" class="badge-category badge-category-injury">
                            <span id="resultCategoryText">Evaluating...</span>
                        </span>
                    </div>
                    <div class="p-3 rounded-3 border mb-3" style="background: var(--bg-secondary);">
                        <h5 class="fw-bold mb-1" id="resultSummaryHeading">Visual indicators may be consistent with...</h5>
                        <p class="text-muted small mb-0" id="resultSummaryDesc">Assessment generated via spectrophotometric color analysis and surface edge gradient measurement.</p>
                    </div>
                    <div class="mb-3 p-3 rounded-3 border" style="background: var(--bg-secondary);">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="small fw-semibold">Visual Feature Correlation Score:</span>
                            <span id="resultScoreText" class="fw-bold text-info">0.0%</span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div id="resultScoreBar" class="progress-bar bg-info" style="width: 0%;"></div>
                        </div>
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valErythema">--</div>
                                <div class="metric-pill-lbl">Erythema</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valRoughness">--</div>
                                <div class="metric-pill-lbl">Roughness</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valChroma">--</div>
                                <div class="metric-pill-lbl">Variance</div>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <h6 class="fw-bold small text-uppercase text-muted mb-2">Visual Observations</h6>
                        <ul id="resultFindingsList" class="small text-muted ps-3 mb-0"></ul>
                    </div>
                    <div class="mb-3">
                        <h6 class="fw-bold small text-uppercase text-muted mb-2">General Educational Guidance</h6>
                        <ul id="resultRecsList" class="small text-muted ps-3 mb-0"></ul>
                    </div>
                    <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2" id="btnScanAnother">
                        <i class="bi bi-arrow-repeat me-1"></i> Scan Another Image
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Safety Warning Signs -->
    <div class="card-custom p-4 mb-5 border-danger-subtle">
        <div class="d-flex align-items-center gap-2 mb-3">
            <span class="badge bg-danger text-white px-3 py-2 rounded-pill">
                <i class="bi bi-hospital me-1"></i> Patient Safety Notice
            </span>
            <h4 class="fw-bold mb-0">When to Seek Immediate Medical Attention</h4>
        </div>
        <div class="row g-3">
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-droplet-fill me-1"></i> Severe Bleeding</div><div class="small text-muted">Blood that continues to flow after 10 minutes of direct pressure.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-graph-up-arrow me-1"></i> Rapidly Spreading Redness</div><div class="small text-muted">Red streaks radiating from the wound or expanding borders.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-thermometer-high me-1"></i> Fever & Systemic Chills</div><div class="small text-muted">Elevated body temperature (>100.4°F), rigors, or nausea.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-radioactive me-1"></i> Foul Pus or Drainage</div><div class="small text-muted">Thick, yellow/green discharge or wound that feels unusually hot.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-arrows-fullscreen me-1"></i> Rapidly Increasing Swelling</div><div class="small text-muted">Swelling that produces severe throbbing pain or numbs limb.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-bandaid-fill me-1"></i> Deep or Gaping Wounds</div><div class="small text-muted">Cuts exposing yellow fat or muscle requiring sutures.</div></div></div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var dropZone = document.getElementById('dropZone');
        var imageFileInput = document.getElementById('imageFileInput');
        var cameraFileInput = document.getElementById('cameraFileInput');
        var btnBrowseFiles = document.getElementById('btnBrowseFiles');
        var btnTakePhoto = document.getElementById('btnTakePhoto');
        var previewContainer = document.getElementById('previewContainer');
        var previewImage = document.getElementById('previewImage');
        var previewFilename = document.getElementById('previewFilename');
        var previewFilesize = document.getElementById('previewFilesize');
        var previewActions = document.getElementById('previewActions');
        var btnRemoveImage = document.getElementById('btnRemoveImage');
        var btnScanImage = document.getElementById('btnScanImage');
        var scanningState = document.getElementById('scanningState');
        var previewFrame = document.getElementById('previewFrame');
        var idleState = document.getElementById('idleState');
        var resultContent = document.getElementById('resultContent');
        var resultCategoryBadge = document.getElementById('resultCategoryBadge');
        var resultCategoryText = document.getElementById('resultCategoryText');
        var resultSummaryHeading = document.getElementById('resultSummaryHeading');
        var resultScoreText = document.getElementById('resultScoreText');
        var resultScoreBar = document.getElementById('resultScoreBar');
        var valErythema = document.getElementById('valErythema');
        var valRoughness = document.getElementById('valRoughness');
        var valChroma = document.getElementById('valChroma');
        var resultFindingsList = document.getElementById('resultFindingsList');
        var resultRecsList = document.getElementById('resultRecsList');
        var btnScanAnother = document.getElementById('btnScanAnother');
        var scannerErrorAlert = document.getElementById('scannerErrorAlert');
        var scannerErrorMsg = document.getElementById('scannerErrorMsg');

        var currentFile = null;

        function showError(msg) {
            scannerErrorMsg.textContent = msg;
            scannerErrorAlert.classList.remove('d-none');
        }
        function clearError() {
            scannerErrorAlert.classList.add('d-none');
        }

        btnBrowseFiles.onclick = function(e) { e.stopPropagation(); imageFileInput.click(); };
        btnTakePhoto.onclick = function(e) { e.stopPropagation(); cameraFileInput.click(); };
        dropZone.onclick = function() { imageFileInput.click(); };

        ['dragenter', 'dragover'].forEach(function(ev) {
            dropZone.addEventListener(ev, function(e) { e.preventDefault(); dropZone.classList.add('dragover'); });
        });
        ['dragleave', 'drop'].forEach(function(ev) {
            dropZone.addEventListener(ev, function(e) { e.preventDefault(); dropZone.classList.remove('dragover'); });
        });
        dropZone.addEventListener('drop', function(e) {
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });

        imageFileInput.onchange = function() { if (this.files.length) handleFile(this.files[0]); };
        cameraFileInput.onchange = function() { if (this.files.length) handleFile(this.files[0]); };

        function handleFile(file) {
            clearError();
            if (file.size > 8 * 1024 * 1024) { showError('Image is too large (max 8 MB).'); return; }
            currentFile = file;
            previewFilename.textContent = file.name;
            previewFilesize.textContent = (file.size / 1024).toFixed(1) + ' KB';
            var reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                dropZone.classList.add('d-none');
                previewContainer.classList.remove('d-none');
                previewActions.classList.remove('d-none');
                scanningState.classList.add('d-none');
            };
            reader.readAsDataURL(file);
        }

        btnRemoveImage.onclick = resetScanner;
        btnScanAnother.onclick = resetScanner;

        function resetScanner() {
            currentFile = null;
            imageFileInput.value = '';
            cameraFileInput.value = '';
            previewImage.src = '';
            previewContainer.classList.add('d-none');
            dropZone.classList.remove('d-none');
            previewFrame.classList.remove('scanning-active');
            resultContent.classList.add('d-none');
            idleState.classList.remove('d-none');
            clearError();
        }

        btnScanImage.onclick = function() {
            if (!currentFile) { showError('Please select an image first.'); return; }
            clearError();
            previewActions.classList.add('d-none');
            scanningState.classList.remove('d-none');
            previewFrame.classList.add('scanning-active');

            var formData = new FormData();
            formData.append('image', currentFile);

            fetch('/api/scan-image', { method: 'POST', body: formData })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                previewFrame.classList.remove('scanning-active');
                scanningState.classList.add('d-none');
                previewActions.classList.remove('d-none');
                renderResult(data);
            })
            .catch(function(err) {
                previewFrame.classList.remove('scanning-active');
                scanningState.classList.add('d-none');
                previewActions.classList.remove('d-none');
                showError('Error during scan: ' + err.message);
            });
        };

        function renderResult(res) {
            idleState.classList.add('d-none');
            resultContent.classList.remove('d-none');
            var cat = res.category || 'Unable to Assess';
            resultCategoryText.textContent = cat;
            resultCategoryBadge.className = 'badge-category';
            if (cat.includes('Infection')) resultCategoryBadge.classList.add('badge-category-infection');
            else if (cat.includes('Inflammation')) resultCategoryBadge.classList.add('badge-category-inflammation');
            else if (cat.includes('Minor Injury')) resultCategoryBadge.classList.add('badge-category-injury');
            else if (cat.includes('Rash')) resultCategoryBadge.classList.add('badge-category-rash');
            else if (cat.includes('Swelling')) resultCategoryBadge.classList.add('badge-category-swelling');
            else resultCategoryBadge.classList.add('badge-category-unable');

            resultSummaryHeading.textContent = 'Visual indicators may be consistent with ' + cat.toLowerCase();
            var score = res.confidence_score || 0;
            resultScoreText.textContent = score.toFixed(1) + '%';
            resultScoreBar.style.width = score + '%';

            var metrics = res.metrics || {};
            valErythema.textContent = (metrics.erythema_index !== undefined) ? metrics.erythema_index : '--';
            valRoughness.textContent = (metrics.surface_roughness !== undefined) ? metrics.surface_roughness : '--';
            valChroma.textContent = (metrics.chromatic_variance !== undefined) ? metrics.chromatic_variance : '--';

            resultFindingsList.innerHTML = '';
            (res.findings || []).forEach(function(f) {
                var li = document.createElement('li');
                li.className = 'mb-1';
                li.textContent = f;
                resultFindingsList.appendChild(li);
            });

            resultRecsList.innerHTML = '';
            (res.recommendations || []).forEach(function(r) {
                var li = document.createElement('li');
                li.className = 'mb-1';
                li.textContent = r;
                resultRecsList.appendChild(li);
            });
        }
    });
    </script>
    """
    return render_page(content)

@app.route('/api/scan-image', methods=['POST'])
def api_scan_image():
    temp_path = None
    try:
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "category": "Unable to Assess", "error": "No file selected"}), 400
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            file.save(temp_path)
            res = compute_vision_metrics(temp_path)
            return jsonify(res)

        req_data = request.get_json(silent=True) or {}
        if 'image_base64' in req_data:
            b64_val = req_data['image_base64']
            if ',' in b64_val:
                b64_val = b64_val.split(',', 1)[1]
            img_bytes = base64.b64decode(b64_val)
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            with open(temp_path, 'wb') as f:
                f.write(img_bytes)
            res = compute_vision_metrics(temp_path)
            return jsonify(res)

        return jsonify({"success": False, "category": "Unable to Assess", "error": "No image data provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "category": "Unable to Assess", "error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


handler = app
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
