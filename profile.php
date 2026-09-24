<?php
// profile.php - Personal Health Profile (Section 6)
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$user = get_logged_in_user();
$is_guest = empty($user);
$user_id = $is_guest ? 0 : $user['id'];
$pdo = get_db_connection();

$success_msg = "";
$errors = [];

// Initialize profile defaults
$profile = [
    'name' => $is_guest ? 'Guest Health Explorer' : ($user['name'] ?? ''),
    'email' => $is_guest ? 'guest@medisense.local' : ($user['email'] ?? ''),
    'age' => 35,
    'gender' => 'Not Specified',
    'height_cm' => 172.0,
    'weight_kg' => 68.0,
    'activity_level' => 'Moderate (3-5 days/week)',
    'smoking_status' => 'Non-Smoker',
    'sleep_hours' => 7.5,
    'health_goals' => 'Maintain healthy cardiovascular fitness and balanced metabolic energy.',
    'pre_existing_conditions' => 'None reported',
    'created_at' => $is_guest ? date('Y-m-d H:i:s') : ($user['created_at'] ?? date('Y-m-d H:i:s'))
];

// Load profile from DB if logged in
if ($pdo && !$is_guest) {
    try {
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $row = $stmt->fetch();
        if ($row) {
            foreach ($profile as $key => $val) {
                if (isset($row[$key]) && $row[$key] !== null && $row[$key] !== '') {
                    $profile[$key] = $row[$key];
                }
            }
        }
    } catch (PDOException $e) {
        // Fallback to session/default
    }
}

// Handle Form Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = sanitize($_POST['name'] ?? $profile['name']);
    $age = intval($_POST['age'] ?? $profile['age']);
    $gender = sanitize($_POST['gender'] ?? $profile['gender']);
    $height_cm = floatval($_POST['height_cm'] ?? $profile['height_cm']);
    $weight_kg = floatval($_POST['weight_kg'] ?? $profile['weight_kg']);
    $activity_level = sanitize($_POST['activity_level'] ?? $profile['activity_level']);
    $smoking_status = sanitize($_POST['smoking_status'] ?? $profile['smoking_status']);
    $sleep_hours = floatval($_POST['sleep_hours'] ?? $profile['sleep_hours']);
    $health_goals = sanitize($_POST['health_goals'] ?? $profile['health_goals']);
    $pre_existing_conditions = sanitize($_POST['pre_existing_conditions'] ?? $profile['pre_existing_conditions']);

    if (empty($name)) {
        $errors[] = "Name cannot be empty.";
    }

    if (empty($errors)) {
        $profile['name'] = $name;
        $profile['age'] = $age;
        $profile['gender'] = $gender;
        $profile['height_cm'] = $height_cm;
        $profile['weight_kg'] = $weight_kg;
        $profile['activity_level'] = $activity_level;
        $profile['smoking_status'] = $smoking_status;
        $profile['sleep_hours'] = $sleep_hours;
        $profile['health_goals'] = $health_goals;
        $profile['pre_existing_conditions'] = $pre_existing_conditions;

        if ($pdo && !$is_guest) {
            try {
                $stmt = $pdo->prepare("UPDATE users SET name = ?, age = ?, gender = ?, height_cm = ?, weight_kg = ?, activity_level = ?, smoking_status = ?, sleep_hours = ?, health_goals = ?, pre_existing_conditions = ? WHERE id = ?");
                $stmt->execute([$name, $age, $gender, $height_cm, $weight_kg, $activity_level, $smoking_status, $sleep_hours, $health_goals, $pre_existing_conditions, $user_id]);
                $success_msg = "Personal Health Profile updated successfully!";
            } catch (PDOException $e) {
                $errors[] = "Database update error: " . $e->getMessage();
            }
        } else {
            $_SESSION['guest_profile'] = $profile;
            $success_msg = "Guest Health Profile updated for this session!";
        }
    }
}

// Compute Basic Health Metrics
$height_m = max(1.0, floatval($profile['height_cm']) / 100);
$bmi = floatval($profile['weight_kg']) / ($height_m * $height_m);
$ideal_weight_min = (18.5 * $height_m * $height_m);
$ideal_weight_max = (24.9 * $height_m * $height_m);
$water_liters = floatval($profile['weight_kg']) * 0.033;
$bmr = (10 * floatval($profile['weight_kg'])) + (6.25 * floatval($profile['height_cm'])) - (5 * intval($profile['age'])) + 5;

// Profile completion percentage
$completion_points = 0;
if (!empty($profile['name'])) $completion_points += 15;
if (!empty($profile['age']) && $profile['age'] > 0) $completion_points += 15;
if (!empty($profile['height_cm']) && $profile['height_cm'] > 0) $completion_points += 15;
if (!empty($profile['weight_kg']) && $profile['weight_kg'] > 0) $completion_points += 15;
if (!empty($profile['activity_level'])) $completion_points += 15;
if (!empty($profile['smoking_status'])) $completion_points += 10;
if (!empty($profile['health_goals'])) $completion_points += 15;
$completion_pct = min(100, $completion_points);

// Fetch Recent Assessments
$recent_history = [];
if ($pdo && !$is_guest) {
    try {
        $stmt = $pdo->prepare("SELECT * FROM health_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 3");
        $stmt->execute([$user_id]);
        $recent_history = $stmt->fetchAll();
    } catch (PDOException $e) {}
}

$page_title = 'MediSense AI | Personal Health Profile';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-3">
    <div class="col-lg-11 col-xl-10">
        <!-- Hero Header -->
        <div class="card-custom p-4 p-md-5 mb-4 hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-1 mb-2 fw-bold">Personal Health Profile</span>
                    <h1 class="display-6 fw-extrabold hero-heading mb-2"><?= sanitize($profile['name']) ?></h1>
                    <p class="hero-lead mb-3">
                        Manage your baseline biometric metrics, lifestyle characteristics, and preventive health targets.
                    </p>
                    <?php if ($is_guest): ?>
                        <div class="alert alert-warning py-2 px-3 small border-0 rounded-3 mb-0 d-inline-block">
                            <i class="bi bi-info-circle me-1"></i> You are viewing in <strong>Guest Mode</strong>. <a href="register.php" class="alert-link text-decoration-underline">Register</a> or <a href="login.php" class="alert-link text-decoration-underline">Log in</a> to permanently link your data.
                        </div>
                    <?php endif; ?>
                </div>
                <div class="col-lg-4 text-center mt-3 mt-lg-0">
                    <div class="p-3 bg-card-subtle rounded-4 border border-secondary border-opacity-25">
                        <small class="text-uppercase fw-bold text-muted d-block">Profile Completion</small>
                        <h2 class="display-5 fw-extrabold text-info mb-1"><?= $completion_pct ?>%</h2>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar bg-info progress-bar-striped" style="width: <?= $completion_pct ?>%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <?php if (!empty($errors)): ?>
            <div class="alert alert-danger shadow-sm mb-4">
                <ul class="mb-0 ps-3">
                    <?php foreach ($errors as $err): ?>
                        <li><?= sanitize($err) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <?php if ($success_msg): ?>
            <div class="alert alert-success shadow-sm mb-4">
                <i class="bi bi-check-circle-fill me-2"></i> <?= sanitize($success_msg) ?>
            </div>
        <?php endif; ?>

        <!-- Basic Health Metrics Strip (Section 6) -->
        <div class="row g-3 mb-4">
            <div class="col-md-3 col-6">
                <div class="card-custom p-3 text-center h-100">
                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Calculated BMI</small>
                    <h3 class="fw-extrabold text-info mb-1"><?= number_format($bmi, 1) ?></h3>
                    <span class="badge <?= $bmi >= 18.5 && $bmi < 25 ? 'bg-success' : 'bg-warning text-dark' ?> rounded-pill small py-1 px-2">
                        <?= $bmi < 18.5 ? 'Underweight' : ($bmi < 25 ? 'Optimal Weight' : ($bmi < 30 ? 'Overweight' : 'Obese')) ?>
                    </span>
                </div>
            </div>
            <div class="col-md-3 col-6">
                <div class="card-custom p-3 text-center h-100">
                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Ideal Weight Band</small>
                    <h4 class="fw-extrabold text-success mb-1"><?= number_format($ideal_weight_min, 1) ?> - <?= number_format($ideal_weight_max, 1) ?></h4>
                    <span class="text-muted small">Kilograms (kg)</span>
                </div>
            </div>
            <div class="col-md-3 col-6">
                <div class="card-custom p-3 text-center h-100">
                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Daily Hydration Target</small>
                    <h3 class="fw-extrabold text-primary mb-1"><?= number_format($water_liters, 1) ?> L</h3>
                    <span class="text-muted small">Water per day</span>
                </div>
            </div>
            <div class="col-md-3 col-6">
                <div class="card-custom p-3 text-center h-100">
                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Estimated BMR</small>
                    <h3 class="fw-extrabold text-warning mb-1"><?= number_format($bmr) ?></h3>
                    <span class="text-muted small">kcal/day basal metabolic</span>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Left Column: Edit Form -->
            <div class="col-lg-8">
                <div class="card-custom p-4 p-md-5">
                    <h4 class="fw-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-pencil-square text-info me-2"></i> Update Profile Information
                    </h4>
                    <p class="text-muted small mb-4">
                        Please provide general health and lifestyle details. MediSense AI does <strong>not</strong> collect unnecessary sensitive information (no social security numbers or financial data).
                    </p>

                    <form method="POST" action="profile.php">
                        <!-- Section: Basic Information -->
                        <h6 class="fw-bold text-uppercase text-muted border-bottom pb-2 mb-3">1. Basic Information</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Full Name</label>
                                <input type="text" name="name" class="form-control" value="<?= sanitize($profile['name']) ?>" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Email Address (Read-Only)</label>
                                <input type="email" class="form-control bg-secondary-subtle" value="<?= sanitize($profile['email']) ?>" readonly>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Age (Years)</label>
                                <input type="number" name="age" class="form-control" min="1" max="120" value="<?= intval($profile['age']) ?>" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Biological Sex</label>
                                <select name="gender" class="form-select">
                                    <option value="Not Specified" <?= $profile['gender'] == 'Not Specified' ? 'selected' : '' ?>>Prefer not to say</option>
                                    <option value="Male" <?= $profile['gender'] == 'Male' ? 'selected' : '' ?>>Male</option>
                                    <option value="Female" <?= $profile['gender'] == 'Female' ? 'selected' : '' ?>>Female</option>
                                    <option value="Other" <?= $profile['gender'] == 'Other' ? 'selected' : '' ?>>Other</option>
                                </select>
                            </div>
                        </div>

                        <!-- Section: Biometric Measurements -->
                        <h6 class="fw-bold text-uppercase text-muted border-bottom pb-2 mb-3">2. Biometric Measurements</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Height (cm)</label>
                                <input type="number" name="height_cm" step="0.5" class="form-control" value="<?= floatval($profile['height_cm']) ?>" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Weight (kg)</label>
                                <input type="number" name="weight_kg" step="0.5" class="form-control" value="<?= floatval($profile['weight_kg']) ?>" required>
                            </div>
                        </div>

                        <!-- Section: Lifestyle Information -->
                        <h6 class="fw-bold text-uppercase text-muted border-bottom pb-2 mb-3">3. Lifestyle Factors</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Physical Activity Level</label>
                                <select name="activity_level" class="form-select">
                                    <option value="Sedentary (Little or no exercise)" <?= $profile['activity_level'] == 'Sedentary (Little or no exercise)' ? 'selected' : '' ?>>Sedentary (Little or no exercise)</option>
                                    <option value="Light (1-3 days/week)" <?= $profile['activity_level'] == 'Light (1-3 days/week)' ? 'selected' : '' ?>>Light (1-3 days/week)</option>
                                    <option value="Moderate (3-5 days/week)" <?= $profile['activity_level'] == 'Moderate (3-5 days/week)' ? 'selected' : '' ?>>Moderate (3-5 days/week)</option>
                                    <option value="Very Active (6-7 days/week)" <?= $profile['activity_level'] == 'Very Active (6-7 days/week)' ? 'selected' : '' ?>>Very Active (6-7 days/week)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Smoking Status</label>
                                <select name="smoking_status" class="form-select">
                                    <option value="Non-Smoker" <?= $profile['smoking_status'] == 'Non-Smoker' ? 'selected' : '' ?>>Non-Smoker</option>
                                    <option value="Former Smoker" <?= $profile['smoking_status'] == 'Former Smoker' ? 'selected' : '' ?>>Former Smoker (> 1 year)</option>
                                    <option value="Current Smoker" <?= $profile['smoking_status'] == 'Current Smoker' ? 'selected' : '' ?>>Current Smoker</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Average Sleep Duration (Hours/Night)</label>
                                <input type="number" name="sleep_hours" step="0.5" min="3" max="14" class="form-control" value="<?= floatval($profile['sleep_hours']) ?>">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-semibold">Known Allergies / Sensitivities</label>
                                <input type="text" name="pre_existing_conditions" class="form-control" placeholder="e.g. Penicillin, Pollen, Peanuts..." value="<?= sanitize($profile['pre_existing_conditions']) ?>">
                            </div>
                            <div class="col-12">
                                <label class="form-label small fw-semibold">Personal Health Goals</label>
                                <textarea name="health_goals" class="form-control" rows="2" placeholder="e.g. Reduce resting heart rate, lower cholesterol, improve weekly sleep..."><?= sanitize($profile['health_goals']) ?></textarea>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary-custom px-5 py-2 rounded-pill">
                            <i class="bi bi-save me-1"></i> Save Profile Changes
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Column: Quick Actions & Recent Assessments -->
            <div class="col-lg-4">
                <!-- Quick Actions (Section 6) -->
                <div class="card-custom p-4 mb-4">
                    <h5 class="fw-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-lightning-charge-fill text-warning me-2"></i> Quick Actions
                    </h5>
                    <div class="d-flex flex-column gap-2">
                        <a href="risk_calculator.php" class="btn btn-outline-info rounded-pill text-start py-2 px-3 d-flex align-items-center justify-content-between">
                            <span><i class="bi bi-calculator me-2"></i> Health Risk Calculator</span>
                            <i class="bi bi-arrow-right"></i>
                        </a>
                        <a href="prediction.php" class="btn btn-outline-info rounded-pill text-start py-2 px-3 d-flex align-items-center justify-content-between">
                            <span><i class="bi bi-cpu me-2"></i> Check Symptoms</span>
                            <i class="bi bi-arrow-right"></i>
                        </a>
                        <a href="image_scanner.php" class="btn btn-outline-danger rounded-pill text-start py-2 px-3 d-flex align-items-center justify-content-between">
                            <span><i class="bi bi-camera me-2"></i> Scan Skin / Injury</span>
                            <i class="bi bi-arrow-right"></i>
                        </a>
                        <a href="history.php" class="btn btn-outline-primary rounded-pill text-start py-2 px-3 d-flex align-items-center justify-content-between">
                            <span><i class="bi bi-clock-history me-2"></i> Assessment History</span>
                            <i class="bi bi-arrow-right"></i>
                        </a>
                        <a href="report.php" class="btn btn-outline-success rounded-pill text-start py-2 px-3 d-flex align-items-center justify-content-between">
                            <span><i class="bi bi-file-earmark-medical me-2"></i> Download Health Report</span>
                            <i class="bi bi-arrow-right"></i>
                        </a>
                    </div>
                </div>

                <!-- Recent Profile Assessments -->
                <div class="card-custom p-4">
                    <h5 class="fw-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-journal-text text-info me-2"></i> Recent Assessments
                    </h5>
                    <?php if (!empty($recent_history)): ?>
                        <div class="list-group list-group-flush rounded-3 border mb-3">
                            <?php foreach ($recent_history as $rec): ?>
                                <a href="result.php?id=<?= $rec['id'] ?>" class="list-group-item list-group-item-action py-2 px-3">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <strong class="text-body small"><?= sanitize($rec['disease']) ?></strong>
                                        <span class="badge bg-secondary-subtle text-secondary small"><?= strtoupper($rec['risk_level']) ?></span>
                                    </div>
                                    <small class="text-muted"><?= date('M d, Y', strtotime($rec['created_at'])) ?> • <?= number_format($rec['probability'], 1) ?>% probability</small>
                                </a>
                            <?php endforeach; ?>
                        </div>
                    <?php else: ?>
                        <p class="small text-muted mb-3">No historical assessments recorded for this profile yet.</p>
                        <a href="assessment.php" class="btn btn-sm btn-outline-info rounded-pill w-100">Take Assessment Now</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
