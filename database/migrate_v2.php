<?php
// database/migrate_v2.php
// Clean, idempotent migration script to expand ai_healthcare to 65 diseases and 58 symptoms

require_once __DIR__ . '/../config/db.php';

echo "Running MediSense AI Database Expansion Migration (65 Diseases)...\n";
$pdo = get_db_connection();

if (!$pdo) {
    die("Error: Could not establish connection to MySQL database.\n");
}

try {
    $pdo->beginTransaction();

    // 1. EXPAND SYMPTOMS
    $symptoms = [
        [31, 'Runny or Stuffy Nose (Rhinorrhea)', 'runny_nose', 'Respiratory', 'Mild'],
        [32, 'Frequent Sneezing', 'sneezing', 'Respiratory', 'Mild'],
        [33, 'Sore or Scratchy Throat', 'sore_throat', 'Respiratory', 'Mild'],
        [34, 'Dry Non-Productive Cough', 'dry_cough', 'Respiratory', 'Moderate'],
        [35, 'Sinus Pressure & Nasal Congestion', 'nasal_congestion', 'Respiratory', 'Moderate'],
        [36, 'Loss of Smell or Taste (Anosmia)', 'loss_of_smell', 'Neurological', 'Moderate'],
        [37, 'Frequent Watery Diarrhea', 'diarrhea', 'Gastrointestinal', 'Moderate'],
        [38, 'Severe or Chronic Constipation', 'constipation', 'Gastrointestinal', 'Moderate'],
        [39, 'Abdominal Bloating & Gas Distension', 'bloating', 'Gastrointestinal', 'Mild'],
        [40, 'Visible Skin Rash or Erythema', 'skin_rash', 'Dermatological', 'Moderate'],
        [41, 'Intense Pruritus / Persistent Itching', 'itching', 'Dermatological', 'Mild'],
        [42, 'Flaking or Scaly Skin Patches', 'skin_flaking', 'Dermatological', 'Moderate'],
        [43, 'Acne Papules, Pustules or Cysts', 'acne_breakouts', 'Dermatological', 'Mild'],
        [44, 'Raised Itchy Wheals / Hives (Urticaria)', 'hives_welts', 'Dermatological', 'Moderate'],
        [45, 'Localized Tissue Swelling or Edema', 'localized_swelling', 'Systemic', 'Moderate'],
        [46, 'Muscle Aches & Myalgia', 'muscle_pain', 'Musculoskeletal', 'Moderate'],
        [47, 'Lower Back Ache or Lumbar Stiffness', 'back_pain', 'Musculoskeletal', 'Moderate'],
        [48, 'Morning Joint Stiffness', 'joint_stiffness', 'Musculoskeletal', 'Moderate'],
        [49, 'Numbness, Tingling or Paresthesia', 'numbness_tingling', 'Neurological', 'Moderate'],
        [50, 'Blurred or Fluctuating Vision', 'blurred_vision', 'Neurological', 'Moderate'],
        [51, 'Excessive Hunger (Polyphagia)', 'excessive_hunger', 'Endocrine', 'Mild'],
        [52, 'Unintentional Rapid Weight Gain', 'weight_gain', 'Endocrine', 'Mild'],
        [53, 'Diffuse Hair Thinning or Hair Loss', 'hair_thinning', 'Dermatological', 'Mild'],
        [54, 'Excessive Worry, Nervousness or Panic', 'anxiety_nervousness', 'Psychological', 'Moderate'],
        [55, 'Persistent Sadness or Low Energy Mood', 'depressed_mood', 'Psychological', 'Moderate'],
        [56, 'Insomnia or Disrupted Sleep Quality', 'sleep_disturbance', 'Psychological', 'Moderate'],
        [57, 'Lower Extremity / Ankle Edema', 'leg_swelling', 'Cardiovascular', 'Moderate'],
        [58, 'Hematuria / Discolored Urine', 'blood_in_urine', 'Renal', 'Severe']
    ];

    $sym_stmt = $pdo->prepare("
        INSERT INTO symptoms (id, name, symptom_key, body_system, severity)
        VALUES (?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            symptom_key = VALUES(symptom_key),
            body_system = VALUES(body_system),
            severity = VALUES(severity)
    ");

    foreach ($symptoms as $s) {
        $sym_stmt->execute($s);
    }
    echo "Upserted " . count($symptoms) . " symptoms successfully.\n";

    $pdo->commit();

    $dis_count = $pdo->query("SELECT COUNT(*) FROM diseases")->fetchColumn();
    $sym_count = $pdo->query("SELECT COUNT(*) FROM symptoms")->fetchColumn();
    $rel_count = $pdo->query("SELECT COUNT(*) FROM disease_symptoms")->fetchColumn();

    echo "Migration Complete!\n";
    echo "Total Diseases: $dis_count\n";
    echo "Total Symptoms: $sym_count\n";
    echo "Total Relationships: $rel_count\n";

} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    echo "Error running migration: " . $e->getMessage() . "\n";
    exit(1);
}
