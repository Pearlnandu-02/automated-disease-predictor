<?php
// register.php
require_once __DIR__ . '/includes/auth.php';

if (is_logged_in()) {
    redirect('dashboard.php');
}

$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = sanitize($_POST['name'] ?? '');
    $email = sanitize($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $confirm_password = $_POST['confirm_password'] ?? '';

    if (empty($name)) {
        $errors[] = "Full Name is required.";
    }

    if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "A valid Email Address is required.";
    }

    if (strlen($password) < 6) {
        $errors[] = "Password must be at least 6 characters long.";
    }

    if ($password !== $confirm_password) {
        $errors[] = "Passwords do not match.";
    }

    if (empty($errors)) {
        $db = Database::getInstance();
        // Check duplicate email
        $stmt = $db->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);
        if ($stmt->fetch()) {
            $errors[] = "An account with this email address already exists.";
        } else {
            $password_hash = password_hash($password, PASSWORD_DEFAULT);
            $stmt = $db->prepare("INSERT INTO users (name, email, password) VALUES (?, ?, ?)");
            if ($stmt->execute([$name, $email, $password_hash])) {
                $_SESSION['user_id'] = $db->lastInsertId();
                set_flash_message('success', 'Registration successful! Welcome to HealthRisk AI.');
                redirect('dashboard.php');
            } else {
                $errors[] = "Failed to register account. Please try again.";
            }
        }
    }
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-5">
    <div class="col-md-6 col-lg-5">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="text-center mb-4">
                <i class="bi bi-person-plus-fill fs-1 text-info"></i>
                <h3 class="fw-bold text-dark mt-2">Create Account</h3>
                <p class="text-muted small">Register to access AI healthcare risk assessment tool</p>
            </div>

            <?php if (!empty($errors)): ?>
                <div class="alert alert-danger shadow-sm">
                    <ul class="mb-0 ps-3">
                        <?php foreach ($errors as $error): ?>
                            <li><?= sanitize($error) ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            <?php endif; ?>

            <form action="register.php" method="POST" class="needs-validation" novalidate>
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" class="form-control" id="name" name="name" required value="<?= sanitize($_POST['name'] ?? '') ?>" placeholder="John Doe">
                </div>

                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required value="<?= sanitize($_POST['email'] ?? '') ?>" placeholder="name@example.com">
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required placeholder="At least 6 characters">
                </div>

                <div class="mb-4">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" required placeholder="Repeat password">
                </div>

                <button type="submit" class="btn btn-primary-custom w-100 py-2 mb-3">
                    <i class="bi bi-check-circle me-1"></i> Register Account
                </button>
            </form>

            <div class="text-center mt-3">
                <span class="text-muted small">Already have an account?</span>
                <a href="login.php" class="text-info fw-bold text-decoration-none ms-1">Login here</a>
            </div>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
