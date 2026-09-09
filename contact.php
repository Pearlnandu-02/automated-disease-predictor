<?php
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';

$success = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = isset($_POST['name']) ? trim($_POST['name']) : '';
    $email = isset($_POST['email']) ? trim($_POST['email']) : '';
    $message = isset($_POST['message']) ? trim($_POST['message']) : '';

    if ($name && $email && $message) {
        $success = true;
        set_flash_message("Thank you! Your message has been submitted successfully.", "success");
    } else {
        set_flash_message("Please fill out all required fields.", "warning");
    }
}
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">GET IN TOUCH</span>
        <h1 class="display-5 fw-extrabold text-white">Contact & Support</h1>
        <p class="lead text-muted mx-auto" style="max-width: 650px;">
            Have questions regarding our AI Disease Prediction project or academic setup? Reach out to our project team.
        </p>
    </div>
</div>

<div class="row g-4 justify-content-center">
    <div class="col-lg-7">
        <div class="card-custom p-4 p-md-5">
            <h4 class="fw-bold text-white mb-4"><i class="bi bi-envelope-fill text-info me-2"></i> Send Us a Message</h4>

            <?php if ($success): ?>
                <div class="alert alert-success bg-success bg-opacity-20 text-success border-success border-opacity-25 rounded-pill px-4">
                    <i class="bi bi-check-circle-fill me-2"></i> Your message has been sent successfully. We will review your academic feedback.
                </div>
            <?php endif; ?>

            <form method="POST" action="contact.php">
                <div class="mb-3">
                    <label class="form-label text-white fw-semibold">Your Full Name</label>
                    <input type="text" name="name" class="form-control" placeholder="e.g. Alex Johnson" required>
                </div>
                <div class="mb-3">
                    <label class="form-label text-white fw-semibold">Email Address</label>
                    <input type="email" name="email" class="form-control" placeholder="name@college.edu" required>
                </div>
                <div class="mb-3">
                    <label class="form-label text-white fw-semibold">Subject / Message</label>
                    <textarea name="message" class="form-control" rows="4" placeholder="Write your inquiry or feedback here..." required></textarea>
                </div>
                <button type="submit" class="btn btn-primary-custom btn-lg w-100 rounded-pill mt-2">
                    <i class="bi bi-send-fill me-2"></i> Send Inquiry
                </button>
            </form>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card-custom p-4 mb-4">
            <h5 class="fw-bold text-white mb-3"><i class="bi bi-info-circle text-info me-2"></i> Project Details</h5>
            <ul class="list-unstyled text-muted small mb-0 lh-lg">
                <li><strong>Institution:</strong> College Academic Department</li>
                <li><strong>Domain:</strong> Healthcare Artificial Intelligence & Web Development</li>
                <li><strong>Backend:</strong> PHP 8 + MySQL + Python Scikit-Learn</li>
            </ul>
        </div>

        <div class="card-custom p-4 border-info">
            <h6 class="fw-bold text-white mb-2"><i class="bi bi-shield-lock text-info me-2"></i> Data Privacy Notice</h6>
            <p class="small text-muted mb-0">
                We respect data privacy. We do NOT store unnecessary sensitive medical identifiers or share personal health information.
            </p>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
