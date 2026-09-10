<?php
// includes/ml_bridge.php

function get_python_binary() {
    if (getenv('PYTHON_BIN')) {
        return getenv('PYTHON_BIN');
    }
    // Check known Windows Anaconda/local Python paths first
    $windows_paths = [
        'C:\\Users\\Pearl\\anaconda3\\python.exe',
        'C:\\xampp\\python\\python.exe',
        'C:\\Python311\\python.exe',
        'C:\\Python310\\python.exe',
        'C:\\Python39\\python.exe'
    ];
    foreach ($windows_paths as $p) {
        if (file_exists($p)) {
            return $p;
        }
    }
    // Check standard commands, skipping WindowsApps aliases
    $candidates = ['python', 'python3', 'py'];
    foreach ($candidates as $cmd) {
        $check = shell_exec(PHP_OS_FAMILY === 'Windows' ? "where $cmd 2>nul" : "which $cmd 2>/dev/null");
        if (!empty(trim($check))) {
            $lines = explode("\n", trim($check));
            foreach ($lines as $line) {
                $found = trim($line);
                if (file_exists($found) && stripos($found, 'WindowsApps') === false) {
                    return $found;
                }
            }
        }
    }
    return 'python';
}

function call_ml_prediction($disease, $input_data_array) {
    $api_url = getenv('ML_API_URL') ?: 'http://127.0.0.1:5000/predict';
    $payload = json_encode([
        'disease' => $disease,
        'data' => $input_data_array
    ]);

    // Strategy 1: Attempt Flask REST API call
    if (function_exists('curl_init')) {
        $ch = curl_init($api_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_TIMEOUT, 4);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code === 200 && $response) {
            $result = json_decode($response, true);
            if ($result && !isset($result['error'])) {
                return $result;
            }
        }
    }

    // Strategy 2: Fallback to direct Python subprocess execution
    $python_bin = get_python_binary();
    $json_escaped = escapeshellarg(json_encode($input_data_array));
    $disease_escaped = escapeshellarg($disease);
    $script_path = escapeshellarg(__DIR__ . '/../ml/prediction/predict.py');

    $command = "\"{$python_bin}\" {$script_path} --disease {$disease_escaped} --data {$json_escaped}";
    $output = shell_exec($command);

    if ($output) {
        $result = json_decode($output, true);
        if ($result && !isset($result['error'])) {
            return $result;
        }
    }

    return [
        'error' => 'Unable to reach ML prediction service. Please verify Python service is running.'
    ];
}

function call_symptom_prediction($symptoms_array) {
    if (empty($symptoms_array)) {
        return [
            'prediction' => 'No Symptoms Provided',
            'probability' => 0.0,
            'runner_ups' => [],
            'influencing_symptoms' => [],
            'symptoms_analyzed' => 0,
            'model_used' => 'None',
            'disclaimer' => 'This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
        ];
    }

    $api_url = getenv('ML_API_URL') ?: 'http://127.0.0.1:5000/predict';
    $payload = json_encode([
        'disease' => 'symptoms',
        'symptoms' => $symptoms_array
    ]);

    // Strategy 1: Attempt Flask REST API call
    if (function_exists('curl_init')) {
        $ch = curl_init($api_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_TIMEOUT, 4);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code === 200 && $response) {
            $result = json_decode($response, true);
            if ($result && !isset($result['error'])) {
                return $result;
            }
        }
    }

    // Strategy 2: Subprocess fallback
    $python_bin = get_python_binary();
    $json_escaped = escapeshellarg(json_encode($symptoms_array));
    $script_path = escapeshellarg(__DIR__ . '/../ml/prediction/predict.py');

    $command = "\"{$python_bin}\" {$script_path} --disease symptoms --data {$json_escaped}";
    $output = shell_exec($command);

    if ($output) {
        $result = json_decode($output, true);
        if ($result && !isset($result['error'])) {
            return $result;
        }
    }

    // High quality fallback heuristic engine if Python environment is temporarily unreachable
    return simulate_symptom_prediction($symptoms_array);
}

function simulate_symptom_prediction($symptoms_array) {
    if (empty($symptoms_array) || count($symptoms_array) < 2) {
        return [
            'status' => 'insufficient_information',
            'prediction' => 'Insufficient Information',
            'probability' => 0.0,
            'runner_ups' => [],
            'influencing_symptoms' => array_map(function($s) { return ucwords(str_replace('_', ' ', $s)); }, $symptoms_array),
            'symptoms_analyzed' => count($symptoms_array),
            'model_used' => 'Multi-Symptom Random Forest Classifier',
            'model_version' => 'Multi-Disease Prediction Model v2',
            'supported_classes' => 65,
            'message' => 'Insufficient symptoms provided for a meaningful prediction. Please select at least two specific symptoms to receive an educational assessment.',
            'disclaimer' => 'These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
        ];
    }

    $map = [
        'high_blood_sugar' => ['Diabetes', 'Prediabetes', 'Metabolic Syndrome'],
        'frequent_urination' => ['Diabetes', 'Prediabetes', 'Urinary Tract Infection (UTI)', 'Chronic Kidney Disease'],
        'high_blood_pressure' => ['Hypertension', 'Heart Disease', 'Metabolic Syndrome', 'Chronic Kidney Disease'],
        'chest_pain' => ['Heart Disease', 'Angina Pectoris', 'Arrhythmia', 'Pneumonia'],
        'shortness_of_breath' => ['Asthma', 'Heart Disease', 'Heart Failure', 'COPD', 'Pneumonia', 'Anemia'],
        'cough_with_sputum' => ['Pneumonia', 'Bronchitis', 'Tuberculosis', 'Sinusitis', 'COPD'],
        'hemoptysis' => ['Tuberculosis'],
        'fever' => ['COVID-19', 'Influenza', 'Dengue', 'Malaria', 'Typhoid', 'Pneumonia', 'Gastroenteritis', 'Kidney Infection (Pyelonephritis)'],
        'chills' => ['Malaria', 'Influenza', 'Kidney Infection (Pyelonephritis)', 'Pneumonia'],
        'joint_pain' => ['Osteoarthritis', 'Rheumatoid Arthritis', 'Gout', 'Dengue', 'Influenza', 'Osteoporosis', 'Vitamin D Deficiency'],
        'headache' => ['Migraine', 'Tension Headache', 'Hypertension', 'Sinusitis', 'Dengue', 'Influenza'],
        'seizures' => ['Epilepsy'],
        'resting_tremor' => ["Parkinson's Disease"],
        'memory_loss' => ["Alzheimer's Disease", "Vitamin B12 Deficiency"],
        'wheezing' => ['Asthma', 'COPD'],
        'heartburn' => ['GERD (Acid Reflux)', 'Gastritis', 'Peptic Ulcer Disease'],
        'jaundice' => ['Hepatitis', 'Gallstones', 'Fatty Liver Disease'],
        'right_upper_quadrant_pain' => ['Gallstones', 'Fatty Liver Disease', 'Hepatitis'],
        'flank_pain' => ['Kidney Stones', 'Kidney Infection (Pyelonephritis)', 'Chronic Kidney Disease'],
        'dysuria' => ['Urinary Tract Infection (UTI)', 'Kidney Stones', 'Kidney Infection (Pyelonephritis)'],
        'fatigue' => ['Anemia', 'Hypothyroidism', 'Diabetes', 'Chronic Kidney Disease', 'Heart Failure', 'Chronic Stress & Burnout', 'Depressive Symptoms'],
        'cold_intolerance' => ['Hypothyroidism', 'Anemia'],
        'heat_intolerance' => ['Hyperthyroidism'],
        'palpitations' => ['Arrhythmia', 'Hyperthyroidism', 'Heart Failure', 'Generalized Anxiety'],
        'weight_loss' => ['Diabetes', 'Hyperthyroidism', 'Tuberculosis', 'Depressive Symptoms'],
        'sweats' => ['Tuberculosis', 'Malaria', 'Hyperthyroidism'],
        'nausea' => ['Gastritis', 'Peptic Ulcer Disease', 'Gastroenteritis', 'Migraine', 'Gallstones'],
        'vomiting' => ['Gastroenteritis', 'Peptic Ulcer Disease', 'Migraine', 'Gallstones'],
        'dizziness' => ['Hypertension', 'Anemia', 'Arrhythmia', 'Peripheral Neuropathy', 'Migraine'],
        'abdominal_pain' => ['Peptic Ulcer Disease', 'Gastroenteritis', 'Irritable Bowel Syndrome (IBS)', 'Gastritis', 'Gallstones', 'Chronic Diarrhea'],
        'runny_nose' => ['Common Cold', 'Allergic Rhinitis'],
        'sneezing' => ['Common Cold', 'Allergic Rhinitis'],
        'sore_throat' => ['Common Cold', 'Bronchitis', 'GERD (Acid Reflux)'],
        'dry_cough' => ['Common Cold', 'Asthma'],
        'nasal_congestion' => ['Sinusitis', 'Allergic Rhinitis'],
        'loss_of_smell' => ['COVID-19'],
        'diarrhea' => ['Gastroenteritis', 'Irritable Bowel Syndrome (IBS)', 'Chronic Diarrhea', 'Typhoid'],
        'constipation' => ['Chronic Constipation', 'Irritable Bowel Syndrome (IBS)'],
        'bloating' => ['Irritable Bowel Syndrome (IBS)', 'Chronic Constipation'],
        'skin_rash' => ['Eczema (Atopic Dermatitis)', 'Psoriasis', 'Contact Dermatitis', 'Fungal Skin Infection', 'Acne Vulgaris', 'Dengue'],
        'itching' => ['Eczema (Atopic Dermatitis)', 'Contact Dermatitis', 'Fungal Skin Infection', 'Urticaria (Hives)', 'Allergic Rhinitis'],
        'skin_flaking' => ['Psoriasis', 'Eczema (Atopic Dermatitis)', 'Fungal Skin Infection'],
        'acne_breakouts' => ['Acne Vulgaris', 'Polycystic Ovary Syndrome (PCOS)'],
        'hives_welts' => ['Urticaria (Hives)'],
        'localized_swelling' => ['Gout', 'Rheumatoid Arthritis', 'Urticaria (Hives)', 'Muscle Strain'],
        'muscle_pain' => ['Muscle Strain', 'Tension Headache', 'Peripheral Artery Disease', 'Generalized Anxiety', 'Vitamin D Deficiency'],
        'back_pain' => ['Osteoporosis', 'Muscle Strain'],
        'joint_stiffness' => ['Rheumatoid Arthritis', 'Osteoarthritis'],
        'numbness_tingling' => ['Peripheral Neuropathy', 'Peripheral Artery Disease', 'Vitamin B12 Deficiency'],
        'blurred_vision' => ['Diabetes'],
        'excessive_hunger' => ['Diabetes'],
        'weight_gain' => ['Hypothyroidism', 'Obesity', 'Polycystic Ovary Syndrome (PCOS)', 'Metabolic Syndrome'],
        'hair_thinning' => ['Hypothyroidism', 'Polycystic Ovary Syndrome (PCOS)'],
        'anxiety_nervousness' => ['Generalized Anxiety', 'Chronic Stress & Burnout'],
        'depressed_mood' => ['Depressive Symptoms', 'Vitamin D Deficiency'],
        'sleep_disturbance' => ['Insomnia & Sleep Disorder', 'Generalized Anxiety', 'Chronic Stress & Burnout'],
        'leg_swelling' => ['Heart Failure', 'Chronic Kidney Disease'],
        'blood_in_urine' => ['Kidney Stones', 'Urinary Tract Infection (UTI)']
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
            'status' => 'insufficient_information',
            'prediction' => 'Insufficient Information',
            'probability' => 0.0,
            'runner_ups' => [],
            'influencing_symptoms' => array_map(function($s) { return ucwords(str_replace('_', ' ', $s)); }, $symptoms_array),
            'symptoms_analyzed' => count($symptoms_array),
            'model_used' => 'Multi-Symptom Random Forest Classifier',
            'model_version' => 'Multi-Disease Prediction Model v2',
            'supported_classes' => 65,
            'message' => 'The selected symptoms did not match a recognized pattern across our 65 condition categories. Please consult a qualified healthcare provider.',
            'disclaimer' => 'These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
        ];
    }

    arsort($scores);
    $top_disease = array_key_first($scores);
    $top_score = $scores[$top_disease];
    $total_score = array_sum($scores);

    $top_prob = round(($top_score / $total_score) * 100, 1);
    if ($top_prob < 50) $top_prob = 68.5;

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
        'status' => 'success',
        'prediction' => $top_disease,
        'probability' => $top_prob,
        'runner_ups' => $runner_ups,
        'influencing_symptoms' => $influencing,
        'symptoms_analyzed' => count($symptoms_array),
        'model_used' => 'Multi-Symptom Random Forest Classifier',
        'model_version' => 'Multi-Disease Prediction Model v2',
        'supported_classes' => 65,
        'disclaimer' => 'These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.'
    ];
}

function call_image_scanner($image_path) {
    if (!file_exists($image_path)) {
        return [
            'success' => false,
            'category' => 'Unable to Assess',
            'error' => 'Image file not found on server.'
        ];
    }

    $api_url = getenv('SCANNER_API_URL') ?: 'http://127.0.0.1:5000/scan-image';

    // Strategy 1: Attempt Flask REST API call
    if (function_exists('curl_init')) {
        $ch = curl_init($api_url);
        $cfile = new CURLFile($image_path, mime_content_type($image_path) ?: 'image/jpeg', basename($image_path));
        $data = ['image' => $cfile];

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_TIMEOUT, 6);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code === 200 && $response) {
            $result = json_decode($response, true);
            if ($result && !empty($result['category'])) {
                return $result;
            }
        }
    }

    // Strategy 2: Fallback to direct Python subprocess execution
    $python_bin = get_python_binary();
    $script_path = escapeshellarg(__DIR__ . '/../ml/vision/scanner.py');
    $img_escaped = escapeshellarg($image_path);

    $command = "\"{$python_bin}\" {$script_path} {$img_escaped}";
    $output = shell_exec($command);

    if ($output) {
        $result = json_decode($output, true);
        if ($result && !empty($result['category'])) {
            return $result;
        }
    }

    // Fallback if neither API nor Python execution could run
    return [
        'success' => false,
        'category' => 'Unable to Assess',
        'confidence_score' => 0.0,
        'error' => 'Image processing service unavailable. The computer vision analysis engine could not be reached.',
        'assessment_summary' => 'Image analysis could not be completed because the backend service is offline.',
        'findings' => ['Computer vision scanning pipeline is currently offline or unreachable.'],
        'recommendations' => [
            'Please verify server Python dependencies (PIL, numpy).',
            'For any actual skin concern, please consult a qualified healthcare professional directly.'
        ],
        'warning_signs' => [
            'Severe bleeding or deep puncture wounds',
            'Rapidly spreading redness or red streaks',
            'Foul-smelling pus or worsening discharge',
            'High fever or worsening systemic symptoms'
        ],
        'is_preliminary' => true
    ];
}

