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
    <title>HealthRisk AI - AI Healthcare Risk Assessment</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Custom CSS -->
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

    <!-- Navigation Header -->
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="index.php">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span>HealthRisk<span class="text-info">AI</span></span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarMain">
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-lg-center gap-1">
                    <li class="nav-item">
                        <a class="nav-link <?= $current_page == 'index.php' ? 'active' : '' ?>" href="index.php">Home</a>
                    </li>
                    <?php if (is_logged_in()): ?>
                        <li class="nav-item">
                            <a class="nav-link <?= $current_page == 'dashboard.php' ? 'active' : '' ?>" href="dashboard.php">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $current_page == 'assessment.php' ? 'active' : '' ?>" href="assessment.php">New Assessment</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $current_page == 'history.php' ? 'active' : '' ?>" href="history.php">History</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link <?= $current_page == 'simulator.php' ? 'active' : '' ?>" href="simulator.php">What-If Simulator</a>
                        </li>
                        <li class="nav-item ms-lg-2">
                            <a class="btn btn-outline-danger btn-sm rounded-pill px-3 py-1 fw-semibold d-inline-flex align-items-center" href="logout.php">
                                <i class="bi bi-box-arrow-right me-1"></i> Logout (<?= sanitize($user['name']) ?>)
                            </a>
                        </li>
                    <?php else: ?>
                        <li class="nav-item ms-lg-2">
                            <a class="btn btn-outline-info rounded-pill px-4 btn-sm" href="login.php">Login</a>
                        </li>
                        <li class="nav-item ms-lg-1">
                            <a class="btn btn-info rounded-pill px-4 btn-sm text-white" href="register.php">Get Started</a>
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
