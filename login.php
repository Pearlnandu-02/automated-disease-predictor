<?php
// login.php
require_once __DIR__ . '/includes/auth.php';

if (is_logged_in()) {
    redirect('dashboard.php');
}

$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = sanitize($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';

    if (empty($email) || empty($password)) {
        $errors[] = "Please enter both email and password.";
    } else {
        $db = Database::getInstance();
        $stmt = $db->prepare("SELECT id, name, password FROM users WHERE email = ?");
        $stmt->execute([$email]);
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
            set_flash_message('success', 'Welcome back, ' . sanitize($user['name']) . '!');
            redirect('dashboard.php');
        } else {
            $errors[] = "Invalid email address or password.";
        }
    }
}

$page_title = 'MediSense AI | Login';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-5">
    <div class="col-md-6 col-lg-4">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="text-center mb-4">
                <i class="bi bi-shield-lock-fill fs-1 text-info"></i>
                <h3 class="fw-bold mt-2">Member Login</h3>
                <p class="text-muted small">Sign in to manage your MediSense AI health risk assessments</p>
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

            <form action="login.php" method="POST">
                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required value="<?= sanitize($_POST['email'] ?? '') ?>" placeholder="name@example.com">
                </div>

                <div class="mb-4">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required placeholder="Enter password">
                </div>

                <button type="submit" class="btn btn-primary-custom w-100 py-2 mb-3">
                    <i class="bi bi-box-arrow-in-right me-1"></i> Log In
                </button>
            </form>

            <div class="text-center mt-3">
                <span class="text-muted small">Don't have an account?</span>
                <a href="register.php" class="text-info fw-bold text-decoration-none ms-1">Register now</a>
            </div>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
