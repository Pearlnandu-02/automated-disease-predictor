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
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 3);

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
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 3);

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

require_once __DIR__ . '/../services/symptom_prediction.php';

function simulate_symptom_prediction($symptoms_array) {
    $res = SymptomPredictionService::matchSymptoms($symptoms_array);
    if (($res['status'] ?? '') === 'insufficient_information' || empty($res['conditions'])) {
        return [
            'status' => 'insufficient_information',
            'prediction' => 'Insufficient Information',
            'probability' => 0.0,
            'match_level' => 'None',
            'runner_ups' => [],
            'conditions' => [],
            'influencing_symptoms' => array_map(function($s) { return ucwords(str_replace('_', ' ', $s)); }, $symptoms_array),
            'symptoms_analyzed' => count($symptoms_array),
            'model_used' => 'Explainable Clinical Feature Co-Occurrence Engine',
            'model_version' => 'Multi-Disease Match Engine v2',
            'supported_classes' => 73,
            'message' => 'Insufficient symptoms provided for a meaningful educational analysis. Please select at least two specific symptoms to receive an educational assessment.',
            'disclaimer' => SymptomPredictionService::getDisclaimer()
        ];
    }

    $top = $res['conditions'][0];
    $runner_ups = [];
    for ($i = 1; $i < count($res['conditions']); $i++) {
        $runner_ups[] = [
            'disease' => $res['conditions'][$i]['name'],
            'probability' => (float)$res['conditions'][$i]['score'],
            'match_level' => $res['conditions'][$i]['match_level']
        ];
    }

    return [
        'status' => 'success',
        'prediction' => $top['name'],
        'probability' => (float)$top['score'],
        'match_level' => $top['match_level'],
        'conditions' => $res['conditions'],
        'runner_ups' => $runner_ups,
        'influencing_symptoms' => array_map(function($s) { return ucwords(str_replace('_', ' ', $s)); }, $top['matched_symptoms']),
        'symptoms_analyzed' => count($symptoms_array),
        'model_used' => 'Explainable Clinical Feature Co-Occurrence Engine',
        'model_version' => 'Multi-Disease Match Engine v2',
        'supported_classes' => 73,
        'emergency_signs' => $res['emergency_signs'] ?? [],
        'disclaimer' => SymptomPredictionService::getDisclaimer()
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
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 4);

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

        // Substring extract JSON object between first { and last } if leading text exists
        $start = strpos($output, '{');
        $end = strrpos($output, '}');
        if ($start !== false && $end !== false && $end > $start) {
            $json_str = substr($output, $start, $end - $start + 1);
            $result = json_decode($json_str, true);
            if ($result && !empty($result['category'])) {
                return $result;
            }
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

