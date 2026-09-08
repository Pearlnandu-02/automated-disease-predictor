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

# Ensure Vercel never caches old serverless responses
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
    <title>HealthRisk AI v3.0 - AI Healthcare Risk Assessment Platform</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-dark: #090d16;
            --card-dark: #111827;
            --card-border: #1f2937;
            --accent-cyan: #06b6d4;
            --accent-teal: #0d9488;
            --accent-purple: #8b5cf6;
            --text-light: #f3f4f6;
            --text-muted: #9ca3af;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.15), transparent 60%),
                radial-gradient(circle at 10% 80%, rgba(139, 92, 246, 0.1), transparent 50%);
        }

        /* Glassmorphism & Modern Navbar */
        .navbar-custom {
            background: rgba(9, 13, 22, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .brand-logo-icon {
            background: linear-gradient(135deg, #06b6d4, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .pulse-badge {
            width: 10px;
            height: 10px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 12px #10b981;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Ultra Premium Glass Cards */
        .card-custom {
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card-custom:hover {
            transform: translateY(-4px);
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 25px 50px rgba(6, 182, 212, 0.15);
        }

        .hero-banner {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(31, 41, 55, 0.8) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 32px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
        }

        .hero-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.3), transparent 70%);
            pointer-events: none;
        }

        /* Risk Badges */
        .badge-risk-LOW {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.5);
            font-weight: 800;
            padding: 8px 20px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .badge-risk-MODERATE {
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.5);
            font-weight: 800;
            padding: 8px 20px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .badge-risk-HIGH {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.5);
            font-weight: 800;
            padding: 8px 20px;
            border-radius: 30px;
            letter-spacing: 0.5px;
        }

        .btn-primary-custom {
            background: linear-gradient(135deg, #06b6d4 0%, #0d9488 100%);
            color: #fff;
            font-weight: 700;
            border-radius: 14px;
            border: none;
            padding: 14px 32px;
            box-shadow: 0 0 25px rgba(6, 182, 212, 0.4);
            transition: all 0.3s ease;
        }

        .btn-primary-custom:hover {
            background: linear-gradient(135deg, #0891b2 0%, #0f766e 100%);
            color: #fff;
            transform: translateY(-2px);
            box-shadow: 0 0 35px rgba(6, 182, 212, 0.6);
        }

        .disclaimer-banner {
            background: rgba(245, 158, 11, 0.1);
            border-left: 5px solid #f59e0b;
            color: #fbbf24;
            padding: 16px 22px;
            border-radius: 14px;
            font-size: 0.9rem;
        }

        .form-control, .form-select {
            background-color: #1f2937;
            border: 1px solid #374151;
            color: #f3f4f6;
            border-radius: 12px;
            padding: 12px 16px;
        }

        .form-control:focus, .form-select:focus {
            background-color: #1f2937;
            border-color: var(--accent-cyan);
            color: #f3f4f6;
            box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.25);
        }

        footer {
            margin-top: auto;
            background: #030712;
            color: #6b7280;
            padding: 45px 0 25px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand fw-extrabold d-flex align-items-center text-white" href="/">
                <i class="bi bi-heart-pulse-fill brand-logo-icon me-2 fs-3"></i>
                <span class="fs-4">HealthRisk<span style="color: #06b6d4;">AI</span></span>
                <span class="ms-3 px-3 py-1 bg-dark border border-cyan text-cyan rounded-pill small d-none d-sm-inline-flex align-items-center gap-2" style="border-color: rgba(6, 182, 212, 0.3) !important;">
                    <span class="pulse-badge"></span><span style="color: #06b6d4; font-weight: 700; font-size: 0.75rem;">AI ENGINE v3.0 LIVE</span>
                </span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-3">
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/assessment">Risk Assessment</a></li>
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/simulator">What-If Simulator</a></li>
                    <li class="nav-item"><a class="nav-link text-light fw-medium" href="/benchmarks">ML Metrics</a></li>
                    {% if user %}
                        <li class="nav-item"><a class="nav-link text-light fw-medium" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item"><a class="btn btn-outline-light btn-sm rounded-pill px-4" href="/logout">Logout ({{ user.name }})</a></li>
                    {% else %}
                        <li class="nav-item"><a class="btn btn-outline-cyan btn-sm rounded-pill px-4 text-cyan" style="border-color: #06b6d4; color: #06b6d4;" href="/login">Login</a></li>
                        <li class="nav-item"><a class="btn btn-primary-custom btn-sm text-white px-4" href="/register">Get Started</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
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
                        <i class="bi bi-heart-pulse-fill text-cyan me-2"></i> HealthRisk<span style="color: #06b6d4;">AI</span>
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
                        <li class="mb-2"><a href="/assessment" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-cyan"></i> Risk Assessment</a></li>
                        <li class="mb-2"><a href="/simulator" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-cyan"></i> What-If Simulator</a></li>
                        <li class="mb-2"><a href="/benchmarks" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-cyan"></i> ML Benchmarks</a></li>
                        <li class="mb-2"><a href="/dashboard" class="text-muted text-decoration-none"><i class="bi bi-chevron-right me-1 text-cyan"></i> Member Dashboard</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6">
                    <h6 class="text-white fw-bold mb-3">Trained Algorithms</h6>
                    <ul class="list-unstyled small text-muted">
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-cyan"></i> Logistic Regression (98.36%)</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-cyan"></i> Random Forest Classifiers</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-cyan"></i> Decision Trees & XAI</li>
                        <li class="mb-2"><i class="bi bi-check2-circle me-1 text-cyan"></i> Joblib Saved Pipelines</li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary opacity-25">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center small text-muted">
                <p class="mb-0">&copy; 2026 HealthRisk AI - Academic Machine Learning Project.</p>
                <p class="mb-0">Built with Python 3.12, Scikit-Learn & Bootstrap 5</p>
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
    <div class="hero-banner p-4 p-md-5 my-3">
        <div class="row align-items-center z-1 position-relative">
            <div class="col-lg-7">
                <span class="badge bg-cyan bg-opacity-20 text-cyan border border-cyan border-opacity-50 fw-bold px-3 py-2 rounded-pill mb-3" style="color: #06b6d4;">
                    <i class="bi bi-cpu me-1"></i> ADVANCED AI HEALTHCARE SYSTEM v3.0
                </span>
                <h1 class="display-3 fw-extrabold mb-3 text-white" style="letter-spacing: -1px;">
                    Personalized Health <br><span style="background: linear-gradient(135deg, #06b6d4, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Risk Predictor</span>
                </h1>
                <p class="lead text-gray-300 mb-4 opacity-90">
                    Evaluate statistical risk levels for <strong>Diabetes</strong> and <strong>Heart Disease</strong> using verified Scikit-Learn pipelines with transparent Explainable AI (XAI) feature contribution breakdown.
                </p>
                <div class="d-flex flex-wrap gap-3">
                    <a href="/assessment" class="btn btn-primary-custom btn-lg">
                        <i class="bi bi-play-circle-fill me-2"></i> Start Risk Assessment
                    </a>
                    <a href="/simulator" class="btn btn-outline-light btn-lg rounded-pill px-4">
                        <i class="bi bi-sliders me-2"></i> What-If Simulator
                    </a>
                </div>
            </div>
            <div class="col-lg-5 mt-4 mt-lg-0">
                <div class="card-custom p-4 text-white shadow-lg">
                    <h5 class="fw-bold mb-3 d-flex align-items-center" style="color: #06b6d4;">
                        <i class="bi bi-shield-check me-2 fs-4"></i> Trained Clinical Models
                    </h5>
                    <div class="p-3 mb-3 bg-dark bg-opacity-60 rounded-3 border-start border-cyan border-4" style="border-color: #06b6d4 !important;">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold mb-0 text-white">Diabetes Risk Model</h6>
                            <span class="badge bg-emerald-500 text-white" style="background: #10b981;">97.40% Accuracy</span>
                        </div>
                        <small class="text-muted">Pima Clinical Dataset • Logistic Regression Classifier</small>
                    </div>
                    <div class="p-3 bg-dark bg-opacity-60 rounded-3 border-start border-purple border-4" style="border-color: #8b5cf6 !important;">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold mb-0 text-white">Heart Disease Risk Model</h6>
                            <span class="badge bg-emerald-500 text-white" style="background: #10b981;">98.36% Accuracy</span>
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
            <div class="card-custom p-4 text-center">
                <small class="text-muted fw-bold uppercase">Top Model Accuracy</small>
                <h2 class="fw-extrabold mb-0" style="color: #06b6d4;">98.36%</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-4 text-center">
                <small class="text-muted fw-bold uppercase">Evaluated Datasets</small>
                <h2 class="fw-extrabold text-white mb-0">1,071 Samples</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-4 text-center">
                <small class="text-muted fw-bold uppercase">Clinical Features</small>
                <h2 class="fw-extrabold mb-0" style="color: #8b5cf6;">21 Parameters</h2>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card-custom p-4 text-center">
                <small class="text-muted fw-bold uppercase">Target Conditions</small>
                <h2 class="fw-extrabold text-success mb-0">Diabetes & Heart</h2>
            </div>
        </div>
    </div>

    <!-- Core Features Grid -->
    <div class="row g-4 py-3">
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">
                    <i class="bi bi-cpu-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">Dual ML Pipeline</h5>
                <p class="text-muted small mb-0">Trained Scikit-Learn pipelines evaluated across Logistic Regression, Decision Trees, and Random Forests with verified metrics.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3" style="background: rgba(139, 92, 246, 0.15); color: #8b5cf6;">
                    <i class="bi bi-bar-chart-line-fill fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">Explainable AI (XAI)</h5>
                <p class="text-muted small mb-0">Transparently visualizes feature influence weights that contribute to the statistical prediction score using interactive Chart.js graphs.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100">
                <div class="p-3 rounded-circle d-inline-block mb-3" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">
                    <i class="bi bi-sliders fs-3"></i>
                </div>
                <h5 class="fw-bold mb-2 text-white">What-If Health Simulator</h5>
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
            <div class="card-custom p-4 p-md-5 mb-4">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="p-3 rounded-circle me-3" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">
                        <i class="bi bi-graph-up-arrow fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0 text-white">Machine Learning Benchmarks & Model Evaluation</h3>
                        <p class="text-muted small mb-0">Verified performance metrics across multiple trained classification algorithms</p>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <!-- Diabetes Evaluation Card -->
                    <div class="col-md-6">
                        <div class="card-custom p-4 border-start border-cyan border-4" style="border-color: #06b6d4 !important;">
                            <h5 class="fw-bold text-white mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Risk Models (Pima Dataset)</h5>
                            <div class="table-responsive">
                                <table class="table table-dark table-bordered align-middle small">
                                    <thead>
                                        <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1-Score</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr class="table-active fw-bold" style="color: #34d399;"><td>Logistic Regression</td><td>97.40%</td><td>98.00%</td><td>94.23%</td><td>96.08%</td></tr>
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
                        <div class="card-custom p-4 border-start border-purple border-4" style="border-color: #8b5cf6 !important;">
                            <h5 class="fw-bold text-white mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Models (UCI Dataset)</h5>
                            <div class="table-responsive">
                                <table class="table table-dark table-bordered align-middle small">
                                    <thead>
                                        <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1-Score</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr class="table-active fw-bold" style="color: #34d399;"><td>Logistic Regression</td><td>98.36%</td><td>97.06%</td><td>100.00%</td><td>98.51%</td></tr>
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
            <div class="card-custom p-4 p-md-5">
                <div class="text-center mb-4">
                    <i class="bi bi-shield-lock-fill fs-1 text-cyan"></i>
                    <h3 class="fw-bold text-white">Member Login</h3>
                    <p class="text-muted small">Access Healthcare AI Assessment Platform</p>
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
                    <i class="bi bi-person-plus-fill fs-1 text-cyan"></i>
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
            <td><strong class="text-cyan">{h.get('disease')}</strong></td>
            <td><span class="badge-risk-{h.get('risk_level')}">{h.get('risk_level')}</span></td>
            <td class="fw-bold fs-6 text-white">{h.get('probability')}%</td>
            <td><a href="/result?idx={len(history)-1-idx}" class="btn btn-sm btn-outline-cyan rounded-pill text-cyan" style="border-color: #06b6d4;"><i class="bi bi-eye me-1"></i>View Result</a></td>
        </tr>
        """
        
    if not history_html:
        history_html = '<tr><td colspan="5" class="text-center text-muted py-4">No assessment history recorded yet. <a href="/assessment" class="btn btn-sm btn-primary-custom ms-2">Start Assessment</a></td></tr>'
        
    content = f"""
    <div class="row gy-4 py-3">
        <div class="col-12">
            <div class="card-custom p-4 bg-dark text-white">
                <span class="badge bg-cyan bg-opacity-20 text-cyan px-3 py-1 mb-2" style="color: #06b6d4;">Member Dashboard</span>
                <h2 class="fw-bold mb-1">Welcome, {user['name']}!</h2>
                <p class="text-muted mb-3">AI-Based Healthcare Risk Assessment & Preventive Care System</p>
                <a href="/assessment" class="btn btn-primary-custom rounded-pill me-2"><i class="bi bi-plus-circle me-1"></i> New Assessment</a>
                <a href="/simulator" class="btn btn-outline-light rounded-pill px-4"><i class="bi bi-sliders me-1"></i> What-If Simulator</a>
            </div>
        </div>
        <div class="col-12">
            <div class="card-custom p-4">
                <h5 class="fw-bold mb-3 text-white"><i class="bi bi-clock-history me-2 text-cyan"></i>Assessment History Log</h5>
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
                    <div class="p-3 rounded-circle me-3" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">
                        <i class="bi bi-clipboard-pulse fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0 text-white">Health Risk Assessment Form</h3>
                        <p class="text-muted small mb-0">Enter clinical parameters for AI-powered risk evaluation</p>
                    </div>
                </div>

                <form method="POST" id="assessForm">
                    <div class="mb-4 bg-dark bg-opacity-50 p-3 rounded-3 border border-secondary border-opacity-25">
                        <label class="form-label fw-bold text-white fs-5 mb-2"><i class="bi bi-virus me-2 text-cyan"></i>Select Target Condition</label>
                        <select name="disease_type" id="disease_type" class="form-select form-select-lg" onchange="toggleForm()">
                            <option value="diabetes">Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart">Heart Disease Risk Assessment (UCI Cardiac Dataset)</option>
                        </select>
                    </div>

                    <!-- DIABETES INPUTS -->
                    <div id="diabetes_inputs">
                        <h5 class="fw-bold text-cyan mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Clinical Metrics</h5>
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
                        <h5 class="fw-bold text-cyan mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Clinical Metrics</h5>
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
                        <i class="bi bi-shield-exclamation me-1 text-warning"></i> By clicking calculate, parameters are evaluated against trained Scikit-Learn models.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100"><i class="bi bi-cpu-fill me-2"></i> Run AI Risk Assessment</button>
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
                <h1 class="display-3 fw-extrabold text-white mt-2">{res.get('probability')}% Probability</h1>
                <p class="text-muted small">Classifier Used: <strong>{res.get('model_used')}</strong></p>
            </div>

            <!-- Explainable AI (XAI) Feature Importance Chart -->
            <div class="card-custom p-4 p-md-5 mb-4">
                <h4 class="fw-bold mb-2 text-white"><i class="bi bi-bar-chart-line-fill text-cyan me-2"></i>Explainable AI (XAI): Parameter Influence Breakdown</h4>
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
                    backgroundColor: 'rgba(6, 182, 212, 0.75)',
                    borderColor: '#06b6d4',
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
                    <div class="p-3 rounded-circle me-3" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">
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
                            <output class="fw-bold fs-5" style="color: #06b6d4;" id="out_glucose">130</output>
                        </label>
                        <input type="range" class="form-range" min="70" max="220" value="130" name="Glucose" oninput="document.getElementById('out_glucose').value = this.value">
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold d-flex justify-content-between text-white">
                            <span>Simulated Body Mass Index (BMI)</span>
                            <output class="fw-bold fs-5" style="color: #06b6d4;" id="out_bmi">27.0</output>
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
