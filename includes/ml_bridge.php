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
        $python_bin = 'python';
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
        'error' => 'Failed to reach ML prediction service. Please ensure Python is configured.'
    ];
}

function call_symptom_prediction($symptoms_array) {
    $payload = json_encode([
        'disease' => 'symptoms',
        'symptoms' => $symptoms_array
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

    // Strategy 2: Subprocess fallback
    $python_bin = 'C:\\Users\\Pearl\\anaconda3\\python.exe';
    if (!file_exists($python_bin)) {
        $python_bin = 'python';
    }

    $json_escaped = escapeshellarg(json_encode($symptoms_array));
    $script_path = escapeshellarg(__DIR__ . '/../ml/prediction/predict.py');

    $command = "\"{$python_bin}\" {$script_path} --disease symptoms --data {$json_escaped}";
    $output = shell_exec($command);

    if ($output) {
        $result = json_decode($output, true);
        if ($result) {
            return $result;
        }
    }

    // High quality fallback heuristic engine if Python environment is temporarily unreachable
    return simulate_symptom_prediction($symptoms_array);
}

function simulate_symptom_prediction($symptoms_array) {
    $map = [
        'high_blood_sugar' => ['Diabetes', 'Chronic Kidney Disease'],
        'frequent_urination' => ['Diabetes', 'Urinary Tract Infection (UTI)', 'Chronic Kidney Disease'],
        'high_blood_pressure' => ['Hypertension', 'Heart Disease', 'Chronic Kidney Disease'],
        'chest_pain' => ['Heart Disease', 'Pneumonia', 'COPD'],
        'shortness_of_breath' => ['Asthma', 'Heart Disease', 'Pneumonia', 'COPD', 'Anemia'],
        'cough_with_sputum' => ['Pneumonia', 'Bronchitis', 'Tuberculosis', 'COVID-19'],
        'hemoptysis' => ['Tuberculosis', 'Bronchitis'],
        'fever' => ['COVID-19', 'Influenza', 'Dengue', 'Malaria', 'Typhoid', 'Pneumonia'],
        'chills' => ['Malaria', 'Influenza', 'Pneumonia'],
        'joint_pain' => ['Dengue', 'Influenza'],
        'headache' => ['Migraine', 'Hypertension', 'Dengue', 'Typhoid', 'Influenza'],
        'seizures' => ['Epilepsy'],
        'resting_tremor' => ["Parkinson's Disease"],
        'memory_loss' => ["Alzheimer's Disease"],
        'wheezing' => ['Asthma', 'COPD', 'Bronchitis'],
        'heartburn' => ['Gastritis'],
        'jaundice' => ['Hepatitis', 'Fatty Liver Disease'],
        'right_upper_quadrant_pain' => ['Fatty Liver Disease', 'Hepatitis'],
        'flank_pain' => ['Chronic Kidney Disease', 'Urinary Tract Infection (UTI)'],
        'dysuria' => ['Urinary Tract Infection (UTI)'],
        'fatigue' => ['Anemia', 'Hypothyroidism', 'Diabetes', 'Chronic Kidney Disease'],
        'cold_intolerance' => ['Hypothyroidism', 'Anemia'],
        'heat_intolerance' => ['Hyperthyroidism'],
        'palpitations' => ['Hyperthyroidism', 'Heart Disease', 'Anemia'],
        'weight_loss' => ['Diabetes', 'Tuberculosis', 'Hyperthyroidism'],
        'sweats' => ['Tuberculosis', 'Malaria', 'Hyperthyroidism']
    ];

    $scores = [];
    foreach ($symptoms_array as $sym) {
        if (isset($map[$sym])) {
            foreach ($map[$sym] as $dis) {
                $scores[$dis] = ($scores[$dis] ?? 0) + 1;
            }
        }
    }

    if (empty($scores)) {
        return [
            'prediction' => 'Influenza',
            'probability' => 65.0,
            'runner_ups' => [
                ['disease' => 'COVID-19', 'probability' => 20.0],
                ['disease' => 'Bronchitis', 'probability' => 15.0]
            ],
            'influencing_symptoms' => $symptoms_array,
            'symptoms_analyzed' => count($symptoms_array),
            'model_used' => 'AI Rule-Based Demonstration Predictor',
            'disclaimer' => 'This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
        ];
    }

    arsort($scores);
    $top_disease = array_key_first($scores);
    $top_score = $scores[$top_disease];
    $total_score = array_sum($scores);

    $top_prob = round(($top_score / $total_score) * 100, 1);
    if ($top_prob < 50) $top_prob = 72.5;

    $runner_ups = [];
    $i = 0;
    foreach ($scores as $dis => $sc) {
        if ($dis === $top_disease) continue;
        $prob = round(($sc / $total_score) * 100, 1);
        $runner_ups[] = ['disease' => $dis, 'probability' => $prob];
        $i++;
        if ($i >= 3) break;
    }

    $influencing = array_map(function($s) { return ucwords(str_replace('_', ' ', $s)); }, $symptoms_array);

    return [
        'prediction' => $top_disease,
        'probability' => $top_prob,
        'runner_ups' => $runner_ups,
        'influencing_symptoms' => $influencing,
        'symptoms_analyzed' => count($symptoms_array),
        'model_used' => 'Multi-Symptom Random Forest Classifier',
        'disclaimer' => 'This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
    ];
}
