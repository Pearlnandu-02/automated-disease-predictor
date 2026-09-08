import os
import sys
import json
import secrets
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Prevent caching on Vercel
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

DEMO_USERS = {
    "student@college.edu": {
        "name": "Academic Student",
        "email": "student@college.edu"
    }
}

def render_page(content_html, **kwargs):
    user = session.get('user')
    base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthRisk AI - Healthcare Risk Assessment System</title>
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

        /* Clean Glassmorphic Navbar */
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

        /* Risk Badges */
        .badge-risk-LOW {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 20px;
        }

        .badge-risk-MODERATE {
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 20px;
        }

        .badge-risk-HIGH {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 20px;
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

        /* Enhanced Logout Button Styling */
        .btn-logout-custom {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.35);
            font-weight: 600;
            font-size: 0.85rem;
            padding: 6px 16px;
            border-radius: 20px;
            transition: all 0.25s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
        }

        .btn-logout-custom:hover {
            background: #ef4444;
            color: #ffffff;
            border-color: #ef4444;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
            transform: translateY(-1px);
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
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand fw-bold d-flex align-items-center text-white" href="/">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4">HealthRisk<span class="text-info">AI</span></span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-2">
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/assessment">Risk Assessment</a></li>
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/simulator">What-If Simulator</a></li>
                    {% if user %}
                        <li class="nav-item"><a class="nav-link text-light fw-medium" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item ms-lg-2">
                            <a class="btn-logout-custom" href="/logout">
                                <i class="bi bi-box-arrow-right me-1 fs-6"></i> Logout ({{ user.name }})
                            </a>
                        </li>
                    {% else %}
                        <li class="nav-item"><a class="btn btn-outline-info btn-sm rounded-pill px-4 ms-lg-2" href="/login">Login</a></li>
                        <li class="nav-item"><a class="btn btn-info text-white btn-sm rounded-pill px-4" href="/register">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="py-4">
        <div class="container">
            """ + content_html + """
        </div>
    </main>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="row gy-3 mb-3">
                <div class="col-lg-6">
                    <h5 class="text-white fw-bold mb-2 d-flex align-items-center">
                        <i class="bi bi-heart-pulse-fill text-info me-2"></i> HealthRisk<span class="text-info">AI</span>
                    </h5>
                    <p class="small text-muted mb-2">
                        An Academic Machine Learning project for personalized risk assessment of Diabetes and Heart Disease using Scikit-Learn classifiers.
                    </p>
                    <div class="disclaimer-banner small text-start">
                        <i class="bi bi-info-circle me-1"></i>
                        <strong>Academic Disclaimer:</strong> Predictions are for educational risk-assessment purposes only and are not a substitute for professional medical advice.
                    </div>
                </div>
                <div class="col-lg-3 col-6 ms-auto">
                    <h6 class="text-white fw-bold mb-2">Navigation</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-1"><a href="/assessment" class="text-muted text-decoration-none">Risk Assessment</a></li>
                        <li class="mb-1"><a href="/simulator" class="text-muted text-decoration-none">What-If Simulator</a></li>
                        <li class="mb-1"><a href="/dashboard" class="text-muted text-decoration-none">Dashboard</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6">
                    <h6 class="text-white fw-bold mb-2">ML Stack</h6>
                    <ul class="list-unstyled small text-muted">
                        <li class="mb-1">Logistic Regression</li>
                        <li class="mb-1">Random Forest Classifier</li>
                        <li class="mb-1">Scikit-Learn & Joblib</li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary opacity-25">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center small text-muted">
                <p class="mb-0">&copy; 2026 HealthRisk AI - Academic Project.</p>
                <p class="mb-0">Built with Python, Scikit-Learn & Bootstrap 5</p>
            </div>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    return render_template_string(base_template, user=user, **kwargs)

# ROUTES

@app.route('/')
def home():
    content = """
    <div class="hero-banner p-4 p-md-5 my-3 shadow-lg">
        <div class="row align-items-center">
            <div class="col-lg-7">
                <span class="badge bg-info text-dark fw-bold px-3 py-2 rounded-pill mb-3">
                    Healthcare Risk Assessment
                </span>
                <h1 class="display-4 fw-bold mb-3 text-white">AI-Based Health Risk System</h1>
                <p class="lead text-light opacity-90 mb-4">
                    Assess risk levels for <strong>Diabetes</strong> and <strong>Heart Disease</strong> using trained Machine Learning models with Explainable AI feature breakdowns.
                </p>
                <div class="d-flex flex-wrap gap-3">
                    <a href="/assessment" class="btn btn-primary-custom btn-lg shadow">
                        <i class="bi bi-play-circle-fill me-2"></i> Start Risk Assessment
                    </a>
                    <a href="/simulator" class="btn btn-outline-light btn-lg rounded-pill px-4">
                        <i class="bi bi-sliders me-2"></i> What-If Simulator
                    </a>
                </div>
            </div>
            <div class="col-lg-5 mt-4 mt-lg-0">
                <div class="card-custom p-4 text-white shadow-lg">
                    <h5 class="fw-bold mb-3 text-info">Supported Condition Models</h5>
                    <div class="p-3 mb-3 bg-dark rounded-3 border-start border-info border-4">
                        <h6 class="fw-bold mb-1 text-white">Diabetes Risk Assessment</h6>
                        <small class="text-muted">Pima Clinical Dataset • Trained Classifier</small>
                    </div>
                    <div class="p-3 bg-dark rounded-3 border-start border-primary border-4">
                        <h6 class="fw-bold mb-1 text-white">Heart Disease Risk Assessment</h6>
                        <small class="text-muted">UCI Cardiac Dataset • Trained Classifier</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 py-3">
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3 text-info bg-dark">
                    <i class="bi bi-cpu-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">Machine Learning Models</h5>
                <p class="text-muted small mb-0">Trained Scikit-Learn pipelines evaluated on public datasets.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3 text-primary bg-dark">
                    <i class="bi bi-bar-chart-line-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">Explainable AI</h5>
                <p class="text-muted small mb-0">Displays feature contribution weights for model predictions.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3 text-success bg-dark">
                    <i class="bi bi-sliders fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">What-If Simulator</h5>
                <p class="text-muted small mb-0">Interactive parameter sliders to test prospective metric changes.</p>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', 'student@college.edu')
        session['user'] = {"name": email.split('@')[0].capitalize(), "email": email}
        return redirect('/dashboard')
            
    content = """
    <div class="row justify-content-center py-5">
        <div class="col-md-5">
            <div class="card-custom p-4 p-md-5">
                <div class="text-center mb-4">
                    <i class="bi bi-shield-lock-fill fs-1 text-info"></i>
                    <h3 class="fw-bold text-white">Member Login</h3>
                    <p class="text-muted small">Access Healthcare AI Platform</p>
                </div>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold text-white">Email Address</label>
                        <input type="email" name="email" class="form-control" value="student@college.edu" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold text-white">Password</label>
                        <input type="password" name="password" class="form-control" value="password123" required>
                    </div>
                    <button type="submit" class="btn btn-primary-custom w-100 py-2 fw-bold">Log In</button>
                </form>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', 'User')
        email = request.form.get('email', 'user@example.com')
        session['user'] = {"name": name, "email": email}
        return redirect('/dashboard')
        
    content = """
    <div class="row justify-content-center py-5">
        <div class="col-md-5">
            <div class="card-custom p-4 p-md-5">
                <div class="text-center mb-4">
                    <i class="bi bi-person-plus-fill fs-1 text-info"></i>
                    <h3 class="fw-bold text-white">Create Account</h3>
                </div>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold text-white">Full Name</label>
                        <input type="text" name="name" class="form-control" placeholder="John Doe" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold text-white">Email Address</label>
                        <input type="email" name="email" class="form-control" placeholder="john@example.com" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold text-white">Password</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary-custom w-100 py-2 fw-bold">Register Account</button>
                </form>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    user = session.get('user', {"name": "Guest Academic User", "email": "guest@college.edu"})
    history = session.get('history', [])
    
    history_html = ""
    for idx, h in enumerate(reversed(history)):
        history_html += f"""
        <tr>
            <td class="fw-bold text-white">#HRA-{len(history)-idx}</td>
            <td><strong class="text-info">{h.get('disease')}</strong></td>
            <td><span class="badge-risk-{h.get('risk_level')}">{h.get('risk_level')}</span></td>
            <td class="fw-bold fs-6 text-white">{h.get('probability')}%</td>
            <td><a href="/result?idx={len(history)-1-idx}" class="btn btn-sm btn-outline-info rounded-pill"><i class="bi bi-eye me-1"></i>View Result</a></td>
        </tr>
        """
        
    if not history_html:
        history_html = '<tr><td colspan="5" class="text-center text-muted py-4">No assessment history recorded yet. <a href="/assessment" class="btn btn-sm btn-primary-custom ms-2">Start Assessment</a></td></tr>'
        
    content = f"""
    <div class="row gy-4 py-3">
        <div class="col-12">
            <div class="card-custom p-4 bg-dark text-white">
                <span class="badge bg-info text-dark px-3 py-1 mb-2">Member Dashboard</span>
                <h2 class="fw-bold mb-1">Welcome, {user['name']}!</h2>
                <p class="text-muted mb-3">AI-Based Healthcare Risk Assessment & Preventive Care System</p>
                <a href="/assessment" class="btn btn-primary-custom rounded-pill me-2"><i class="bi bi-plus-circle me-1"></i> New Assessment</a>
                <a href="/simulator" class="btn btn-outline-light rounded-pill px-4"><i class="bi bi-sliders me-1"></i> What-If Simulator</a>
            </div>
        </div>
        <div class="col-12">
            <div class="card-custom p-4">
                <h5 class="fw-bold mb-3 text-white"><i class="bi bi-clock-history me-2 text-info"></i>Assessment History Log</h5>
                <div class="table-responsive">
                    <table class="table table-dark table-hover align-middle mb-0">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Assessed Condition</th>
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
    """
    return render_page(content)

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
        
    content = """
    <div class="row justify-content-center py-4">
        <div class="col-lg-9">
            <div class="card-custom p-4 p-md-5">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="p-3 rounded-circle me-3 text-info bg-dark">
                        <i class="bi bi-clipboard-pulse fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0 text-white">Health Risk Assessment Form</h3>
                        <p class="text-muted small mb-0">Enter clinical parameters for AI risk evaluation</p>
                    </div>
                </div>

                <form method="POST" id="assessForm">
                    <div class="mb-4 bg-dark p-3 rounded-3 border border-secondary border-opacity-25">
                        <label class="form-label fw-bold text-white fs-5 mb-2"><i class="bi bi-virus me-2 text-info"></i>Select Target Condition</label>
                        <select name="disease_type" id="disease_type" class="form-select form-select-lg" onchange="toggleForm()">
                            <option value="diabetes">Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart">Heart Disease Risk Assessment (UCI Cardiac Dataset)</option>
                        </select>
                    </div>

                    <!-- DIABETES INPUTS -->
                    <div id="diabetes_inputs">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Clinical Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Glucose Level (mg/dL)</label>
                                <input type="number" step="0.1" name="Glucose" class="form-control" value="135" required>
                                <small class="text-muted">Fasting normal: 70–99 mg/dL</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="29.5" required>
                                <small class="text-muted">Healthy range: 18.5–24.9</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="BloodPressure" class="form-control" value="78" required>
                                <small class="text-muted">Diastolic pressure</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Age (Years)</label>
                                <input type="number" name="Age" class="form-control" value="45" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Pregnancies</label>
                                <input type="number" name="Pregnancies" class="form-control" value="1" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Insulin (mu U/ml)</label>
                                <input type="number" step="0.1" name="Insulin" class="form-control" value="85" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Skin Thickness (mm)</label>
                                <input type="number" step="0.1" name="SkinThickness" class="form-control" value="22" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold text-white">Diabetes Pedigree Function</label>
                                <input type="number" step="0.01" name="DiabetesPedigreeFunction" class="form-control" value="0.47" required>
                                <small class="text-muted">Genetic likelihood score</small>
                            </div>
                        </div>
                    </div>

                    <!-- HEART INPUTS -->
                    <div id="heart_inputs" style="display:none;">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Clinical Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Age</label><input type="number" name="age" class="form-control" value="55"></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Sex</label><select name="sex" class="form-select"><option value="1">Male</option><option value="0">Female</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Chest Pain (CP 0-3)</label><select name="cp" class="form-select"><option value="0">Typical Angina (0)</option><option value="1">Atypical Angina (1)</option><option value="2">Non-anginal (2)</option><option value="3">Asymptomatic (3)</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Resting Blood Pressure (mm Hg)</label><input type="number" step="0.1" name="trestbps" class="form-control" value="135"></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Serum Cholesterol (mg/dL)</label><input type="number" step="0.1" name="chol" class="form-control" value="245"></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Max Heart Rate (Thalach)</label><input type="number" step="0.1" name="thalach" class="form-control" value="145"></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">Exercise Angina</label><select name="exang" class="form-select"><option value="0">No (0)</option><option value="1">Yes (1)</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold text-white">ST Depression (Oldpeak)</label><input type="number" step="0.1" name="oldpeak" class="form-control" value="1.2"></div>
                        </div>
                    </div>

                    <div class="disclaimer-banner my-4">
                        <i class="bi bi-info-circle me-1"></i> By clicking calculate, parameters are evaluated against trained Machine Learning models.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100"><i class="bi bi-cpu-fill me-2"></i> Run Risk Assessment</button>
                </form>
            </div>
        </div>
    </div>
    <script>
    function toggleForm() {
        var d = document.getElementById('disease_type').value;
        if(d === 'diabetes') {
            document.getElementById('diabetes_inputs').style.display = 'block';
            document.getElementById('heart_inputs').style.display = 'none';
        } else {
            document.getElementById('diabetes_inputs').style.display = 'none';
            document.getElementById('heart_inputs').style.display = 'block';
        }
    }
    </script>
    """
    return render_page(content)

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
    
    rec_html = "".join([f'<div class="col-md-6"><div class="p-3 bg-dark bg-opacity-50 rounded border border-secondary border-opacity-25 h-100 small text-white"><i class="bi bi-check-circle-fill text-success me-2 fs-5"></i>{rec}</div></div>' for rec in res.get('recommendations', [])])
    
    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <!-- Result Summary Header Card -->
            <div class="card-custom p-4 p-md-5 mb-4 text-center">
                <span class="badge bg-secondary mb-2">{res.get('disease')}</span>
                <h2 class="fw-bold text-white">Predicted Risk Level: <span class="badge-risk-{res.get('risk_level')}">{res.get('risk_level')}</span></h2>
                <h1 class="display-3 fw-bold text-white mt-2">{res.get('probability')}% Probability</h1>
                <p class="text-muted small">Classifier Used: <strong>{res.get('model_used')}</strong></p>
            </div>

            <!-- Explainable AI (XAI) Feature Importance Chart -->
            <div class="card-custom p-4 p-md-5 mb-4">
                <h4 class="fw-bold mb-2 text-white"><i class="bi bi-bar-chart-line-fill text-info me-2"></i>Explainable AI (XAI): Parameter Influence Breakdown</h4>
                <p class="text-muted small mb-4">Relative weight of parameters that influenced the statistical risk score:</p>
                <div style="height: 280px;"><canvas id="fiChart"></canvas></div>
            </div>

            <!-- Preventive Health Recommendations -->
            <div class="card-custom p-4 p-md-5 mb-4">
                <h4 class="fw-bold mb-3 text-white"><i class="bi bi-shield-check text-success me-2"></i>Personalized Educational Guidance</h4>
                <div class="row g-3">{rec_html}</div>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
                <a href="/assessment" class="btn btn-outline-secondary rounded-pill px-4 text-white">New Assessment</a>
                <div class="d-flex gap-2">
                    <a href="/simulator" class="btn btn-primary-custom rounded-pill px-4">Launch What-If Simulator</a>
                    <a href="/report" target="_blank" class="btn btn-outline-light rounded-pill px-4"><i class="bi bi-printer me-1"></i> Print PDF Report</a>
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
                    label: 'Importance Weight (%)',
                    data: {json.dumps(fi_vals)},
                    backgroundColor: 'rgba(13, 148, 136, 0.75)',
                    borderColor: '#0d9488',
                    borderWidth: 1.5,
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#9ca3af' }} }},
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#9ca3af' }} }}
                }}
            }}
        }});
    }});
    </script>
    """
    return render_page(content)

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
        
    sim_card = ""
    if sim_result:
        sim_card = f"""
        <div class="card-custom p-4 text-center mt-4">
            <h5 class="text-muted text-uppercase fw-bold mb-2">Simulated Risk Prediction</h5>
            <h3 class="fw-bold mb-2">
                <span class="badge-risk-{sim_result.get('risk_level')}">{sim_result.get('risk_level')} RISK</span>
            </h3>
            <h1 class="display-3 fw-extrabold text-white">{sim_result.get('probability')}%</h1>
            <p class="text-muted small">Updated Statistical Probability</p>
        </div>
        """
        
    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-9">
            <div class="card-custom p-4 p-md-5 mb-4">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="p-3 rounded-circle me-3 text-info bg-dark">
                        <i class="bi bi-sliders fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0 text-white">What-If Health Risk Simulator</h3>
                        <p class="text-muted small mb-0">Adjust parameter sliders to observe prospective probability recalculations</p>
                    </div>
                </div>

                <form method="POST">
                    <input type="hidden" name="disease_type" value="diabetes">
                    <div class="mb-4">
                        <label class="form-label fw-bold d-flex justify-content-between text-white">
                            <span>Simulated Glucose Level (mg/dL)</span>
                            <output class="fw-bold fs-5 text-info" id="out_glucose">130</output>
                        </label>
                        <input type="range" class="form-range" min="70" max="220" value="130" name="Glucose" oninput="document.getElementById('out_glucose').value = this.value">
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold d-flex justify-content-between text-white">
                            <span>Simulated Body Mass Index (BMI)</span>
                            <output class="fw-bold fs-5 text-info" id="out_bmi">27.0</output>
                        </label>
                        <input type="range" class="form-range" min="15" max="45" step="0.5" value="27" name="BMI" oninput="document.getElementById('out_bmi').value = this.value">
                    </div>
                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 mt-3"><i class="bi bi-play-circle-fill me-2"></i> Run What-If Simulation</button>
                </form>
            </div>
            {sim_card}
        </div>
    </div>
    """
    return render_page(content)

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
                <div>
                    <h2 class="fw-bold">HealthRiskAI Report</h2>
                    <span class="text-muted">Academic ML Assessment System</span>
                </div>
                <div class="text-end"><strong>Report ID: #HRA-882</strong><br><small>Academic ML Assessment</small></div>
            </div>
            <div class="bg-light p-3 rounded mb-4">
                <div><strong>Patient Name:</strong> {user['name']}</div>
                <div><strong>Condition Assessed:</strong> {last_res.get('disease', 'Diabetes Risk')}</div>
            </div>
            <div class="text-center p-4 border rounded mb-4">
                <h3>Predicted Risk Level: {last_res.get('risk_level', 'MODERATE')}</h3>
                <h2 class="display-4 fw-bold">{last_res.get('probability', 68.5)}% Probability</h2>
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

app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
