import os
import sys
import json
import secrets
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease, predict_symptoms

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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Healthcare - Intelligent Disease Prediction & Health Assistance System</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-dark: #1e293b;
            --card-border: #334155;
            --accent-cyan: #06b6d4;
            --accent-teal: #0d9488;
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        .navbar-custom {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .card-custom {
            background: var(--card-dark);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .hero-banner {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
        }

        .btn-primary-custom {
            background: #0d9488;
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
            background: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #f59e0b;
            color: #fbbf24;
            padding: 14px 18px;
            border-radius: 10px;
            font-size: 0.875rem;
        }

        .form-control, .form-select {
            background-color: #0f172a;
            border: 1px solid #334155;
            color: #f8fafc;
            border-radius: 10px;
            padding: 10px 14px;
        }

        .form-control:focus, .form-select:focus {
            background-color: #0f172a;
            border-color: var(--accent-teal);
            color: #f8fafc;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.25);
        }

        footer {
            margin-top: auto;
            background: #090d16;
            color: #64748b;
            padding: 35px 0 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-xl navbar-dark navbar-custom sticky-top py-3">
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
                    <li class="nav-item"><a class="nav-link text-light" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/about">About</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/prediction">AI Prediction</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/assessment">Clinical Risk</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/simulator">Simulator</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/diseases">Diseases Library</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/symptoms">Symptoms Guide</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/prevention">Prevention</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/dataset-info">Dataset & AI</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/project-info">About Project</a></li>
                    <li class="nav-item"><a class="nav-link text-light" href="/contact">Contact</a></li>
                    {% if user %}
                        <li class="nav-item"><a class="nav-link text-light" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item ms-xl-2">
                            <a class="btn btn-outline-danger btn-sm rounded-pill px-3" href="/logout">Logout ({{ user.name }})</a>
                        </li>
                    {% else %}
                        <li class="nav-item ms-xl-2"><a class="btn btn-outline-info btn-sm rounded-pill px-3" href="/login">Login</a></li>
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
    if request.method == 'POST':
        symptoms = request.form.getlist('symptoms')
        if symptoms:
            result = predict_symptoms(symptoms)

    res_card = ""
    if result:
        res_card = f"""
        <div class="card-custom p-4 text-center border-info mt-4">
            <span class="badge bg-secondary mb-2">AI PREDICTION OUTPUT</span>
            <h2 class="display-5 fw-bold text-white my-2">{result.get('prediction')}</h2>
            <h1 class="display-3 fw-extrabold text-info">{result.get('probability')}%</h1>
            <p class="small text-muted">Model Confidence Score</p>
            <div class="disclaimer-banner small text-start my-3">{result.get('disclaimer')}</div>
        </div>
        """

    content = f"""
    <div class="row justify-content-center py-3">
        <div class="col-lg-8">
            <div class="card-custom p-4 p-md-5">
                <h3 class="fw-bold text-white mb-3">AI Symptom Checker</h3>
                <form method="POST" action="/prediction">
                    <div class="mb-3">
                        <label class="form-label text-white fw-bold">Select Symptoms:</label>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="high_blood_sugar" id="s1"><label class="form-check-label text-light" for="s1">High Blood Sugar / Thirst</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="frequent_urination" id="s2"><label class="form-check-label text-light" for="s2">Frequent Urination</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="high_blood_pressure" id="s3"><label class="form-check-label text-light" for="s3">High Blood Pressure</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="chest_pain" id="s4"><label class="form-check-label text-light" for="s4">Chest Pain / Tightness</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="shortness_of_breath" id="s5"><label class="form-check-label text-light" for="s5">Shortness of Breath</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="cough_with_sputum" id="s6"><label class="form-check-label text-light" for="s6">Persistent Cough with Sputum</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="fever" id="s7"><label class="form-check-label text-light" for="s7">Fever (>100.4°F)</label></div>
                        <div class="form-check"><input class="form-check-input" type="checkbox" name="symptoms" value="fatigue" id="s8"><label class="form-check-label text-light" for="s8">Chronic Lethargy & Fatigue</label></div>
                    </div>
                    <button type="submit" class="btn btn-primary-custom w-100 py-3">Submit Symptoms & Predict</button>
                </form>
            </div>
            {res_card}
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
        else:
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
        <div class="col-lg-9">
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
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>Heart Disease Risk Assessment (Cleveland Cardiac Model)</option>
                        </select>
                    </div>

                    <!-- Diabetes Fields -->
                    <div id="diabetes_fields" style="display: {'block' if disease_type == 'diabetes' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Biomarkers</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label text-light small">Glucose Level (mg/dL)</label>
                                <input type="number" step="0.1" name="Glucose" class="form-control" value="120" required>
                                <small class="text-muted">Normal fasting: 70-140 mg/dL</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="28.4" required>
                                <small class="text-muted">Normal: 18.5-24.9</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="BloodPressure" class="form-control" value="75" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-light small">Age (Years)</label>
                                <input type="number" name="Age" class="form-control" value="42" required>
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

                    <!-- Heart Fields -->
                    <div id="heart_fields" style="display: {'block' if disease_type == 'heart' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Cardiovascular Biomarkers</h5>
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

                    <div class="disclaimer-banner my-3 small">
                        <i class="bi bi-info-circle-fill me-1"></i> Data will be evaluated using our trained machine learning pipeline. Results are informational and educational only.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                        <i class="bi bi-cpu-fill me-2"></i> Compute AI Health Risk Assessment
                    </button>
                </form>

                <script>
                function toggleFields(val) {{
                    document.getElementById('diabetes_fields').style.display = (val === 'diabetes') ? 'block' : 'none';
                    document.getElementById('heart_fields').style.display = (val === 'heart') ? 'block' : 'none';
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
    
    if disease_type == 'diabetes':
        glucose = float(request.form.get('Glucose', 145))
        bmi = float(request.form.get('BMI', 31.0))
        bp = float(request.form.get('BloodPressure', 82))
        age = float(request.form.get('Age', 45))
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
    else:
        chol = float(request.form.get('chol', 250))
        trestbps = float(request.form.get('trestbps', 140))
        thalach = float(request.form.get('thalach', 130))
        age = float(request.form.get('age', 58))
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

    sim_result = predict_disease(disease_type, input_data)
    risk_color = "success" if sim_result['risk_level'] == "LOW" else ("warning" if sim_result['risk_level'] == "MODERATE" else "danger")
    
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
                        <label class="form-label text-white fw-bold">Select Target Model:</label>
                        <select name="disease_type" class="form-select" onchange="this.form.submit()">
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>Diabetes Risk Simulator</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>Heart Disease Risk Simulator</option>
                        </select>
                    </div>

                    <div class="row g-4 my-2">
                        <div class="col-md-6">
                            <label class="form-label text-white small fw-bold">{'Glucose Level (mg/dL)' if disease_type == 'diabetes' else 'Serum Cholesterol (mg/dL)'}: <span class="text-info fw-bold">{glucose if disease_type == 'diabetes' else chol}</span></label>
                            <input type="range" class="form-range" name="{'Glucose' if disease_type == 'diabetes' else 'chol'}" min="{'70' if disease_type == 'diabetes' else '120'}" max="{'250' if disease_type == 'diabetes' else '400'}" value="{glucose if disease_type == 'diabetes' else chol}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label text-white small fw-bold">{'Body Mass Index (BMI)' if disease_type == 'diabetes' else 'Resting Blood Pressure (mm Hg)'}: <span class="text-info fw-bold">{bmi if disease_type == 'diabetes' else trestbps}</span></label>
                            <input type="range" class="form-range" name="{'BMI' if disease_type == 'diabetes' else 'trestbps'}" min="{'15' if disease_type == 'diabetes' else '90'}" max="{'50' if disease_type == 'diabetes' else '200'}" step="{'0.5' if disease_type == 'diabetes' else '1'}" value="{bmi if disease_type == 'diabetes' else trestbps}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label text-white small fw-bold">{'Blood Pressure (mm Hg)' if disease_type == 'diabetes' else 'Max Heart Rate (bpm)'}: <span class="text-info fw-bold">{bp if disease_type == 'diabetes' else thalach}</span></label>
                            <input type="range" class="form-range" name="{'BloodPressure' if disease_type == 'diabetes' else 'thalach'}" min="{'50' if disease_type == 'diabetes' else '80'}" max="{'130' if disease_type == 'diabetes' else '210'}" value="{bp if disease_type == 'diabetes' else thalach}">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label text-white small fw-bold">Age: <span class="text-info fw-bold">{age}</span></label>
                            <input type="range" class="form-range" name="age" min="20" max="85" value="{age}">
                        </div>
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
    content = """
    <div class="card-custom p-5 text-center my-4">
        <h2 class="fw-bold text-white mb-3">Symptoms Guide & Body System Mapping</h2>
        <p class="text-muted small">Explore indicators organized across Endocrine, Respiratory, Cardiovascular, and Neurological systems.</p>
        <a href="/prediction" class="btn btn-primary-custom rounded-pill mt-3">Launch AI Symptom Checker</a>
    </div>
    """
    return render_page(content)

@app.route('/prevention')
@app.route('/prevention.php')
@app.route('/api/prevention')
def prevention():
    content = """
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-3">Health Awareness & Disease Prevention</h2>
        <p class="text-muted small mb-4">Evidence-based lifestyle strategies, physical activity standards, and screening timelines.</p>
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

handler = app
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
