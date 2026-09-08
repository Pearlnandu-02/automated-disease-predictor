<?php
// includes/auth.php
require_once __DIR__ . '/functions.php';
require_once __DIR__ . '/../config/database.php';

function is_logged_in() {
    return isset($_SESSION['user_id']) && !empty($_SESSION['user_id']);
}

function require_login() {
    if (!is_logged_in()) {
        set_flash_message('warning', 'Please log in to access this page.');
        redirect('login.php');
    }
}

function get_logged_in_user() {
    if (!is_logged_in()) {
        return null;
    }
    $db = Database::getInstance();
    $stmt = $db->prepare("SELECT id, name, email, created_at FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    return $stmt->fetch();
}
