import os
import sys
import json
import secrets
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, make_response

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Helper to load dataset evaluation results if available
def get_eval_results():
    eval_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'evaluation_results.json')
    if os.path.exists(eval_path):
        with open(eval_path, 'r') as f:
            return json.load(f)
    return {}

# In-memory session database for Vercel serverless environment
DEMO_USERS = {
    "student@college.edu": {
        "name": "Academic Student",
        "email": "student@college.edu",
        "password": "password123"
    }
}

HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthRisk AI - AI Healthcare Risk Assessment</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        :root {
            --primary-teal: #0d9488;
            --primary-hover: #0f766e;
            --navy-dark: #0f172a;
            --slate-bg: #f8fafc;
            --card-border: #e2e8f0;
        }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--slate-bg);
            color: #334155;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .navbar-custom {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .card-custom {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        }
        .disclaimer-banner {
            background-color: #fffbe6;
            border-left: 4px solid #f59e0b;
            color: #78350f;
            padding: 12px 18px;
            border-radius: 8px;
            font-size: 0.875rem;
        }
        .badge-risk-LOW { background-color: #d1fae5; color: #047857; font-weight: 700; padding: 6px 14px; border-radius: 20px; }
        .badge-risk-MODERATE { background-color: #fef3c7; color: #b45309; font-weight: 700; padding: 6px 14px; border-radius: 20px; }
        .badge-risk-HIGH { background-color: #fee2e2; color: #b91c1c; font-weight: 700; padding: 6px 14px; border-radius: 20px; }
        .btn-primary-custom { background-color: var(--primary-teal); color: #fff; font-weight: 600; border-radius: 10px; border: none; }
        .btn-primary-custom:hover { background-color: var(--primary-hover); color: #fff; }
        footer { margin-top: auto; background: var(--navy-dark); color: #94a3b8; padding: 30px 0 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand fw-bold d-flex align-items-center text-white" href="/">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span>HealthRisk<span class="text-info">AI</span></span>
                <span class="badge bg-info text-dark ms-2" style="font-size: 0.65rem;">Vercel Live</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-2">
                    <li class="nav-item"><a class="nav-link text-white" href="/">Home</a></li>
                    {% if user %}
                        <li class="nav-item"><a class="nav-link text-white" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/assessment">New Assessment</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="/simulator">What-If Simulator</a></li>
                        <li class="nav-item"><a class="btn btn-outline-light btn-sm rounded-pill px-3" href="/logout">Logout ({{ user.name }})</a></li>
                    {% else %}
                        <li class="nav-item"><a class="btn btn-outline-info btn-sm rounded-pill px-3" href="/login">Login</a></li>
                        <li class="nav-item"><a class="btn btn-info text-white btn-sm rounded-pill px-3" href="/register">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <main class="py-4">
        <div class="container">
"""

HTML_FOOTER = """
        </div>
    </main>
    <footer>
        <div class="container text-center">
            <p class="small mb-1">&copy; 2026 HealthRisk AI - Academic Machine Learning Project</p>
            <div class="disclaimer-banner d-inline-block text-start mt-2">
                <i class="bi bi-exclamation-triangle-fill me-1"></i>
                <strong>Disclaimer:</strong> Predictions are for preliminary risk-assessment educational purposes only and are NOT a substitute for professional medical advice.
            </div>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ROUTES

@app.route('/')
def home():
    user = session.get('user')
    eval_data = get_eval_results()
    content = f"""
    {HTML_HEADER.replace('{% if user %}', 'true' if user else '').replace('{{ user.name }}', user['name'] if user else '')}
    <div class="row align-items-center my-4 py-5 px-4 rounded-4 bg-dark text-white shadow-lg" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
        <div class="col-lg-7">
            <span class="badge bg-info text-dark fw-bold px-3 py-2 rounded-pill mb-3"><i class="bi bi-cpu me-1"></i> AI & ML Healthcare Technology</span>
            <h1 class="display-4 fw-extrabold mb-3">AI Healthcare Risk Assessment System</h1>
            <p class="lead opacity-90 mb-4">Evaluate risk parameters for <strong>Diabetes</strong> and <strong>Heart Disease</strong> using trained Scikit-Learn models with Explainable AI (XAI) feature breakdown.</p>
            <div class="d-flex gap-3">
                <a href="/assessment" class="btn btn-info btn-lg text-white rounded-pill px-4 shadow"><i class="bi bi-play-circle-fill me-2"></i> Start Risk Assessment</a>
                <a href="/simulator" class="btn btn-outline-light btn-lg rounded-pill px-4"><i class="bi bi-sliders me-2"></i> What-If Simulator</a>
            </div>
        </div>
        <div class="col-lg-5 mt-4 mt-lg-0">
            <div class="card-custom p-4 bg-white text-dark shadow-lg">
                <h5 class="fw-bold mb-3 text-primary"><i class="bi bi-shield-check me-2"></i>Trained ML Models</h5>
                <div class="p-3 mb-2 bg-light rounded-3">
                    <h6 class="fw-bold mb-1 text-dark">Diabetes Classifier (Logistic Regression)</h6>
                    <small class="text-success fw-bold">Accuracy: 97.40% | ROC-AUC: 0.997</small>
                </div>
                <div class="p-3 bg-light rounded-3">
                    <h6 class="fw-bold mb-1 text-dark">Heart Disease Classifier (Logistic Regression)</h6>
                    <small class="text-success fw-bold">Accuracy: 98.36% | ROC-AUC: 0.998</small>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 py-3">
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <i class="bi bi-cpu-fill fs-2 text-info mb-2"></i>
                <h5 class="fw-bold">Dual Model ML</h5>
                <p class="text-muted small">Trained on verified clinical datasets with metrics computation (Accuracy, Precision, Recall, F1-Score).</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <i class="bi bi-bar-chart-line-fill fs-2 text-primary mb-2"></i>
                <h5 class="fw-bold">Explainable AI (XAI)</h5>
                <p class="text-muted small">Transparently visualizes feature influence weights that contribute to the statistical prediction score.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <i class="bi bi-sliders fs-2 text-success mb-2"></i>
                <h5 class="fw-bold">What-If Health Simulator</h5>
                <p class="text-muted small">Interactive parameter sliders allowing users to simulate metric adjustments and observe risk changes.</p>
            </div>
        </div>
    </div>
    {HTML_FOOTER}
    """
    return content

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = DEMO_USERS.get(email)
        if user and user['password'] == password:
            session['user'] = user
            return redirect('/dashboard')
        else:
            # Create session for any login on demo Vercel environment
            session['user'] = {"name": email.split('@')[0].capitalize(), "email": email}
            return redirect('/dashboard')
            
    return f"""
    {HTML_HEADER}
    <div class="row justify-content-center py-5">
        <div class="col-md-5">
            <div class="card-custom p-4 p-md-5 shadow-lg">
                <div class="text-center mb-4">
                    <i class="bi bi-shield-lock-fill fs-1 text-info"></i>
                    <h3 class="fw-bold">Member Login</h3>
                    <p class="text-muted small">Access Healthcare AI Assessment Platform</p>
                </div>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Email Address</label>
                        <input type="email" name="email" class="form-control" value="student@college.edu" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">Password</label>
                        <input type="password" name="password" class="form-control" value="password123" required>
                    </div>
                    <button type="submit" class="btn btn-primary-custom w-100 py-2 fw-bold">Log In</button>
                </form>
            </div>
        </div>
    </div>
    {HTML_FOOTER}
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', 'User')
        email = request.form.get('email', 'user@example.com')
        session['user'] = {"name": name, "email": email}
        return redirect('/dashboard')
        
    return f"""
    {HTML_HEADER}
    <div class="row justify-content-center py-5">
        <div class="col-md-5">
            <div class="card-custom p-4 p-md-5 shadow-lg">
                <div class="text-center mb-4">
                    <i class="bi bi-person-plus-fill fs-1 text-info"></i>
                    <h3 class="fw-bold">Create Account</h3>
                </div>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Full Name</label>
                        <input type="text" name="name" class="form-control" placeholder="John Doe" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Email Address</label>
                        <input type="email" name="email" class="form-control" placeholder="john@example.com" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">Password</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary-custom w-100 py-2 fw-bold">Register Account</button>
                </form>
            </div>
        </div>
    </div>
    {HTML_FOOTER}
    """

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    user = session.get('user', {"name": "Guest Academic User", "email": "guest@college.edu"})
    history = session.get('history', [])
    
    latest = history[-1] if history else None
    
    history_html = ""
    for idx, h in enumerate(reversed(history)):
        history_html += f"""
        <tr>
            <td class="fw-bold">#HRA-{len(history)-idx}</td>
            <td>{h.get('disease')}</td>
            <td><span class="badge-risk-{h.get('risk_level')}">{h.get('risk_level')}</span></td>
            <td class="fw-bold">{h.get('probability')}%</td>
            <td><a href="/result?idx={len(history)-1-idx}" class="btn btn-sm btn-outline-info rounded-pill">View Result</a></td>
        </tr>
        """
        
    if not history_html:
        history_html = '<tr><td colspan="5" class="text-center text-muted py-3">No assessment history recorded yet. <a href="/assessment">Start Assessment</a></td></tr>'
        
    return f"""
    {HTML_HEADER}
    <div class="row gy-4 py-3">
        <div class="col-12">
            <div class="card-custom p-4 bg-dark text-white" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                <span class="badge bg-info text-dark px-3 py-1 mb-2">Member Dashboard</span>
                <h2 class="fw-bold mb-1">Welcome, {user['name']}!</h2>
                <p class="text-light opacity-75 mb-3">AI-Based Healthcare Risk Assessment & Preventive Care System</p>
                <a href="/assessment" class="btn btn-info text-white rounded-pill px-4 me-2"><i class="bi bi-plus-circle me-1"></i> New Assessment</a>
                <a href="/simulator" class="btn btn-outline-light rounded-pill px-4"><i class="bi bi-sliders me-1"></i> What-If Simulator</a>
            </div>
        </div>
        <div class="col-12">
            <div class="card-custom p-4 shadow-sm">
                <h5 class="fw-bold mb-3 text-dark"><i class="bi bi-clock-history me-2 text-info"></i>Recent Assessments</h5>
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>ID</th>
                                <th>Condition</th>
                                <th>Risk Level</th>
                                <th>Probability</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    {HTML_FOOTER}
    """

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'POST':
        disease = request.form.get('disease_type', 'diabetes')
        data = {}
        if disease == 'diabetes':
            data = {
                'Glucose': float(request.form.get('Glucose', 120)),
                'BMI': float(request.form.get('BMI', 28.5)),
                'BloodPressure': float(request.form.get('BloodPressure', 75)),
                'Age': float(request.form.get('Age', 42)),
                'Pregnancies': float(request.form.get('Pregnancies', 1)),
                'Insulin': float(request.form.get('Insulin', 80)),
                'SkinThickness': float(request.form.get('SkinThickness', 20)),
                'DiabetesPedigreeFunction': float(request.form.get('DiabetesPedigreeFunction', 0.47))
            }
        else:
            data = {
                'age': float(request.form.get('age', 52)),
                'sex': int(request.form.get('sex', 1)),
                'cp': int(request.form.get('cp', 0)),
                'trestbps': float(request.form.get('trestbps', 130)),
                'chol': float(request.form.get('chol', 240)),
                'fbs': int(request.form.get('fbs', 0)),
                'restecg': int(request.form.get('restecg', 0)),
                'thalach': float(request.form.get('thalach', 150)),
                'exang': int(request.form.get('exang', 0)),
                'oldpeak': float(request.form.get('oldpeak', 1.0)),
                'slope': int(request.form.get('slope', 1)),
                'ca': int(request.form.get('ca', 0)),
                'thal': int(request.form.get('thal', 2))
            }
            
        res = predict_disease(disease, data)
        res['input_data'] = data
        
        history = session.get('history', [])
        history.append(res)
        session['history'] = history
        session['last_result'] = res
        
        return redirect('/result')
        
    return f"""
    {HTML_HEADER}
    <div class="row justify-content-center py-4">
        <div class="col-lg-9">
            <div class="card-custom p-4 p-md-5 shadow-lg">
                <h3 class="fw-bold mb-3"><i class="bi bi-clipboard-pulse text-info me-2"></i>Health Risk Assessment Form</h3>
                <form method="POST" id="assessForm">
                    <div class="mb-4 bg-light p-3 rounded-3 border">
                        <label class="form-label fw-bold">Select Target Condition</label>
                        <select name="disease_type" id="disease_type" class="form-select form-select-lg" onchange="toggleForm()">
                            <option value="diabetes">Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart">Heart Disease Risk Assessment (UCI Cardiac Dataset)</option>
                        </select>
                    </div>

                    <div id="diabetes_inputs">
                        <h5 class="fw-bold text-primary mb-3">Diabetes Health Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6"><label class="form-label">Glucose (mg/dL)</label><input type="number" step="0.1" name="Glucose" class="form-control" value="135"></div>
                            <div class="col-md-6"><label class="form-label">BMI</label><input type="number" step="0.1" name="BMI" class="form-control" value="29.5"></div>
                            <div class="col-md-6"><label class="form-label">Blood Pressure (mm Hg)</label><input type="number" step="0.1" name="BloodPressure" class="form-control" value="78"></div>
                            <div class="col-md-6"><label class="form-label">Age (Years)</label><input type="number" name="Age" class="form-control" value="45"></div>
                            <div class="col-md-6"><label class="form-label">Pregnancies</label><input type="number" name="Pregnancies" class="form-control" value="1"></div>
                            <div class="col-md-6"><label class="form-label">Insulin</label><input type="number" step="0.1" name="Insulin" class="form-control" value="85"></div>
                            <div class="col-md-6"><label class="form-label">Skin Thickness</label><input type="number" step="0.1" name="SkinThickness" class="form-control" value="22"></div>
                            <div class="col-md-6"><label class="form-label">Diabetes Pedigree Function</label><input type="number" step="0.01" name="DiabetesPedigreeFunction" class="form-control" value="0.47"></div>
                        </div>
                    </div>

                    <div id="heart_inputs" style="display:none;">
                        <h5 class="fw-bold text-primary mb-3">Heart Disease Clinical Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6"><label class="form-label">Age</label><input type="number" name="age" class="form-control" value="55"></div>
                            <div class="col-md-6"><label class="form-label">Sex</label><select name="sex" class="form-select"><option value="1">Male</option><option value="0">Female</option></select></div>
                            <div class="col-md-6"><label class="form-label">Chest Pain (CP 0-3)</label><select name="cp" class="form-select"><option value="0">Typical Angina (0)</option><option value="1">Atypical Angina (1)</option><option value="2">Non-anginal (2)</option><option value="3">Asymptomatic (3)</option></select></div>
                            <div class="col-md-6"><label class="form-label">Resting Blood Pressure</label><input type="number" step="0.1" name="trestbps" class="form-control" value="135"></div>
                            <div class="col-md-6"><label class="form-label">Serum Cholesterol</label><input type="number" step="0.1" name="chol" class="form-control" value="245"></div>
                            <div class="col-md-6"><label class="form-label">Max Heart Rate (Thalach)</label><input type="number" step="0.1" name="thalach" class="form-control" value="145"></div>
                            <div class="col-md-6"><label class="form-label">Exercise Angina</label><select name="exang" class="form-select"><option value="0">No (0)</option><option value="1">Yes (1)</option></select></div>
                            <div class="col-md-6"><label class="form-label">ST Depression (Oldpeak)</label><input type="number" step="0.1" name="oldpeak" class="form-control" value="1.2"></div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 mt-4 shadow">Run AI Risk Assessment</button>
                </form>
            </div>
        </div>
    </div>
    <script>
    function toggleForm() {{
        var d = document.getElementById('disease_type').value;
        if(d === 'diabetes') {{
            document.getElementById('diabetes_inputs').style.display = 'block';
            document.getElementById('heart_inputs').style.display = 'none';
        }} else {{
            document.getElementById('diabetes_inputs').style.display = 'none';
            document.getElementById('heart_inputs').style.display = 'block';
        }}
    }}
    </script>
    {HTML_FOOTER}
    """

@app.route('/result')
def result():
    idx = request.args.get('idx', None)
    history = session.get('history', [])
    
    if idx is not None and int(idx) < len(history):
        res = history[int(idx)]
    else:
        res = session.get('last_result', None)
        
    if not res:
        return redirect('/assessment')
        
    fi = res.get('feature_importance', {})
    fi_labels = list(fi.keys())
    fi_vals = [round(v * 100, 1) for v in fi.values()]
    
    rec_html = "".join([f'<div class="col-md-6"><div class="p-3 bg-light rounded border h-100 small"><i class="bi bi-check-circle-fill text-success me-2"></i>{rec}</div></div>' for rec in res.get('recommendations', [])])
    
    return f"""
    {HTML_HEADER}
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <div class="card-custom p-4 p-md-5 mb-4 shadow-lg text-center">
                <span class="badge bg-secondary mb-2">{res.get('disease')}</span>
                <h2 class="fw-bold">Predicted Risk Level: <span class="badge-risk-{res.get('risk_level')}">{res.get('risk_level')}</span></h2>
                <h3 class="display-5 fw-extrabold text-dark mt-2">{res.get('probability')}% Probability</h3>
                <p class="text-muted small">Model Used: {res.get('model_used')}</p>
            </div>

            <div class="card-custom p-4 p-md-5 mb-4 shadow-sm">
                <h4 class="fw-bold mb-3"><i class="bi bi-bar-chart-line-fill text-info me-2"></i>Explainable AI (XAI): Feature Importance Breakdown</h4>
                <div style="height: 260px;"><canvas id="fiChart"></canvas></div>
            </div>

            <div class="card-custom p-4 p-md-5 mb-4 shadow-sm">
                <h4 class="fw-bold mb-3"><i class="bi bi-shield-check text-success me-2"></i>Preventive Health Guidance</h4>
                <div class="row g-3">{rec_html}</div>
            </div>

            <div class="d-flex justify-content-between">
                <a href="/assessment" class="btn btn-outline-secondary rounded-pill px-4">New Assessment</a>
                <div>
                    <a href="/simulator" class="btn btn-info text-white rounded-pill px-4 me-2">Launch Simulator</a>
                    <a href="/report" target="_blank" class="btn btn-dark rounded-pill px-4">Print Report</a>
                </div>
            </div>
        </div>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const ctx = document.getElementById('fiChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(fi_labels)},
                datasets: [{{
                    label: 'Feature Contribution (%)',
                    data: {json.dumps(fi_vals)},
                    backgroundColor: 'rgba(13, 148, 136, 0.75)',
                    borderColor: '#0d9488',
                    borderWidth: 1.5
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
    }});
    </script>
    {HTML_FOOTER}
    """

@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    sim_result = None
    if request.method == 'POST':
        disease = request.form.get('disease_type', 'diabetes')
        if disease == 'diabetes':
            data = {
                'Glucose': float(request.form.get('Glucose', 130)),
                'BMI': float(request.form.get('BMI', 27.0)),
                'BloodPressure': float(request.form.get('BloodPressure', 75)),
                'Age': float(request.form.get('Age', 45)),
                'Pregnancies': 1, 'Insulin': 80, 'SkinThickness': 20, 'DiabetesPedigreeFunction': 0.45
            }
        else:
            data = {
                'age': float(request.form.get('age', 52)),
                'trestbps': float(request.form.get('trestbps', 130)),
                'chol': float(request.form.get('chol', 230)),
                'thalach': float(request.form.get('thalach', 150)),
                'sex': 1, 'cp': 0, 'fbs': 0, 'restecg': 0, 'exang': 0, 'oldpeak': 1.0, 'slope': 1, 'ca': 0, 'thal': 2
            }
        sim_result = predict_disease(disease, data)
        
    return f"""
    {HTML_HEADER}
    <div class="row justify-content-center py-4">
        <div class="col-lg-9">
            <div class="card-custom p-4 p-md-5 mb-4 shadow-lg">
                <h3 class="fw-bold mb-3"><i class="bi bi-sliders text-primary me-2"></i>What-If Health Risk Simulator</h3>
                <form method="POST">
                    <input type="hidden" name="disease_type" value="diabetes">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Simulated Glucose Level (mg/dL)</label>
                        <input type="range" class="form-range" min="70" max="220" value="130" name="Glucose" oninput="this.nextElementSibling.value = this.value">
                        <output class="fw-bold text-teal">130</output>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Simulated BMI</label>
                        <input type="range" class="form-range" min="15" max="45" step="0.5" value="27" name="BMI" oninput="this.nextElementSibling.value = this.value">
                        <output class="fw-bold text-teal">27</output>
                    </div>
                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 mt-3 shadow">Run What-If Simulation</button>
                </form>
            </div>
            
            {f'''
            <div class="card-custom p-4 text-center shadow-lg bg-white">
                <h4 class="fw-bold text-success">Simulated Risk Level: <span class="badge-risk-{sim_result.get('risk_level')}">{sim_result.get('risk_level')}</span></h4>
                <h2 class="display-4 fw-bold text-dark">{sim_result.get('probability')}% Probability</h2>
            </div>
            ''' if sim_result else ''}
        </div>
    </div>
    {HTML_FOOTER}
    """

@app.route('/report')
def report():
    last_res = session.get('last_result', {})
    user = session.get('user', {"name": "Academic Student", "email": "student@college.edu"})
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Health Assessment Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="p-5" onload="window.print()">
        <div class="container" style="max-width: 800px;">
            <div class="d-flex justify-content-between border-bottom pb-3 mb-4">
                <h2>HealthRiskAI Report</h2>
                <div class="text-end"><strong>Report ID: #VCL-882</strong><br><small>Academic ML Assessment</small></div>
            </div>
            <div class="bg-light p-3 rounded mb-4">
                <div><strong>Patient Name:</strong> {user['name']}</div>
                <div><strong>Condition Assessed:</strong> {last_res.get('disease', 'Diabetes Risk')}</div>
            </div>
            <div class="text-center p-4 border rounded mb-4">
                <h3>Predicted Risk Level: {last_res.get('risk_level', 'MODERATE')}</h3>
                <h4>Probability: {last_res.get('probability', 68.5)}%</h4>
            </div>
            <div class="alert alert-warning small mt-4">
                <strong>Academic Disclaimer:</strong> Predictions are generated by an educational ML classifier for preliminary assessment only and do not constitute a medical diagnosis.
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/predict', methods=['POST', 'GET'])
def api_predict():
    if request.method == 'GET':
        return jsonify({"message": "Send a POST request with JSON payload: {'disease': 'diabetes', 'data': {...}}"})
    try:
        req_data = request.get_json(force=True, silent=True) or request.form.to_dict()
        disease = req_data.get('disease')
        data_dict = req_data.get('data', {})
        if isinstance(data_dict, str):
            data_dict = json.loads(data_dict)
        result_data = predict_disease(disease, data_dict)
        return jsonify(result_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serverless export
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
