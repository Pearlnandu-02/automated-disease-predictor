<?php
require_once __DIR__ . '/includes/functions.php';

$success = false;
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = sanitize($_POST['name'] ?? '');
    $email = sanitize($_POST['email'] ?? '');
    $message = sanitize($_POST['message'] ?? '');

    if (empty($name) || strlen($name) > 100) {
        $error = "Please provide a valid name (up to 100 characters).";
    } elseif (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 150) {
        $error = "Please provide a valid email address.";
    } elseif (empty($message) || strlen($message) < 5 || strlen($message) > 2000) {
        $error = "Message must be between 5 and 2000 characters.";
    } else {
        $pdo = get_db_connection();
        if ($pdo) {
            try {
                $stmt = $pdo->prepare("INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)");
                $stmt->execute([$name, $email, $message]);
                $success = true;
                set_flash_message('success', "Thank you, {$name}! Your message has been received and recorded in the database. Our academic project team will review your inquiry.");
            } catch (PDOException $e) {
                error_log("Contact form error: " . $e->getMessage());
                $error = "An error occurred while saving your message. Please try again.";
            }
        } else {
            $error = "Database service is temporarily unavailable. Please try again later.";
        }
    }

    if ($error) {
        set_flash_message('warning', $error);
    }
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-white px-3 py-2 rounded-pill fw-bold mb-2">GET IN TOUCH</span>
        <h1 class="display-5 fw-extrabold mb-2">Contact & Support</h1>
        <p class="lead text-muted mx-auto" style="max-width: 650px;">
            Have questions regarding our AI Disease Prediction project or academic setup? Reach out to our project team.
        </p>
    </div>
</div>

<div class="row g-4 justify-content-center">
    <div class="col-lg-7">
        <div class="card-custom p-4 p-md-5">
            <h4 class="fw-bold mb-4"><i class="bi bi-envelope-fill text-info me-2"></i> Send Us a Message</h4>

            <?php if ($success): ?>
                <div class="alert alert-success bg-success bg-opacity-20 text-success border-success border-opacity-25 rounded-pill px-4 mb-4">
                    <i class="bi bi-check-circle-fill me-2"></i> Your message has been saved successfully to our project database.
                </div>
            <?php endif; ?>

            <form method="POST" action="contact.php">
                <div class="mb-3">
                    <label class="form-label">Your Full Name</label>
                    <input type="text" name="name" class="form-control" placeholder="e.g. Alex Johnson" maxlength="100" required value="<?= isset($_POST['name']) && !$success ? sanitize($_POST['name']) : '' ?>">
                </div>
                <div class="mb-3">
                    <label class="form-label">Email Address</label>
                    <input type="email" name="email" class="form-control" placeholder="name@college.edu" maxlength="150" required value="<?= isset($_POST['email']) && !$success ? sanitize($_POST['email']) : '' ?>">
                </div>
                <div class="mb-3">
                    <label class="form-label">Subject / Message</label>
                    <textarea name="message" class="form-control" rows="4" placeholder="Write your inquiry or feedback here (min 5 characters)..." maxlength="2000" required><?= isset($_POST['message']) && !$success ? sanitize($_POST['message']) : '' ?></textarea>
                </div>
                <button type="submit" class="btn btn-primary-custom btn-lg w-100 rounded-pill mt-2">
                    <i class="bi bi-send-fill me-2"></i> Submit Inquiry
                </button>
            </form>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card-custom p-4 mb-4">
            <h5 class="fw-bold mb-3"><i class="bi bi-info-circle text-info me-2"></i> Project Details</h5>
            <ul class="list-unstyled text-muted small mb-0 lh-lg">
                <li><strong>Project:</strong> AI Healthcare System</li>
                <li><strong>Scope:</strong> Academic College Project</li>
                <li><strong>Backend:</strong> PHP 8 + MySQL PDO + Python ML</li>
            </ul>
        </div>

        <div class="card-custom p-4 border-info">
            <h6 class="fw-bold mb-2"><i class="bi bi-shield-lock text-info me-2"></i> Data Privacy Notice</h6>
            <p class="small text-muted mb-0">
                We respect data privacy. Contact inquiries and symptom submissions are stored securely in local database tables and are never sold or shared with external advertising networks.
            </p>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
