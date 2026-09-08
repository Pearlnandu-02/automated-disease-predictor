<?php
// includes/ml_bridge.php

function call_ml_prediction($disease, $input_data_array) {
    $payload = json_encode([
        'disease' => $disease,
        'data' => $input_data_array
    ]);

    // Strategy 1: Attempt Flask REST API call
    $ch = curl_init('http://127.0.0.1:5000/predict');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code === 200 && $response) {
        $result = json_decode($response, true);
        if ($result && !isset($result['error'])) {
            return $result;
        }
    }

    // Strategy 2: Fallback to direct Python subprocess execution
    $python_bin = 'C:\\Users\\Pearl\\anaconda3\\python.exe';
    if (!file_exists($python_bin)) {
        $python_bin = 'python'; // Default system fallback
    }

    $json_escaped = escapeshellarg(json_encode($input_data_array));
    $disease_escaped = escapeshellarg($disease);
    $script_path = escapeshellarg(__DIR__ . '/../ml/prediction/predict.py');

    $command = "\"{$python_bin}\" {$script_path} --disease {$disease_escaped} --data {$json_escaped}";
    $output = shell_exec($command);

    if ($output) {
        $result = json_decode($output, true);
        if ($result) {
            return $result;
        }
    }

    return [
        'error' => 'Failed to reach ML prediction service. Please ensure Anaconda Python is installed.'
    ];
}
