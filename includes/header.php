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

    <!-- Navigation Header -->
    <nav class="navbar navbar-expand-xl navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center me-3" href="index.php">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4 fw-bold">AI Healthcare<span class="text-info">.</span></span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarMain">
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-xl-center gap-1 small fw-medium">
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'index.php' ? 'active text-info fw-bold' : '' ?>" href="index.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'about.php' ? 'active text-info fw-bold' : '' ?>" href="about.php">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'prediction.php' ? 'active text-info fw-bold' : '' ?>" href="prediction.php">AI Prediction</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'image_scanner.php' ? 'active text-info fw-bold' : '' ?>" href="image_scanner.php">
                            <i class="bi bi-camera me-1"></i>Injury Scanner
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'assessment.php' ? 'active text-info fw-bold' : '' ?>" href="assessment.php">Clinical Risk</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'simulator.php' ? 'active text-info fw-bold' : '' ?>" href="simulator.php">Simulator</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'diseases.php' || $current_page == 'disease_detail.php' ? 'active text-info fw-bold' : '' ?>" href="diseases.php">Diseases Library</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'symptoms_guide.php' ? 'active text-info fw-bold' : '' ?>" href="symptoms_guide.php">Symptoms Guide</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'prevention.php' ? 'active text-info fw-bold' : '' ?>" href="prevention.php">Prevention</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'dataset_info.php' ? 'active text-info fw-bold' : '' ?>" href="dataset_info.php">Dataset & AI</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'contact.php' ? 'active text-info fw-bold' : '' ?>" href="contact.php">Contact</a>
                    </li>

                    <!-- Theme Toggle Button -->
                    <li class="nav-item ms-xl-2 my-1 my-xl-0">
                        <button id="themeToggleBtn" type="button" class="btn btn-sm rounded-pill px-3 py-1 theme-toggle-btn d-inline-flex align-items-center gap-1" title="Toggle Dark/Light Mode" aria-label="Toggle dark/light theme">
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
                    </li>

                    <?php if (is_logged_in()): ?>
                        <li class="nav-item ms-xl-1">
                            <a class="nav-link <?= $current_page == 'dashboard.php' ? 'active text-info fw-bold' : '' ?>" href="dashboard.php">Dashboard</a>
                        </li>
                        <li class="nav-item ms-xl-1">
                            <a class="btn btn-outline-danger btn-sm rounded-pill px-3 py-1 fw-semibold d-inline-flex align-items-center" href="logout.php">
                                <i class="bi bi-box-arrow-right me-1"></i> Logout (<?= sanitize($user['name']) ?>)
                            </a>
                        </li>
                    <?php else: ?>
                        <li class="nav-item ms-xl-2">
                            <a class="btn btn-outline-info rounded-pill px-3 btn-sm" href="login.php">Login</a>
                        </li>
                        <li class="nav-item ms-xl-1">
                            <a class="btn btn-info rounded-pill px-3 btn-sm" href="register.php">Register</a>
                        </li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="py-4">
        <div class="container">
            <?php display_flash_message(); ?>
