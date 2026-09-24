<?php
/**
 * api/record_prediction.php
 * Records symptom prediction history in MySQL if user is authenticated.
 */
header('Content-Type: application/json');
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/auth.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    $input = $_POST;
}

$symptoms = $input['symptoms'] ?? [];
$top_condition = $input['top_condition'] ?? $input['predicted_disease'] ?? '';
$score = floatval($input['score'] ?? $input['confidence'] ?? 0);

if (empty($symptoms) || empty($top_condition)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing symptoms or condition']);
    exit;
}

$pdo = get_db_connection();
if ($pdo && is_logged_in()) {
    try {
        $user = get_logged_in_user();
        $sym_str = is_array($symptoms) ? implode(', ', $symptoms) : strval($symptoms);
        $stmt = $pdo->prepare("INSERT INTO prediction_history (user_id, symptoms_selected, predicted_disease, confidence) VALUES (?, ?, ?, ?)");
        $stmt->execute([
            $user['id'],
            $sym_str,
            $top_condition,
            $score
        ]);
        echo json_encode(['success' => true, 'recorded' => true]);
        exit;
    } catch (Exception $e) {
        echo json_encode(['success' => true, 'recorded' => false, 'error' => $e->getMessage()]);
        exit;
    }
}

echo json_encode(['success' => true, 'recorded' => false, 'guest' => true]);
