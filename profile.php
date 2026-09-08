<?php
// profile.php
require_once __DIR__ . '/includes/auth.php';

require_login();

$user = get_logged_in_user();
$user_id = $user['id'];
$errors = [];
$success_msg = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = sanitize($_POST['name'] ?? '');
    
    if (empty($name)) {
        $errors[] = "Name cannot be empty.";
    } else {
        $db = Database::getInstance();
        $stmt = $db->prepare("UPDATE users SET name = ? WHERE id = ?");
        if ($stmt->execute([$name, $user_id])) {
            $success_msg = "Profile updated successfully!";
            $user['name'] = $name;
        } else {
            $errors[] = "Failed to update profile.";
        }
    }
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-6">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="text-center mb-4">
                <i class="bi bi-person-circle fs-1 text-info"></i>
                <h3 class="fw-bold mt-2">User Profile</h3>
                <p class="text-muted small">Manage your account credentials</p>
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

            <?php if ($success_msg): ?>
                <div class="alert alert-success shadow-sm"><?= sanitize($success_msg) ?></div>
            <?php endif; ?>

            <form action="profile.php" method="POST">
                <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" name="name" class="form-control" value="<?= sanitize($user['name']) ?>" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">Email Address (Read-Only)</label>
                    <input type="email" class="form-control bg-light" value="<?= sanitize($user['email']) ?>" readonly>
                </div>

                <div class="mb-4">
                    <label class="form-label">Member Since</label>
                    <input type="text" class="form-control bg-light" value="<?= date('F d, Y', strtotime($user['created_at'])) ?>" readonly>
                </div>

                <button type="submit" class="btn btn-primary-custom w-100 py-2">
                    <i class="bi bi-save me-1"></i> Save Changes
                </button>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
