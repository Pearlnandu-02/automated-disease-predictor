<?php
// includes/header.php
require_once __DIR__ . '/auth.php';
$current_page = basename($_SERVER['PHP_SELF']);
$user = get_logged_in_user();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= isset($page_title) ? htmlspecialchars($page_title) : 'MediSense AI | AI Disease Prediction & Health Assistance' ?></title>
    <meta name="description" content="MediSense AI - Smarter Insights. Better Health. An educational AI healthcare platform providing multi-symptom disease predictions, clinical risk assessments, health simulations, and computer vision infection & injury scanning.">
    <meta property="og:title" content="MediSense AI | Smarter Insights. Better Health.">
    <meta property="og:description" content="Smarter Insights. Better Health. Educational disease prediction, clinical risk evaluations, and visual infection & injury assessments powered by AI.">
    <meta property="og:site_name" content="MediSense AI">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%2312bfe3'><path fill-rule='evenodd' d='m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z'/></svg>">
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Prevent Theme Flash (FOUC) & Bulletproof Theme Engine -->
    <script>
    function applyTheme(theme) {
        var valid = (theme === 'light') ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', valid);
        document.documentElement.setAttribute('data-bs-theme', valid);
        try {
            localStorage.setItem('ai_healthcare_theme', valid);
            localStorage.setItem('theme', valid);
        } catch (e) {}

        var btns = document.querySelectorAll('.theme-toggle-btn, #themeToggleBtn');
        btns.forEach(function(btn) {
            var darkIcon = btn.querySelector('.theme-icon-dark');
            var lightIcon = btn.querySelector('.theme-icon-light');
            var label = btn.querySelector('.theme-text');
            if (valid === 'light') {
                if (darkIcon) darkIcon.classList.add('d-none');
                if (lightIcon) lightIcon.classList.remove('d-none');
                if (label) label.textContent = 'Theme';
                btn.setAttribute('title', 'Switch to dark mode');
                btn.setAttribute('aria-label', 'Switch to dark mode');
            } else {
                if (darkIcon) darkIcon.classList.remove('d-none');
                if (lightIcon) lightIcon.classList.add('d-none');
                if (label) label.textContent = 'Theme';
                btn.setAttribute('title', 'Switch to light mode');
                btn.setAttribute('aria-label', 'Switch to light mode');
            }
        });
    }

    function toggleSiteTheme() {
        var current = document.documentElement.getAttribute('data-theme') || 'dark';
        var next = (current === 'dark') ? 'light' : 'dark';
        applyTheme(next);
    }

    (function() {
        var urlParams = new URLSearchParams(window.location.search);
        var urlTheme = urlParams.get('theme');
        var saved = urlTheme || localStorage.getItem('ai_healthcare_theme') || localStorage.getItem('theme');
        var theme = (saved === 'light' || saved === 'dark') ? saved : 'dark';
        if (urlTheme === 'light' || urlTheme === 'dark') {
            try {
                localStorage.setItem('ai_healthcare_theme', urlTheme);
                localStorage.setItem('theme', urlTheme);
            } catch(e) {}
        }
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.setAttribute('data-bs-theme', theme);
    })();
    </script>

    <!-- Custom CSS -->
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

    <?php
    $is_clinical_active = in_array($current_page, ['assessment.php', 'simulator.php', 'risk_calculator.php', 'report.php']);
    $is_library_active = in_array($current_page, ['diseases.php', 'disease_detail.php', 'symptoms_guide.php', 'prevention.php', 'education.php', 'emergency.php']);
    ?>
    <!-- Navigation Header -->
    <nav class="navbar navbar-expand-xl navbar-custom sticky-top">
        <div class="container">
            <!-- Brand Logo -->
            <a class="navbar-brand d-flex align-items-center me-3 me-xl-4" href="index.php">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4 fw-bold">MediSense<span class="text-info"> AI</span></span>
            </a>

            <!-- Mobile Hamburger Toggler -->
            <button class="navbar-toggler border-0 shadow-none px-2" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
                <i class="bi bi-list fs-2 text-primary-theme"></i>
            </button>

            <!-- Navbar Collapse -->
            <div class="collapse navbar-collapse" id="navbarMain">
                <!-- Navigation Links -->
                <ul class="navbar-nav me-xl-auto mb-2 mb-xl-0 align-items-xl-center gap-xl-1 py-2 py-xl-0 small fw-semibold">
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'index.php' ? 'active text-info fw-bold' : '' ?>" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'about.php' ? 'active text-info fw-bold' : '' ?>" href="about.php">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'prediction.php' ? 'active text-info fw-bold' : '' ?>" href="prediction.php">
                            <i class="bi bi-cpu me-1 text-info"></i>AI Prediction
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'image_scanner.php' ? 'active text-info fw-bold' : '' ?>" href="image_scanner.php">
                            <i class="bi bi-camera me-1 text-info"></i>Injury Scanner
                        </a>
                    </li>

                    <!-- Clinical Tools Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle d-inline-flex align-items-center gap-1 <?= $is_clinical_active ? 'active text-info fw-bold' : '' ?>" href="#" id="clinicalToolsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <span>Clinical Tools</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-custom shadow-lg border-0" aria-labelledby="clinicalToolsDropdown">
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'assessment.php' ? 'active-sub' : '' ?>" href="assessment.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-shield-check fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Clinical Risk Assessment</div>
                                        <div class="dropdown-item-desc">Comprehensive multi-parameter clinical evaluation.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'risk_calculator.php' ? 'active-sub' : '' ?>" href="risk_calculator.php">
                                    <div class="dropdown-icon-box text-warning mt-1">
                                        <i class="bi bi-calculator fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Health Risk Calculator</div>
                                        <div class="dropdown-item-desc">Interactive BMI, cardiac, metabolic & lifestyle risks.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'prediction.php' ? 'active-sub' : '' ?>" href="prediction.php">
                                    <div class="dropdown-icon-box text-primary mt-1">
                                        <i class="bi bi-activity fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Symptom Checker</div>
                                        <div class="dropdown-item-desc">Multi-symptom AI disease correlation screening.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'simulator.php' ? 'active-sub' : '' ?>" href="simulator.php">
                                    <div class="dropdown-icon-box text-success mt-1">
                                        <i class="bi bi-sliders fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Health Simulator</div>
                                        <div class="dropdown-item-desc">Explore educational health calculations & what-if scenarios.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'report.php' ? 'active-sub' : '' ?>" href="report.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-file-earmark-medical fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Health Reports</div>
                                        <div class="dropdown-item-desc">View and download printable health summaries.</div>
                                    </div>
                                </a>
                            </li>
                        </ul>
                    </li>

                    <!-- Health Library Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle d-inline-flex align-items-center gap-1 <?= $is_library_active ? 'active text-info fw-bold' : '' ?>" href="#" id="healthLibraryDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <span>Health Library</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-custom shadow-lg border-0" aria-labelledby="healthLibraryDropdown">
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= in_array($current_page, ['diseases.php', 'disease_detail.php']) ? 'active-sub' : '' ?>" href="diseases.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-journal-medical fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Disease Library</div>
                                        <div class="dropdown-item-desc">Explore 70+ categorized conditions & clinical summaries.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'symptoms_guide.php' ? 'active-sub' : '' ?>" href="symptoms_guide.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-diagram-3-fill fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Symptoms Guide</div>
                                        <div class="dropdown-item-desc">Browse clinical symptoms & associated conditions.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'prevention.php' ? 'active-sub' : '' ?>" href="prevention.php">
                                    <div class="dropdown-icon-box text-success mt-1">
                                        <i class="bi bi-heart-pulse-fill fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Prevention Center</div>
                                        <div class="dropdown-item-desc">10 essential preventive health domains & practical tips.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'education.php' ? 'active-sub' : '' ?>" href="education.php">
                                    <div class="dropdown-icon-box text-warning mt-1">
                                        <i class="bi bi-book-half fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Health Education</div>
                                        <div class="dropdown-item-desc">Articles, FAQs, glossary, myths vs facts & AI guide.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'emergency.php' ? 'active-sub' : '' ?>" href="emergency.php">
                                    <div class="dropdown-icon-box text-danger mt-1">
                                        <i class="bi bi-hospital fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Emergency Guide</div>
                                        <div class="dropdown-item-desc">Critical warning signs requiring immediate medical care.</div>
                                    </div>
                                </a>
                            </li>
                        </ul>
                    </li>

                    <li class="nav-item">
                        <a class="nav-link <?= in_array($current_page, ['dashboard.php', 'profile.php', 'history.php']) ? 'active text-info fw-bold' : '' ?>" href="dashboard.php">
                            <i class="bi bi-speedometer2 me-1"></i>Dashboard
                        </a>
                    </li>
                </ul>

                <!-- Right Actions Area -->
                <div class="navbar-actions d-flex align-items-center gap-2">
                    <!-- Global Search Trigger -->
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-1 d-inline-flex align-items-center gap-2" data-bs-toggle="modal" data-bs-target="#globalSearchModal" title="Global Search (Ctrl+K)">
                        <i class="bi bi-search"></i>
                        <span class="d-none d-md-inline small">Search</span>
                        <kbd class="bg-secondary bg-opacity-25 text-body small px-1 rounded border border-secondary border-opacity-25" style="font-size: 0.65rem;">⌘K</kbd>
                    </button>

                    <!-- Compact Icon-Based Theme Toggle Button -->
                    <button id="themeToggleBtn" type="button" class="theme-toggle-btn" onclick="toggleSiteTheme()" title="Switch to dark mode" aria-label="Switch to dark mode">
                        <i class="bi bi-moon-stars-fill theme-icon-dark text-warning"></i>
                        <i class="bi bi-sun-fill theme-icon-light text-warning d-none"></i>
                        <span class="theme-text">Theme</span>
                    </button>
                    <script>
                    (function() {
                        var t = document.documentElement.getAttribute('data-theme') || 'dark';
                        if (typeof applyTheme === 'function') {
                            applyTheme(t);
                        }
                    })();
                    </script>

                    <?php if (is_logged_in()): ?>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-info dropdown-toggle rounded-pill px-3 py-1" type="button" id="userMenuDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="bi bi-person-circle me-1"></i> <?= sanitize($user['name']) ?>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end dropdown-menu-custom shadow-lg border-0" aria-labelledby="userMenuDropdown">
                                <li>
                                    <a class="dropdown-item py-2 px-3 <?= $current_page == 'profile.php' ? 'active-sub' : '' ?>" href="profile.php">
                                        <i class="bi bi-person-lines-fill me-2 text-info"></i> Personal Health Profile
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item py-2 px-3 <?= $current_page == 'history.php' ? 'active-sub' : '' ?>" href="history.php">
                                        <i class="bi bi-clock-history me-2 text-primary"></i> Assessment History
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item py-2 px-3 <?= $current_page == 'health_assistant.php' ? 'active-sub' : '' ?>" href="health_assistant.php">
                                        <i class="bi bi-chat-heart me-2 text-success"></i> AI Health Assistant
                                    </a>
                                </li>
                                <li><hr class="dropdown-divider opacity-25"></li>
                                <li>
                                    <a class="dropdown-item py-2 px-3 text-danger" href="logout.php">
                                        <i class="bi bi-box-arrow-right me-2"></i> Logout
                                    </a>
                                </li>
                            </ul>
                        </div>
                    <?php else: ?>
                        <a class="btn-nav-login" href="login.php">Login</a>
                        <a class="btn-nav-register" href="register.php">Register</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="py-4">
        <div class="container">
            <?php display_flash_message(); ?>
