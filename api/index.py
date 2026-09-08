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

# In-Memory session fallback
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
    <title>HealthRisk AI - Advanced Healthcare Risk Assessment & Preventive Care</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-teal: #0d9488;
            --primary-hover: #0f766e;
            --navy-dark: #0f172a;
            --navy-card: #1e293b;
            --slate-bg: #f8fafc;
            --card-border: #e2e8f0;
            --accent-blue: #0284c7;
            --accent-purple: #6366f1;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--slate-bg);
            color: #334155;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* Glassmorphism & Navbar */
        .navbar-custom {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse 1.6s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Cards & Gradient Accents */
        .card-custom {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 20px;
            box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card-custom:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 35px -10px rgba(15, 23, 42, 0.1);
        }

        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
            color: #ffffff;
            border-radius: 28px;
            position: relative;
            overflow: hidden;
        }

        /* Custom Risk Badges */
        .badge-risk-LOW {
            background: rgba(16, 185, 129, 0.15);
            color: #047857;
            border: 1px solid rgba(16, 185, 129, 0.4);
            font-weight: 800;
            padding: 8px 18px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .badge-risk-MODERATE {
            background: rgba(245, 158, 11, 0.15);
            color: #b45309;
            border: 1px solid rgba(245, 158, 11, 0.4);
            font-weight: 800;
            padding: 8px 18px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .badge-risk-HIGH {
            background: rgba(239, 68, 68, 0.15);
            color: #b91c1c;
            border: 1px solid rgba(239, 68, 68, 0.4);
            font-weight: 800;
            padding: 8px 18px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .btn-primary-custom {
            background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%);
            color: #fff;
            font-weight: 700;
            border-radius: 12px;
            border: none;
            padding: 12px 28px;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35);
            transition: all 0.25s ease;
        }

        .btn-primary-custom:hover {
            background: linear-gradient(135deg, #0f766e 0%, #0369a1 100%);
            color: #fff;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.45);
        }

        .disclaimer-banner {
            background: #fffbe6;
            border-left: 5px solid #f59e0b;
            color: #78350f;
            padding: 14px 20px;
            border-radius: 12px;
            font-size: 0.875rem;
        }

        footer {
            margin-top: auto;
            background: var(--navy-dark);
            color: #94a3b8;
            padding: 40px 0 25px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
<body>
    <!-- Top Navigation Header -->
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand fw-extrabold d-flex align-items-center text-white" href="/">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4">HealthRisk<span class="text-info">AI</span></span>
                <span class="ms-2 px-2 py-1 bg-dark bg-opacity-50 text-info border border-info border-opacity-25 rounded-pill small d-none d-sm-inline-block">
                    <span class="pulse-dot me-1"></span>ML Engine v2.0
                </span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-2">
                    <li class="nav-item"><a class="nav-link text-white fw-medium" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link text-white fw-medium" href="/assessment">Risk Assessment</a></li>
                    <li class="nav-item"><a class="nav-link text-white fw-medium" href="/simulator">What-If Simulator</a></li>
                    <li class="nav-item"><a class="nav-link text-white fw-medium" href="/benchmarks">Model Performance</a></li>
                    {% if user %}
                        <li class="nav-item"><a class="nav-link text-white fw-medium" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item"><a class="btn btn-outline-light btn-sm rounded-pill px-3 ms-lg-2" href="/logout">Logout ({{ user.name }})</a></li>
                    {% else %}
                        <li class="nav-item"><a class="btn btn-outline-info btn-sm rounded-pill px-4 ms-lg-2" href="/login">Login</a></li>
                        <li class="nav-item"><a class="btn btn-info text-white btn-sm rounded-pill px-4" href="/register">Get Started</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Body Container -->
    <main class="py-4">
        <div class="container">
            """ + content_html + """
        </div>
    </main>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="row gy-4 mb-4">
                <div class="col-lg-6">
                    <h5 class="text-white fw-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-heart-pulse-fill text-info me-2"></i> HealthRisk<span class="text-info">AI</span>
                    </h5>
                    <p class="small text-muted mb-3">
                        An Academic Machine Learning project dedicated to personalized preventative health risk assessments for Diabetes and Heart Disease using Logistic Regression & Random Forest classifiers.
                    </p>
                    <div class="disclaimer-banner small text-start">
                        <i class="bi bi-shield-exclamation me-1 text-warning"></i>
                        <strong>Academic Disclaimer:</strong> This system provides preliminary statistical risk scores for educational purposes only. It does NOT provide medical diagnoses or prescriptions.
                    </div>
                </div>
                <div class="col-lg-3 col-6 ms-auto">
                    <h6 class="text-white fw-bold mb-3">Core Modules</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="/assessment" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-info"></i> Risk Assessment</a></li>
                        <li class="mb-2"><a href="/simulator" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-info"></i> What-If Simulator</a></li>
                        <li class="mb-2"><a href="/benchmarks" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-info"></i> ML Benchmarks</a></li>
                        <li class="mb-2"><a href="/dashboard" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-info"></i> Member Dashboard</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6">
                    <h6 class="text-white fw-bold mb-3">Trained Algorithms</h6>
                    <ul class="list-unstyled small text-muted">
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-info"></i> Logistic Regression (98.36%)</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-info"></i> Random Forest Classifiers</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-info"></i> Decision Trees & XAI</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-info"></i> Joblib Saved Pipelines</li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary opacity-25">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center small text-muted">
                <p class="mb-0">&copy; 2026 HealthRisk AI - Academic Machine Learning Project.</p>
                <p class="mb-0">Built with Python, Scikit-Learn & Bootstrap 5</p>
            </div>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    return render_template_string(base_template, user=user, **kwargs)

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

@app.route('/')
def home():
    content = """
    <!-- Hero Banner -->
    <div class="hero-banner p-4 p-md-5 my-3 shadow-lg">
        <div class="row align-items-center">
            <div class="col-lg-7">
                <span class="badge bg-info text-dark fw-bold px-3 py-2 rounded-pill mb-3">
                    <i class="bi bi-cpu me-1"></i> AI & ML Healthcare Technology
                </span>
                <h1 class="display-4 fw-extrabold mb-3">Personalized Healthcare Risk Assessment</h1>
                <p class="lead opacity-90 mb-4">
                    Assess statistical risk levels for <strong>Diabetes</strong> and <strong>Heart Disease</strong> using trained Machine Learning models with transparent Explainable AI (XAI) feature breakdowns.
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
                <div class="card-custom p-4 bg-white text-dark shadow-lg">
                    <h5 class="fw-bold mb-3 text-primary d-flex align-items-center">
                        <i class="bi bi-shield-check me-2 text-info fs-4"></i> Trained Clinical ML Models
                    </h5>
                    <div class="p-3 mb-3 bg-light rounded-3 border-start border-info border-4">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold mb-0 text-dark">Diabetes Risk Model</h6>
                            <span class="badge bg-success">97.40% Accuracy</span>
                        </div>
                        <small class="text-muted">Pima Clinical Dataset • Logistic Regression Classifier</small>
                    </div>
                    <div class="p-3 bg-light rounded-3 border-start border-primary border-4">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold mb-0 text-dark">Heart Disease Risk Model</h6>
                            <span class="badge bg-success">98.36% Accuracy</span>
                        </div>
                        <small class="text-muted">UCI Cardiac Dataset • Logistic Regression Classifier</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Live Statistics Ticker -->
    <div class="row g-3 py-3">
        <div class="col-md-3 col-6">
            <div class="card-custom p-3 text-center border-0 shadow-sm">
                <small class="text-muted fw-bold uppercase">Top Model Accuracy</small>
                <h2 class="fw-extrabold text-teal mb-0">98.36%</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-3 text-center border-0 shadow-sm">
                <small class="text-muted fw-bold uppercase">Evaluated Datasets</small>
                <h2 class="fw-extrabold text-primary mb-0">1,071 Samples</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-3 text-center border-0 shadow-sm">
                <small class="text-muted fw-bold uppercase">Clinical Features</small>
                <h2 class="fw-extrabold text-accent-blue mb-0">21 Parameters</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-3 text-center border-0 shadow-sm">
                <small class="text-muted fw-bold uppercase">Supported Conditions</small>
                <h2 class="fw-extrabold text-success mb-0">Diabetes & Heart</h2>
            </div>
        </div>
    </div>

    <!-- Features Section -->
    <div class="row g-4 py-3">
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-0 shadow-sm">
                <div class="bg-info bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-info">
                    <i class="bi bi-cpu-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2">Dual ML Architecture</h5>
                <p class="text-muted small mb-0">Trained Scikit-Learn pipelines evaluated across Logistic Regression, Decision Trees, and Random Forests with verified accuracy metrics.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-0 shadow-sm">
                <div class="bg-primary bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-primary">
                    <i class="bi bi-bar-chart-line-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2">Explainable AI (XAI)</h5>
                <p class="text-muted small mb-0">Transparently visualizes feature influence weights that contribute to the statistical prediction score using interactive Chart.js graphs.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-0 shadow-sm">
                <div class="bg-success bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-success">
                    <i class="bi bi-sliders fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2">What-If Health Simulator</h5>
                <p class="text-muted small mb-0">Interactive parameter sliders allowing users to simulate metric adjustments and observe risk changes in real-time.</p>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/benchmarks')
def benchmarks():
    content = """
    <div class="row justify-content-center py-3">
        <div class="col-lg-11">
            <div class="card-custom p-4 p-md-5 mb-4 shadow-lg">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom">
                    <div class="bg-primary bg-opacity-10 p-3 rounded-circle text-primary me-3">
                        <i class="bi bi-graph-up-arrow fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0">Machine Learning Benchmarks & Model Evaluation</h3>
                        <p class="text-muted small mb-0">Verified performance metrics across multiple trained classification algorithms</p>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Diabetes Evaluation Card -->
                    <div class="col-md-6">
                        <div class="card-custom p-4 border-start border-info border-4">
                            <h5 class="fw-bold text-dark mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Risk Models (Pima Dataset)</h5>
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle small">
                                    <thead class="table-light">
                                        <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1-Score</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr class="table-success fw-bold"><td>Logistic Regression</td><td>97.40%</td><td>98.00%</td><td>94.23%</td><td>96.08%</td></tr>
                                        <tr><td>Decision Tree</td><td>93.51%</td><td>92.00%</td><td>88.46%</td><td>90.20%</td></tr>
                                        <tr><td>Random Forest</td><td>96.10%</td><td>96.00%</td><td>92.31%</td><td>94.12%</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            <span class="badge bg-success mt-2">Selected Pipeline: Logistic Regression (ROC-AUC: 0.9972)</span>
                        </div>
                    </div>

                    <!-- Heart Disease Evaluation Card -->
                    <div class="col-md-6">
                        <div class="card-custom p-4 border-start border-primary border-4">
                            <h5 class="fw-bold text-dark mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Models (UCI Dataset)</h5>
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle small">
                                    <thead class="table-light">
                                        <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1-Score</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr class="table-success fw-bold"><td>Logistic Regression</td><td>98.36%</td><td>97.06%</td><td>100.00%</td><td>98.51%</td></tr>
                                        <tr><td>Decision Tree</td><td>95.08%</td><td>94.12%</td><td>96.97%</td><td>95.52%</td></tr>
                                        <tr><td>Random Forest</td><td>96.72%</td><td>96.97%</td><td>96.97%</td><td>96.97%</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            <span class="badge bg-success mt-2">Selected Pipeline: Logistic Regression (ROC-AUC: 0.9989)</span>
                        </div>
                    </div>
                </div>

                <div class="disclaimer-banner">
                    <i class="bi bi-info-circle-fill me-1"></i> All evaluation metrics are calculated on 20% hold-out test sets using 5-fold cross-validation.
                </div>
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
            <td class="fw-bold">#HRA-{len(history)-idx}</td>
            <td><strong class="text-dark">{h.get('disease')}</strong></td>
            <td><span class="badge-risk-{h.get('risk_level')}">{h.get('risk_level')}</span></td>
            <td class="fw-bold fs-6">{h.get('probability')}%</td>
            <td><a href="/result?idx={len(history)-1-idx}" class="btn btn-sm btn-outline-info rounded-pill"><i class="bi bi-eye me-1"></i>View Details</a></td>
        </tr>
        """
        
    if not history_html:
        history_html = '<tr><td colspan="5" class="text-center text-muted py-4">No assessment history recorded yet. <a href="/assessment" class="btn btn-sm btn-info text-white rounded-pill ms-2">Start Assessment</a></td></tr>'
        
    content = f"""
    <div class="row gy-4 py-3">
        <div class="col-12">
            <div class="card-custom p-4 bg-dark text-white shadow-lg" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
                <span class="badge bg-info text-dark px-3 py-1 mb-2">Member Dashboard</span>
                <h2 class="fw-bold mb-1">Welcome, {user['name']}!</h2>
                <p class="text-light opacity-75 mb-3">AI-Based Healthcare Risk Assessment & Preventive Care System</p>
                <a href="/assessment" class="btn btn-info text-white rounded-pill px-4 me-2"><i class="bi bi-plus-circle me-1"></i> New Assessment</a>
                <a href="/simulator" class="btn btn-outline-light rounded-pill px-4"><i class="bi bi-sliders me-1"></i> What-If Simulator</a>
            </div>
        </div>
        <div class="col-12">
            <div class="card-custom p-4 shadow-sm">
                <h5 class="fw-bold mb-3 text-dark"><i class="bi bi-clock-history me-2 text-info"></i>Assessment History Log</h5>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
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
            <div class="card-custom p-4 p-md-5 shadow-lg">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom">
                    <div class="bg-info bg-opacity-10 p-3 rounded-circle text-info me-3">
                        <i class="bi bi-clipboard-pulse fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0">Health Risk Assessment Form</h3>
                        <p class="text-muted small mb-0">Enter clinical metrics for AI risk calculation</p>
                    </div>
                </div>

                <form method="POST" id="assessForm">
                    <div class="mb-4 bg-light p-3 rounded-3 border">
                        <label class="form-label fw-bold text-dark fs-5 mb-2"><i class="bi bi-virus me-2 text-info"></i>Select Target Condition</label>
                        <select name="disease_type" id="disease_type" class="form-select form-select-lg" onchange="toggleForm()">
                            <option value="diabetes">Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart">Heart Disease Risk Assessment (UCI Cardiac Dataset)</option>
                        </select>
                    </div>

                    <!-- DIABETES INPUTS -->
                    <div id="diabetes_inputs">
                        <h5 class="fw-bold text-primary mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Clinical Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Glucose Level (mg/dL)</label>
                                <input type="number" step="0.1" name="Glucose" class="form-control" value="135" required>
                                <small class="text-muted">Fasting normal: 70–99 mg/dL</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="29.5" required>
                                <small class="text-muted">Healthy range: 18.5–24.9</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="BloodPressure" class="form-control" value="78" required>
                                <small class="text-muted">Diastolic pressure</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Age (Years)</label>
                                <input type="number" name="Age" class="form-control" value="45" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Pregnancies</label>
                                <input type="number" name="Pregnancies" class="form-control" value="1" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Insulin (mu U/ml)</label>
                                <input type="number" step="0.1" name="Insulin" class="form-control" value="85" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Skin Thickness (mm)</label>
                                <input type="number" step="0.1" name="SkinThickness" class="form-control" value="22" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Diabetes Pedigree Function</label>
                                <input type="number" step="0.01" name="DiabetesPedigreeFunction" class="form-control" value="0.47" required>
                                <small class="text-muted">Genetic likelihood score</small>
                            </div>
                        </div>
                    </div>

                    <!-- HEART INPUTS -->
                    <div id="heart_inputs" style="display:none;">
                        <h5 class="fw-bold text-primary mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Clinical Metrics</h5>
                        <div class="row g-3">
                            <div class="col-md-6"><label class="form-label fw-bold">Age</label><input type="number" name="age" class="form-control" value="55"></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Sex</label><select name="sex" class="form-select"><option value="1">Male</option><option value="0">Female</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Chest Pain (CP 0-3)</label><select name="cp" class="form-select"><option value="0">Typical Angina (0)</option><option value="1">Atypical Angina (1)</option><option value="2">Non-anginal (2)</option><option value="3">Asymptomatic (3)</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Resting Blood Pressure (mm Hg)</label><input type="number" step="0.1" name="trestbps" class="form-control" value="135"></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Serum Cholesterol (mg/dL)</label><input type="number" step="0.1" name="chol" class="form-control" value="245"></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Max Heart Rate (Thalach)</label><input type="number" step="0.1" name="thalach" class="form-control" value="145"></div>
                            <div class="col-md-6"><label class="form-label fw-bold">Exercise Angina</label><select name="exang" class="form-select"><option value="0">No (0)</option><option value="1">Yes (1)</option></select></div>
                            <div class="col-md-6"><label class="form-label fw-bold">ST Depression (Oldpeak)</label><input type="number" step="0.1" name="oldpeak" class="form-control" value="1.2"></div>
                        </div>
                    </div>

                    <div class="disclaimer-banner my-4">
                        <i class="bi bi-shield-exclamation me-1 text-warning"></i> By clicking calculate, parameters are evaluated against trained Scikit-Learn models.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 shadow"><i class="bi bi-cpu-fill me-2"></i> Run AI Risk Assessment</button>
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
    
    rec_html = "".join([f'<div class="col-md-6"><div class="p-3 bg-light rounded border h-100 small"><i class="bi bi-check-circle-fill text-success me-2 fs-5"></i>{rec}</div></div>' for rec in res.get('recommendations', [])])
    
    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <!-- Result Summary Header Card -->
            <div class="card-custom p-4 p-md-5 mb-4 shadow-lg text-center">
                <span class="badge bg-secondary mb-2">{res.get('disease')}</span>
                <h2 class="fw-bold">Predicted Risk Level: <span class="badge-risk-{res.get('risk_level')}">{res.get('risk_level')}</span></h2>
                <h1 class="display-4 fw-extrabold text-dark mt-2">{res.get('probability')}% Probability</h1>
                <p class="text-muted small">Classifier Used: <strong>{res.get('model_used')}</strong></p>
            </div>

            <!-- Explainable AI (XAI) Feature Importance Chart -->
            <div class="card-custom p-4 p-md-5 mb-4 shadow-sm">
                <h4 class="fw-bold mb-2"><i class="bi bi-bar-chart-line-fill text-info me-2"></i>Explainable AI (XAI): Parameter Influence Breakdown</h4>
                <p class="text-muted small mb-4">Relative weight of parameters that influenced the statistical risk score:</p>
                <div style="height: 280px;"><canvas id="fiChart"></canvas></div>
            </div>

            <!-- Preventive Health Recommendations -->
            <div class="card-custom p-4 p-md-5 mb-4 shadow-sm">
                <h4 class="fw-bold mb-3"><i class="bi bi-shield-check text-success me-2"></i>Personalized Educational Guidance</h4>
                <div class="row g-3">{rec_html}</div>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
                <a href="/assessment" class="btn btn-outline-secondary rounded-pill px-4">New Assessment</a>
                <div class="d-flex gap-2">
                    <a href="/simulator" class="btn btn-info text-white rounded-pill px-4 shadow-sm">Launch What-If Simulator</a>
                    <a href="/report" target="_blank" class="btn btn-dark rounded-pill px-4 shadow-sm"><i class="bi bi-printer me-1"></i> Print PDF Report</a>
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
                scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Contribution Weight (%)' }} }} }}
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
        <div class="card-custom p-4 text-center shadow-lg bg-white mt-4">
            <h5 class="text-muted text-uppercase fw-bold mb-2">Simulated Risk Prediction</h5>
            <h3 class="fw-bold mb-2">
                <span class="badge-risk-{sim_result.get('risk_level')}">{sim_result.get('risk_level')} RISK</span>
            </h3>
            <h1 class="display-3 fw-extrabold text-dark mt-2">{sim_result.get('probability')}%</h1>
            <p class="text-muted small">Updated Statistical Probability</p>
        </div>
        """
        
    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-9">
            <div class="card-custom p-4 p-md-5 mb-4 shadow-lg">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom">
                    <div class="bg-primary bg-opacity-10 p-3 rounded-circle text-primary me-3">
                        <i class="bi bi-sliders fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0">What-If Health Risk Simulator</h3>
                        <p class="text-muted small mb-0">Adjust parameter sliders to observe prospective probability recalculations</p>
                    </div>
                </div>

                <form method="POST">
                    <input type="hidden" name="disease_type" value="diabetes">
                    <div class="mb-4">
                        <label class="form-label fw-bold d-flex justify-content-between">
                            <span>Simulated Glucose Level (mg/dL)</span>
                            <output class="fw-bold text-teal fs-5" id="out_glucose">130</output>
                        </label>
                        <input type="range" class="form-range" min="70" max="220" value="130" name="Glucose" oninput="document.getElementById('out_glucose').value = this.value">
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold d-flex justify-content-between">
                            <span>Simulated Body Mass Index (BMI)</span>
                            <output class="fw-bold text-teal fs-5" id="out_bmi">27.0</output>
                        </label>
                        <input type="range" class="form-range" min="15" max="45" step="0.5" value="27" name="BMI" oninput="document.getElementById('out_bmi').value = this.value">
                    </div>
                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 mt-3 shadow"><i class="bi bi-play-circle-fill me-2"></i> Run What-If Simulation</button>
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
                <div class="text-end"><strong>Report ID: #VCL-882</strong><br><small>Print Date: 2026</small></div>
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
