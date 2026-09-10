<?php
require_once __DIR__ . '/../includes/ml_bridge.php';

echo "Testing PHP ML Bridge...\n";

// Test 1: Insufficient symptoms
$res1 = call_symptom_prediction(['fever']);
echo "Test 1 (Single symptom):\n";
echo "Prediction: " . ($res1['prediction'] ?? 'N/A') . " | Status: " . ($res1['status'] ?? 'N/A') . "\n\n";

// Test 2: Asthma presentation
$res2 = call_symptom_prediction(['shortness_of_breath', 'wheezing', 'cough_with_sputum']);
echo "Test 2 (Asthma symptoms):\n";
echo "Prediction: " . ($res2['prediction'] ?? 'N/A') . " (" . ($res2['probability'] ?? 0) . "%) | Status: " . ($res2['status'] ?? 'N/A') . "\n";
if (!empty($res2['runner_ups'])) {
    echo "Runner-ups: ";
    foreach ($res2['runner_ups'] as $r) {
        echo $r['disease'] . " (" . $r['probability'] . "%) ";
    }
    echo "\n";
}
echo "Model Used: " . ($res2['model_used'] ?? 'N/A') . "\n\n";

// Test 3: Common Cold
$res3 = call_symptom_prediction(['runny_nose', 'sneezing', 'sore_throat', 'dry_cough']);
echo "Test 3 (Common Cold symptoms):\n";
echo "Prediction: " . ($res3['prediction'] ?? 'N/A') . " (" . ($res3['probability'] ?? 0) . "%) | Status: " . ($res3['status'] ?? 'N/A') . "\n\n";

echo "PHP ML Bridge Tests Completed Successfully!\n";
