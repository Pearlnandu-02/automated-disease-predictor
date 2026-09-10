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
    <title>AI Healthcare - Intelligent Disease Prediction & Health Assistance System</title>
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
                if (label) label.textContent = 'Light';
                btn.setAttribute('title', 'Switch to Dark Mode');
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
            } else {
                if (darkIcon) darkIcon.classList.remove('d-none');
                if (lightIcon) lightIcon.classList.add('d-none');
                if (label) label.textContent = 'Dark';
                btn.setAttribute('title', 'Switch to Light Mode');
                btn.setAttribute('aria-label', 'Switch to Light Mode');
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
    $is_clinical_active = in_array($current_page, ['assessment.php', 'simulator.php']);
    $is_library_active = in_array($current_page, ['diseases.php', 'disease_detail.php', 'symptoms_guide.php', 'prevention.php']);
    ?>
    <!-- Navigation Header -->
    <nav class="navbar navbar-expand-xl navbar-custom sticky-top">
        <div class="container">
            <!-- Brand Logo -->
            <a class="navbar-brand d-flex align-items-center me-3 me-xl-4" href="index.php">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4 fw-bold">AI Healthcare<span class="text-info">.</span></span>
            </a>

            <!-- Mobile Hamburger Toggler -->
            <button class="navbar-toggler border-0 shadow-none px-2" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
                <i class="bi bi-list fs-2 text-primary-theme"></i>
            </button>

            <!-- Navbar Collapse -->
            <div class="collapse navbar-collapse" id="navbarMain">
                <!-- Center Links -->
                <ul class="navbar-nav mx-auto mb-2 mb-xl-0 align-items-xl-center gap-xl-1 py-2 py-xl-0 small fw-semibold">
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
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= ($current_page == 'assessment.php' && ($_GET['type'] ?? '') !== 'diabetes') ? 'active-sub' : '' ?>" href="assessment.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-shield-check fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Clinical Risk Assessment</div>
                                        <div class="dropdown-item-desc">Evaluate selected health risk factors.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'simulator.php' ? 'active-sub' : '' ?>" href="simulator.php">
                                    <div class="dropdown-icon-box text-info mt-1">
                                        <i class="bi bi-sliders fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Health Simulator</div>
                                        <div class="dropdown-item-desc">Explore educational health calculations.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= ($current_page == 'assessment.php' && ($_GET['type'] ?? '') === 'diabetes') ? 'active-sub' : '' ?>" href="assessment.php?type=diabetes">
                                    <div class="dropdown-icon-box text-danger mt-1">
                                        <i class="bi bi-droplet-fill fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Diabetes Assessment</div>
                                        <div class="dropdown-item-desc">Review diabetes-related health indicators.</div>
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
                                        <div class="dropdown-item-title">Diseases Library</div>
                                        <div class="dropdown-item-desc">Explore supported conditions.</div>
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
                                        <div class="dropdown-item-desc">Browse symptoms and associated conditions.</div>
                                    </div>
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item d-flex align-items-start gap-3 py-2 px-3 rounded-3 <?= $current_page == 'prevention.php' ? 'active-sub' : '' ?>" href="prevention.php">
                                    <div class="dropdown-icon-box text-success mt-1">
                                        <i class="bi bi-heart-pulse-fill fs-5"></i>
                                    </div>
                                    <div>
                                        <div class="dropdown-item-title">Prevention</div>
                                        <div class="dropdown-item-desc">Explore preventive health guidance.</div>
                                    </div>
                                </a>
                            </li>
                        </ul>
                    </li>
                </ul>

                <!-- Right Actions -->
                <div class="d-flex align-items-center gap-2 pt-2 pt-xl-0 border-top border-xl-0 border-secondary border-opacity-25 mt-2 mt-xl-0">
                    <!-- Theme Toggle Button -->
                    <button id="themeToggleBtn" type="button" class="btn btn-sm rounded-pill px-3 py-1 theme-toggle-btn d-inline-flex align-items-center gap-1" onclick="toggleSiteTheme()" title="Toggle Dark/Light Mode" aria-label="Toggle dark/light theme">
                        <i class="bi bi-moon-stars-fill theme-icon-dark text-warning"></i>
                        <i class="bi bi-sun-fill theme-icon-light text-warning d-none"></i>
                        <span class="theme-text small fw-semibold">Dark</span>
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
                        <a class="nav-link px-2 <?= $current_page == 'dashboard.php' ? 'active text-info fw-bold' : '' ?>" href="dashboard.php">Dashboard</a>
                        <a class="btn btn-outline-danger btn-sm rounded-pill px-3 py-1 fw-semibold d-inline-flex align-items-center" href="logout.php">
                            <i class="bi bi-box-arrow-right me-1"></i> Logout (<?= sanitize($user['name']) ?>)
                        </a>
                    <?php else: ?>
                        <a class="btn btn-outline-info rounded-pill px-3 py-1 btn-sm fw-semibold" href="login.php">Login</a>
                        <a class="btn btn-info rounded-pill px-3 py-1 btn-sm text-white fw-semibold" href="register.php">Register</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="py-4">
        <div class="container">
            <?php display_flash_message(); ?>
