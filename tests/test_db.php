<?php
require_once __DIR__ . '/../includes/functions.php';

$pdo = get_db_connection();
if (!$pdo) {
    echo "DB Connection Failed\n";
    exit(1);
}
echo "Connected successfully to MySQL ai_healthcare DB!\n";

$tables = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
echo "Tables: " . implode(', ', $tables) . "\n";

$diseases = $pdo->query('SELECT COUNT(*) FROM diseases')->fetchColumn();
echo "Disease count: " . $diseases . "\n";

$symptoms = $pdo->query('SELECT COUNT(*) FROM symptoms')->fetchColumn();
echo "Symptom count: " . $symptoms . "\n";

$mappings = $pdo->query('SELECT COUNT(*) FROM disease_symptoms')->fetchColumn();
echo "Mappings count: " . $mappings . "\n";

$users = $pdo->query('SELECT COUNT(*) FROM users')->fetchColumn();
echo "User count: " . $users . "\n";

$history = $pdo->query('SELECT COUNT(*) FROM prediction_history')->fetchColumn();
echo "Prediction history count: " . $history . "\n";
