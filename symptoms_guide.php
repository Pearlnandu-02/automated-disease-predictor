<?php
require_once __DIR__ . '/includes/functions.php';
$page_title = 'MediSense AI | Symptoms Guide';
require_once __DIR__ . '/includes/header.php';

// Comprehensive structured symptom knowledge base aligned with 58 ML features and 65 diseases
$symptom_guide_data = [
    // General / Systemic
    [
        'key' => 'fatigue',
        'name' => 'Chronic Lethargy & Fatigue',
        'category' => 'General',
        'icon' => 'bi-battery-half',
        'explanation' => 'A persistent sense of extreme physical exhaustion and lack of vital energy that does not significantly resolve with sleep or normal rest.',
        'conditions' => 'Anemia, Chronic Kidney Disease, Diabetes, Hypothyroidism, Heart Failure, Depressive Symptoms, Chronic Stress',
        'when_to_seek' => 'When accompanied by shortness of breath, unexplained fever, sudden weight loss, chest discomfort, or when it impairs everyday tasks.'
    ],
    [
        'key' => 'fever',
        'name' => 'Fever (>100.4°F / 38°C)',
        'category' => 'General',
        'icon' => 'bi-thermometer-high',
        'explanation' => 'An elevated body temperature resulting from the body\'s immune response to microbial infection, inflammation, or systemic illness.',
        'conditions' => 'Pneumonia, COVID-19, Influenza, Dengue, Malaria, Typhoid, Kidney Infection (Pyelonephritis), Gastroenteritis',
        'when_to_seek' => 'If body temperature exceeds 103°F (39.4°C), lasts more than 3 consecutive days, or is accompanied by stiff neck, mental confusion, or rash.'
    ],
    [
        'key' => 'chills',
        'name' => 'Severe Chills & Rigors',
        'category' => 'General',
        'icon' => 'bi-snow',
        'explanation' => 'Involuntary muscular shivering accompanied by a feeling of coldness, frequently signaling an acute surge in core body temperature.',
        'conditions' => 'Acute Pneumonia, Malaria, Influenza, Kidney Infection (Pyelonephritis), Systemic Sepsis',
        'when_to_seek' => 'When occurring with shaking rigors, high fever, delirium, sudden shortness of breath, or localized acute flank or back pain.'
    ],
    [
        'key' => 'weight_loss',
        'name' => 'Unexplained Rapid Weight Loss',
        'category' => 'General',
        'icon' => 'bi-graph-down-arrow',
        'explanation' => 'Losing more than 5% of body weight unintentionally over 6 to 12 months without deliberate dietary restriction or increased physical activity.',
        'conditions' => 'Type 1 & Type 2 Diabetes, Hyperthyroidism, Tuberculosis, Chronic Kidney Disease, Depressive Symptoms',
        'when_to_seek' => 'Prompt medical consultation is advised whenever weight decline is continuous, involuntary, or coupled with severe fatigue and night sweats.'
    ],
    [
        'key' => 'sweats',
        'name' => 'Drenching Night Sweats',
        'category' => 'General',
        'icon' => 'bi-droplet-half',
        'explanation' => 'Repeated episodes of extreme perspiration during nocturnal sleep that soak through bedclothes and linens despite comfortable room temperatures.',
        'conditions' => 'Tuberculosis, Malaria, Hyperthyroidism, Chronic Infections, Endocrine Imbalances',
        'when_to_seek' => 'If persisting for more than 2 weeks, or accompanied by low-grade fever, cough, enlarged lymph nodes, or unexplained weight loss.'
    ],
    [
        'key' => 'localized_swelling',
        'name' => 'Localized Tissue Swelling / Edema',
        'category' => 'General',
        'icon' => 'bi-bounding-box',
        'explanation' => 'Visible accumulation of fluid within soft tissues or joint capsules resulting in localized enlargement, tightness, and warmth.',
        'conditions' => 'Gout, Rheumatoid Arthritis, Urticaria (Hives), Muscle Strain, Contact Dermatitis',
        'when_to_seek' => 'Immediate evaluation if swelling is hot, rapidly expanding, intensely painful, or associated with high fever or difficulty breathing.'
    ],

    // Respiratory
    [
        'key' => 'shortness_of_breath',
        'name' => 'Shortness of Breath (Dyspnea)',
        'category' => 'Respiratory',
        'icon' => 'bi-wind',
        'explanation' => 'A subjective sensation of air hunger, labored breathing, or inability to take in a complete breath during mild exertion or at rest.',
        'conditions' => 'Asthma, Chronic Obstructive Pulmonary Disease (COPD), Pneumonia, Heart Failure, Angina Pectoris, Anemia',
        'when_to_seek' => 'Seek immediate emergency medical evaluation if sudden in onset, accompanied by chest tightness, blue lips/fingertips, or lightheadedness.'
    ],
    [
        'key' => 'cough_with_sputum',
        'name' => 'Persistent Productive Cough',
        'category' => 'Respiratory',
        'icon' => 'bi-lungs',
        'explanation' => 'A persistent reflex cough producing noticeable phlegm or mucus from the lower respiratory tract lasting longer than two weeks.',
        'conditions' => 'Bacterial Pneumonia, Chronic Bronchitis, Asthma Exacerbation, COPD, Sinusitis, Tuberculosis',
        'when_to_seek' => 'When mucus turns rusty or discolored with high fever, or if coughing fits cause vomiting, severe chest pain, or wheezing.'
    ],
    [
        'key' => 'dry_cough',
        'name' => 'Dry Non-Productive Cough',
        'category' => 'Respiratory',
        'icon' => 'bi-soundwave',
        'explanation' => 'A tickling, persistent throat or bronchial cough that does not produce mucus or phlegm from the airways.',
        'conditions' => 'Common Cold, Early Asthma, COVID-19, Allergic Bronchospasm, GERD-related micro-aspiration',
        'when_to_seek' => 'If cough persists beyond 3 weeks, disrupts nocturnal sleep, or is accompanied by chest discomfort or shortness of breath.'
    ],
    [
        'key' => 'wheezing',
        'name' => 'Respiratory Wheezing',
        'category' => 'Respiratory',
        'icon' => 'bi-soundwave',
        'explanation' => 'A high-pitched musical whistling sound produced by air passing through narrowed or inflamed bronchial airways during expiration.',
        'conditions' => 'Bronchial Asthma, COPD, Acute Allergic Reactions, Acute Bronchitis',
        'when_to_seek' => 'Immediate clinical attention is critical if wheezing begins acutely after allergen exposure, causes gasping, or limits speech to single words.'
    ],
    [
        'key' => 'hemoptysis',
        'name' => 'Hemoptysis (Coughing Blood)',
        'category' => 'Respiratory',
        'icon' => 'bi-exclamation-octagon',
        'explanation' => 'The expectoration of frank blood or blood-tinged sputum originating from the lungs, bronchi, or trachea.',
        'conditions' => 'Pulmonary Tuberculosis, Severe Pneumonia, Pulmonary Embolism, Bronchiectasis',
        'when_to_seek' => 'Immediate emergency evaluation is mandatory for any coughing of blood to identify the underlying vascular or infectious etiology.'
    ],
    [
        'key' => 'runny_nose',
        'name' => 'Runny Nose (Rhinorrhea)',
        'category' => 'Respiratory',
        'icon' => 'bi-droplet',
        'explanation' => 'Excessive discharge of thin or thick mucus from the nasal passages due to mucosal inflammation or hypersecretion.',
        'conditions' => 'Common Cold, Allergic Rhinitis, Seasonal Allergies, Viral Upper Respiratory Infections',
        'when_to_seek' => 'If nasal discharge turns foul-smelling, is accompanied by high fever and severe facial headache, or occurs unilaterally.'
    ],
    [
        'key' => 'sneezing',
        'name' => 'Frequent Sneezing',
        'category' => 'Respiratory',
        'icon' => 'bi-emoji-dizzy',
        'explanation' => 'Involuntary convulsive expulsion of air from the lungs through the nose and mouth triggered by nasal mucosal irritation.',
        'conditions' => 'Allergic Rhinitis, Common Cold, Environmental Dust/Pollen Sensitivity',
        'when_to_seek' => 'When occurring with wheezing, facial pain, or persistent eye inflammation.'
    ],
    [
        'key' => 'sore_throat',
        'name' => 'Sore or Scratchy Throat',
        'category' => 'Respiratory',
        'icon' => 'bi-chat-square-dots',
        'explanation' => 'Pain, scratchiness, or irritation of the pharynx that often worsens during swallowing.',
        'conditions' => 'Common Cold, Acute Bronchitis, Pharyngitis, GERD Acid Reflux, Tonsillitis',
        'when_to_seek' => 'If swallowing is severely painful, breathing is compromised, or high fever with white tonsillar exudate develops.'
    ],
    [
        'key' => 'nasal_congestion',
        'name' => 'Sinus Pressure & Nasal Congestion',
        'category' => 'Respiratory',
        'icon' => 'bi-shield-shaded',
        'explanation' => 'Blockage of nasal passages accompanied by a sensation of fullness or dull ache across the forehead, cheeks, or periorbital sinuses.',
        'conditions' => 'Acute or Chronic Sinusitis, Allergic Rhinitis, Common Cold, Deviated Septum',
        'when_to_seek' => 'When accompanied by periorbital swelling, visual changes, severe one-sided headache, or high fever.'
    ],

    // Cardiovascular
    [
        'key' => 'chest_pain',
        'name' => 'Chest Pain / Angina',
        'category' => 'Cardiovascular',
        'icon' => 'bi-heart-pulse-fill',
        'explanation' => 'A sensation of retrosternal pressure, heaviness, squeezing, or sharp discomfort across the anterior thorax.',
        'conditions' => 'Coronary Artery Disease, Angina Pectoris, Myocardial Ischemia, Arrhythmia, Pericarditis, Pneumonia',
        'when_to_seek' => 'Seek immediate 911/emergency attention for crushing chest pain radiating to jaw, neck, back, or left arm, accompanied by sweating or dyspnea.'
    ],
    [
        'key' => 'high_blood_pressure',
        'name' => 'High Blood Pressure',
        'category' => 'Cardiovascular',
        'icon' => 'bi-speedometer2',
        'explanation' => 'Sustained elevation of arterial pressure exceeding 130 mmHg systolic or 80 mmHg diastolic, increasing cardiac workload.',
        'conditions' => 'Primary Hypertension, Metabolic Syndrome, Heart Disease, Chronic Kidney Disease, Arteriosclerosis',
        'when_to_seek' => 'Seek urgent clinical evaluation if resting blood pressure exceeds 180/120 mmHg, or if paired with severe headache, chest pain, or visual blur.'
    ],
    [
        'key' => 'palpitations',
        'name' => 'Heart Palpitations & Tachycardia',
        'category' => 'Cardiovascular',
        'icon' => 'bi-activity',
        'explanation' => 'A conscious awareness of rapid, fluttering, pounding, or irregular heartbeats originating from ectopic or reentrant cardiac pacing.',
        'conditions' => 'Arrhythmia, Hyperthyroidism, Generalized Anxiety, Heart Failure, Severe Anemia',
        'when_to_seek' => 'Seek immediate emergency evaluation if palpitations occur with syncope (fainting), chest tightness, severe shortness of breath, or dizziness.'
    ],
    [
        'key' => 'leg_swelling',
        'name' => 'Lower Extremity / Ankle Edema',
        'category' => 'Cardiovascular',
        'icon' => 'bi-water',
        'explanation' => 'Pitting or dependent swelling of the feet, ankles, and lower legs caused by fluid extravasation from venous congestion.',
        'conditions' => 'Congestive Heart Failure, Chronic Kidney Disease, Venous Insufficiency, Hepatic Cirrhosis',
        'when_to_seek' => 'If swelling develops rapidly, is warm and unilateral (deep vein thrombosis risk), or is accompanied by exertional breathlessness.'
    ],

    // Gastrointestinal & Hepatic
    [
        'key' => 'heartburn',
        'name' => 'Heartburn & Acid Reflux',
        'category' => 'Digestive',
        'icon' => 'bi-fire',
        'explanation' => 'A burning retrosternal discomfort moving upward toward the throat, caused by acidic gastric contents regurgitating into the esophagus.',
        'conditions' => 'Gastroesophageal Reflux Disease (GERD), Gastritis, Peptic Ulcer Disease, Hiatal Hernia',
        'when_to_seek' => 'When accompanied by difficulty swallowing, vomiting coffee-ground material, black tarry stools, or if radiating to jaw, neck, or left arm.'
    ],
    [
        'key' => 'abdominal_pain',
        'name' => 'Abdominal Pain & Cramping',
        'category' => 'Digestive',
        'icon' => 'bi-bandaid',
        'explanation' => 'Visceral or somatic discomfort localized to any quadrant of the abdominal cavity, ranging from dull cramps to sharp focal pain.',
        'conditions' => 'Peptic Ulcer Disease, Gastroenteritis, Irritable Bowel Syndrome (IBS), Gastritis, Gallstones, Chronic Diarrhea',
        'when_to_seek' => 'Immediate emergency care is needed for sudden rigid abdomen, severe right lower quadrant pain (appendicitis), or continuous vomiting.'
    ],
    [
        'key' => 'nausea',
        'name' => 'Persistent Nausea',
        'category' => 'Digestive',
        'icon' => 'bi-emoji-neutral',
        'explanation' => 'An unpleasant, wave-like sensation of gastrointestinal distress with an involuntary inclination to vomit.',
        'conditions' => 'Gastritis, Peptic Ulcer Disease, Gastroenteritis, Migraine, Gallstones, Hepatitis, Kidney Stones',
        'when_to_seek' => 'When inability to keep fluids down causes dehydration, or if accompanied by confusion, high fever, or severe abdominal pain.'
    ],
    [
        'key' => 'vomiting',
        'name' => 'Persistent Vomiting',
        'category' => 'Digestive',
        'icon' => 'bi-exclamation-triangle',
        'explanation' => 'Forceful retrograde expulsion of gastric and intestinal contents through the mouth.',
        'conditions' => 'Acute Gastroenteritis, Peptic Ulcer Disease, Migraine, Gallstones, Food Poisoning',
        'when_to_seek' => 'If emesis contains frank blood or dark "coffee ground" material, persists beyond 24 hours, or causes profound lethargy.'
    ],
    [
        'key' => 'diarrhea',
        'name' => 'Frequent Watery Diarrhea',
        'category' => 'Digestive',
        'icon' => 'bi-water',
        'explanation' => 'The passage of loose, watery stools three or more times a day caused by impaired fluid absorption or intestinal secretory hyperdrive.',
        'conditions' => 'Acute Gastroenteritis, Irritable Bowel Syndrome (IBS), Chronic Diarrhea, Typhoid, Inflammatory Bowel Disease',
        'when_to_seek' => 'When signs of dehydration appear, stools contain visible blood or mucus, or diarrhea is accompanied by high fever (>102°F).'
    ],
    [
        'key' => 'constipation',
        'name' => 'Chronic Constipation',
        'category' => 'Digestive',
        'icon' => 'bi-slash-circle',
        'explanation' => 'Infrequent, hard, dry bowel movements occurring fewer than 3 times per week, often accompanied by straining and incomplete evacuation.',
        'conditions' => 'Chronic Constipation, Irritable Bowel Syndrome (IBS-C), Hypothyroidism, Pelvic Floor Dyssynergia',
        'when_to_seek' => 'If accompanied by severe abdominal distension, vomiting, rectal bleeding, or sudden onset after age 50.'
    ],
    [
        'key' => 'bloating',
        'name' => 'Abdominal Bloating & Distension',
        'category' => 'Digestive',
        'icon' => 'bi-circle',
        'explanation' => 'A subjective sensation of tightness, fullness, and visible distension in the abdomen caused by excessive intestinal gas accumulation.',
        'conditions' => 'Irritable Bowel Syndrome (IBS), Chronic Constipation, Small Intestinal Bacterial Overgrowth (SIBO), Celiac Disease',
        'when_to_seek' => 'If accompanied by unexplained weight loss, persistent abdominal pain, fever, or visible blood in stool.'
    ],
    [
        'key' => 'jaundice',
        'name' => 'Jaundice (Yellowing Skin / Eyes)',
        'category' => 'Digestive',
        'icon' => 'bi-eye-fill',
        'explanation' => 'Yellow pigmentation of the sclera, mucous membranes, and skin resulting from elevated unconjugated or conjugated serum bilirubin levels.',
        'conditions' => 'Viral Hepatitis, Gallstones (Biliary Obstruction), Fatty Liver Disease, Hemolytic Anemias',
        'when_to_seek' => 'Immediate medical evaluation is needed to determine the underlying hepatic or biliary etiology, especially if accompanied by dark urine or pale stool.'
    ],
    [
        'key' => 'right_upper_quadrant_pain',
        'name' => 'Right Upper Quadrant Abdominal Pain',
        'category' => 'Digestive',
        'icon' => 'bi-geo-alt-fill',
        'explanation' => 'Localized pain beneath the right lower costal rib margin, characteristic of hepatobiliary inflammation or ductal distension.',
        'conditions' => 'Gallstones (Biliary Colic), Acute Cholecystitis, Fatty Liver Disease, Acute Hepatitis',
        'when_to_seek' => 'Seek immediate emergency attention if pain is constant, severe, radiates to the right shoulder, or is accompanied by fever or jaundice.'
    ],

    // Neurological
    [
        'key' => 'headache',
        'name' => 'Severe Throbbing Headache',
        'category' => 'Neurological',
        'icon' => 'bi-lightning',
        'explanation' => 'Moderate-to-severe pulsing or band-like cephalic pain, frequently aggravated by physical exertion, sound, or bright lights.',
        'conditions' => 'Migraine, Tension Headache, Sinusitis, Severe Hypertension, Dengue, Influenza',
        'when_to_seek' => 'Seek emergency care for a sudden "thunderclap" headache, or if accompanied by high fever, stiff neck, confusion, or weakness.'
    ],
    [
        'key' => 'dizziness',
        'name' => 'Dizziness & Vertigo',
        'category' => 'Neurological',
        'icon' => 'bi-arrow-repeat',
        'explanation' => 'Lightheadedness, faintness, or a false spinning sensation (vertigo) resulting from vestibular, circulatory, or neurological disturbances.',
        'conditions' => 'Severe Anemia, Hypertension, Cardiac Arrhythmias, Migraine, Peripheral Neuropathy, Dehydration',
        'when_to_seek' => 'When accompanied by chest pain, slurred speech, acute hearing loss, double vision, or uncoordinated motor movements.'
    ],
    [
        'key' => 'seizures',
        'name' => 'Seizures & Convulsions',
        'category' => 'Neurological',
        'icon' => 'bi-broadcast',
        'explanation' => 'Sudden, unprovoked paroxysmal electrical events in the cerebral cortex producing convulsive movements or altered consciousness.',
        'conditions' => 'Epilepsy, Severe Head Trauma, Stroke, Electrolyte Derangements, CNS Infections',
        'when_to_seek' => 'Call 911 immediately if a seizure lasts longer than 5 minutes, if consecutive seizures occur, or if breathing does not resume normally.'
    ],
    [
        'key' => 'resting_tremor',
        'name' => 'Resting Hand Tremor',
        'category' => 'Neurological',
        'icon' => 'bi-hand-index-thumb',
        'explanation' => 'An involuntary, rhythmic oscillatory movement of the hands or fingers that occurs predominantly when muscles are fully supported at rest.',
        'conditions' => 'Parkinson\'s Disease, Drug-induced Parkinsonism, Essential Tremor (kinetic), Severe Anxiety',
        'when_to_seek' => 'Seek neurological evaluation when tremors progressively impair buttoning clothing, eating, handwriting, or walking balance.'
    ],
    [
        'key' => 'memory_loss',
        'name' => 'Progressive Memory Loss',
        'category' => 'Neurological',
        'icon' => 'bi-person-x',
        'explanation' => 'Gradual or noticeable deterioration in short-term recall, spatial navigation, task execution, or word-finding abilities.',
        'conditions' => 'Alzheimer\'s Disease, Vascular Dementia, Vitamin B12 Deficiency, Normal Pressure Hydrocephalus',
        'when_to_seek' => 'When memory deficits compromise self-care, bill management, driving safety, or orientation to familiar surroundings.'
    ],
    [
        'key' => 'numbness_tingling',
        'name' => 'Numbness & Paresthesia (Pins & Needles)',
        'category' => 'Neurological',
        'icon' => 'bi-fingerprint',
        'explanation' => 'Abnormal sensory sensations described as tingling, prickling, or loss of protective sensation in hands or feet.',
        'conditions' => 'Peripheral Neuropathy, Vitamin B12 Deficiency, Peripheral Artery Disease, Radiculopathy',
        'when_to_seek' => 'If numbness spreads rapidly up limbs, affects bowel/bladder control, or leads to undetected cutaneous wounds.'
    ],
    [
        'key' => 'blurred_vision',
        'name' => 'Blurred or Fluctuating Vision',
        'category' => 'Neurological',
        'icon' => 'bi-eye-slash',
        'explanation' => 'Loss of visual acuity or sharpness, making fine details difficult to distinguish at standard reading or distance ranges.',
        'conditions' => 'Diabetic Hyperglycemia (Lens Osmotic Shift), Diabetic Retinopathy, Cataracts, Glaucoma, Severe Hypertension',
        'when_to_seek' => 'Urgent ophthalmological evaluation is essential if vision loss is sudden, painful, or accompanied by flashes of light or dark floaters.'
    ],
    [
        'key' => 'loss_of_smell',
        'name' => 'Loss of Smell or Taste (Anosmia)',
        'category' => 'Neurological',
        'icon' => 'bi-flower1',
        'explanation' => 'Partial or total inability to perceive odorants or taste nuances resulting from olfactory neuroepithelial disruption.',
        'conditions' => 'COVID-19, Severe Viral Sinusitis, Allergic Nasal Polyposis, Head Trauma',
        'when_to_seek' => 'If persisting for more than 4 weeks, accompanied by unilateral nasal obstruction, or following traumatic head injury.'
    ],

    // Endocrine & Metabolic
    [
        'key' => 'high_blood_sugar',
        'name' => 'High Blood Sugar & Polydipsia',
        'category' => 'Endocrine',
        'icon' => 'bi-droplet',
        'explanation' => 'Excess glucose in circulation (Hyperglycemia), producing excessive thirst (polydipsia), dry mouth, and increased volume of urination.',
        'conditions' => 'Type 1 & Type 2 Diabetes Mellitus, Prediabetes, Metabolic Syndrome',
        'when_to_seek' => 'Urgent care is required if fruity breath odor, rapid breathing, confusion, or nausea develops (Diabetic Ketoacidosis risk).'
    ],
    [
        'key' => 'excessive_hunger',
        'name' => 'Excessive Hunger (Polyphagia)',
        'category' => 'Endocrine',
        'icon' => 'bi-cup-hot',
        'explanation' => 'An insatiable, voracious appetite and food craving despite consuming sufficient or excess caloric intake.',
        'conditions' => 'Type 1 & Type 2 Diabetes Mellitus, Hyperthyroidism, Hypoglycemia',
        'when_to_seek' => 'When paired with rapid weight loss, persistent thirst, or frequent night urination.'
    ],
    [
        'key' => 'weight_gain',
        'name' => 'Unintentional Rapid Weight Gain',
        'category' => 'Endocrine',
        'icon' => 'bi-graph-up-arrow',
        'explanation' => 'A rapid, unexplained increase in body mass occurring without a conscious increase in caloric intake or change in physical lifestyle.',
        'conditions' => 'Hypothyroidism, Clinical Obesity, Polycystic Ovary Syndrome (PCOS), Metabolic Syndrome, Heart Failure (Fluid)',
        'when_to_seek' => 'If rapid weight gain occurs over days with facial, ankle, or abdominal swelling, indicating cardiac or renal fluid retention.'
    ],
    [
        'key' => 'cold_intolerance',
        'name' => 'Cold Intolerance & Hypometabolism',
        'category' => 'Endocrine',
        'icon' => 'bi-thermometer-snow',
        'explanation' => 'An abnormal, heightened sensitivity to cold ambient temperatures caused by reduced basal metabolic heat production.',
        'conditions' => 'Hypothyroidism (Hashimoto\'s Disease), Severe Anemia, Raynaud\'s Phenomenon, Anorexia',
        'when_to_seek' => 'When joined by sluggishness, coarse dry skin, constipation, bradycardia (slow heart rate), or progressive weight gain.'
    ],
    [
        'key' => 'heat_intolerance',
        'name' => 'Heat Intolerance & Hyperhidrosis',
        'category' => 'Endocrine',
        'icon' => 'bi-thermometer-sun',
        'explanation' => 'Hypersensitivity to moderately warm environments, associated with excessive cutaneous sweating, irritability, and heat distress.',
        'conditions' => 'Hyperthyroidism (Graves\' Disease), Autonomic Dysregulation, Menopausal Transitions',
        'when_to_seek' => 'If accompanied by continuous rapid pulse, unintentional weight loss, bulging eyes (proptosis), or significant fine tremors.'
    ],

    // Renal & Urological
    [
        'key' => 'frequent_urination',
        'name' => 'Frequent Urination (Polyuria)',
        'category' => 'Urinary',
        'icon' => 'bi-droplet-half',
        'explanation' => 'The excessive, repetitive need to empty the bladder throughout the day or night, often with large urinary volumes.',
        'conditions' => 'Diabetes Mellitus, Prediabetes, Urinary Tract Infection (UTI), Chronic Kidney Disease',
        'when_to_seek' => 'If urination is paired with intense burning, cloudy hematuria, high fever, or severe lower back pain.'
    ],
    [
        'key' => 'dysuria',
        'name' => 'Painful Urination (Dysuria)',
        'category' => 'Urinary',
        'icon' => 'bi-slash-circle',
        'explanation' => 'A sharp burning, stinging, or scalding discomfort localized to the urethra during micturition.',
        'conditions' => 'Urinary Tract Infection (Cystitis), Kidney Stones, Kidney Infection (Pyelonephritis), Urethritis',
        'when_to_seek' => 'Seek immediate medical attention if accompanied by fever, chills, vomiting, or acute flank pain.'
    ],
    [
        'key' => 'flank_pain',
        'name' => 'Flank & Renal Angle Pain',
        'category' => 'Urinary',
        'icon' => 'bi-geo-alt',
        'explanation' => 'Intense aching or colicky sharp pain localized in the lateral torso between the lower ribs and iliac crest.',
        'conditions' => 'Kidney Stones (Nephrolithiasis), Acute Kidney Infection (Pyelonephritis), Chronic Kidney Disease',
        'when_to_seek' => 'Seek immediate emergency attention for excruciating spasmodic flank pain radiating to the groin, or when paired with fever and chills.'
    ],
    [
        'key' => 'blood_in_urine',
        'name' => 'Blood in Urine (Hematuria)',
        'category' => 'Urinary',
        'icon' => 'bi-exclamation-circle-fill',
        'explanation' => 'Visible pink, red, or cola-colored discoloration of urine caused by the presence of red blood cells.',
        'conditions' => 'Kidney Stones, Severe Urinary Tract Infection, Pyelonephritis, Glomerulonephritis',
        'when_to_seek' => 'Any occurrence of visible blood in the urine requires prompt clinical and diagnostic evaluation.'
    ],

    // Dermatological
    [
        'key' => 'skin_rash',
        'name' => 'Visible Skin Rash or Erythema',
        'category' => 'Dermatological',
        'icon' => 'bi-grid-fill',
        'explanation' => 'A noticeable eruption or widespread redness on the skin altering texture, color, and barrier integrity.',
        'conditions' => 'Eczema (Atopic Dermatitis), Psoriasis, Contact Dermatitis, Fungal Skin Infection, Acne Vulgaris, Dengue',
        'when_to_seek' => 'If rash is rapidly spreading, forms painful blisters, covers >10% of body, or is accompanied by high fever or mucosal lesions.'
    ],
    [
        'key' => 'itching',
        'name' => 'Intense Pruritus (Itching)',
        'category' => 'Dermatological',
        'icon' => 'bi-hand-index',
        'explanation' => 'An irritating sensation of the skin that provokes the urge to scratch, resulting from histamine or neuropeptide activation.',
        'conditions' => 'Eczema, Contact Dermatitis, Fungal Skin Infection, Urticaria (Hives), Allergic Rhinitis',
        'when_to_seek' => 'If itching prevents sleep, leads to open weeping lesions, or is accompanied by jaundice or dark urine.'
    ],
    [
        'key' => 'skin_flaking',
        'name' => 'Flaking or Scaly Skin Patches',
        'category' => 'Dermatological',
        'icon' => 'bi-layers',
        'explanation' => 'Excess shedding of dead epidermal keratinocytes producing dry, silvery, or yellowish flakes across the cutaneous surface.',
        'conditions' => 'Psoriasis, Eczema (Atopic Dermatitis), Fungal Skin Infection, Seborrheic Dermatitis',
        'when_to_seek' => 'If scales crack and bleed, cover large surface areas, or fail to respond to standard OTC emollient moisturizers.'
    ],
    [
        'key' => 'acne_breakouts',
        'name' => 'Acne Papules, Pustules or Cysts',
        'category' => 'Dermatological',
        'icon' => 'bi-circle-half',
        'explanation' => 'Inflammatory or comedonal lesions arising from follicular hyperkeratinization and sebum accumulation.',
        'conditions' => 'Acne Vulgaris, Polycystic Ovary Syndrome (PCOS), Hormonal Imbalance',
        'when_to_seek' => 'When lesions cause deep painful cysts, permanent scarring, or emotional distress.'
    ],
    [
        'key' => 'hives_welts',
        'name' => 'Raised Itchy Wheals / Hives (Urticaria)',
        'category' => 'Dermatological',
        'icon' => 'bi-chat-heart',
        'explanation' => 'Transient raised, edematous, intensely pruritic wheals with pale centers and surrounding red erythema.',
        'conditions' => 'Urticaria (Hives), Acute Allergic Drug/Food Reaction, Viral Exanthem',
        'when_to_seek' => 'Seek immediate emergency care if hives occur with lip/tongue swelling, hoarseness, difficulty swallowing, or breathlessness (anaphylaxis).'
    ],
    [
        'key' => 'hair_thinning',
        'name' => 'Diffuse Hair Thinning / Alopecia',
        'category' => 'Dermatological',
        'icon' => 'bi-scissors',
        'explanation' => 'Noticeable reduction in scalp hair density, excessive daily shedding, or patch-like loss of follicular shafts.',
        'conditions' => 'Hypothyroidism, Polycystic Ovary Syndrome (PCOS), Telogen Effluvium (Severe Stress/Illness), Iron Deficiency',
        'when_to_seek' => 'If hair loss is sudden, accompanied by scalp redness and scaling, or paired with profound fatigue and weight changes.'
    ],

    // Musculoskeletal
    [
        'key' => 'joint_pain',
        'name' => 'Severe Joint / Bone Pain',
        'category' => 'Musculoskeletal',
        'icon' => 'bi-diagram-3',
        'explanation' => 'Aching, stiffness, warmth, or swelling within articular joints that restricts range of motion or weight-bearing mobility.',
        'conditions' => 'Osteoarthritis, Rheumatoid Arthritis, Gout, Dengue, Influenza, Osteoporosis, Vitamin D Deficiency',
        'when_to_seek' => 'Immediate evaluation if a single joint becomes hot, red, and swollen with high fever, which can indicate acute septic arthritis.'
    ],
    [
        'key' => 'joint_stiffness',
        'name' => 'Morning Joint Stiffness',
        'category' => 'Musculoskeletal',
        'icon' => 'bi-hourglass-split',
        'explanation' => 'A sensation of restricted joint mobility and tightness upon waking in the morning that requires gentle movement to loosen.',
        'conditions' => 'Rheumatoid Arthritis (typically > 60 mins), Osteoarthritis (typically < 30 mins)',
        'when_to_seek' => 'When morning stiffness persists longer than 1 hour daily, affects multiple small joints in hands symmetrically, or causes swelling.'
    ],
    [
        'key' => 'muscle_pain',
        'name' => 'Muscle Aches & Myalgia',
        'category' => 'Musculoskeletal',
        'icon' => 'bi-person-arms-up',
        'explanation' => 'Diffuse or localized aching tenderness, soreness, and stiffness across major skeletal muscle groups.',
        'conditions' => 'Muscle Strain, Tension Headache, Peripheral Artery Disease (Claudication), Generalized Anxiety, Vitamin D Deficiency, Influenza',
        'when_to_seek' => 'If muscle pain follows sudden traumatic injury, is accompanied by dark tea-colored urine (rhabdomyolysis), or prevents walking.'
    ],
    [
        'key' => 'back_pain',
        'name' => 'Lower Back Ache / Lumbar Stiffness',
        'category' => 'Musculoskeletal',
        'icon' => 'bi-body-text',
        'explanation' => 'Ache, stiffness, or sharp spasm localized to the lumbosacral region of the spine, often aggravated by bending or lifting.',
        'conditions' => 'Muscle Strain, Osteoporosis (Vertebral Compression), Lumbar Disc Herniation, Spinal Spondylosis',
        'when_to_seek' => 'Seek immediate emergency care if back pain radiates down both legs with "saddle" numbness or loss of bladder/bowel control.'
    ],

    // Psychological & Well-being
    [
        'key' => 'anxiety_nervousness',
        'name' => 'Excessive Worry & Nervousness',
        'category' => 'Psychological',
        'icon' => 'bi-exclamation-triangle-fill',
        'explanation' => 'An educational screening indicator reflecting persistent, intrusive worry, autonomic hyperarousal, and difficulty relaxing.',
        'conditions' => 'Generalized Anxiety Symptoms, Chronic Stress & Burnout, Hyperthyroidism, Insomnia',
        'when_to_seek' => 'When anxiety induces severe panic attacks, chest tightness, avoidance of daily activities, or feelings of hopelessness.'
    ],
    [
        'key' => 'depressed_mood',
        'name' => 'Persistent Low Energy & Depressed Mood',
        'category' => 'Psychological',
        'icon' => 'bi-cloud-drizzle-fill',
        'explanation' => 'An educational screening indicator reflecting lasting sadness, anhedonia (loss of interest), and unrefreshing fatigue.',
        'conditions' => 'Depressive Symptoms, Vitamin D Deficiency, Chronic Stress & Burnout, Hypothyroidism',
        'when_to_seek' => 'Seek immediate clinical care or contact a crisis lifeline (call/text 988 in the US) if experiencing thoughts of self-harm or suicide.'
    ],
    [
        'key' => 'sleep_disturbance',
        'name' => 'Insomnia & Sleep Disruption',
        'category' => 'Psychological',
        'icon' => 'bi-moon-stars-fill',
        'explanation' => 'Difficulty falling asleep, frequent nocturnal awakenings, or non-restorative sleep leading to daytime impairment.',
        'conditions' => 'Insomnia & Sleep Disorder, Generalized Anxiety, Chronic Stress & Burnout, Obstructive Sleep Apnea',
        'when_to_seek' => 'When insomnia persists for greater than 3 months, impairs work/driving safety, or is accompanied by loud gasping/choking at night.'
    ]
];

$categories = ['All', 'General', 'Respiratory', 'Cardiovascular', 'Digestive', 'Neurological', 'Endocrine', 'Urinary', 'Dermatological', 'Musculoskeletal', 'Psychological'];
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">CLINICAL DIRECTORY</span>
        <h1 class="display-5 fw-extrabold mb-2">Interactive Symptoms Guide & Clinical Index (<?= count($symptom_guide_data) ?> Symptoms)</h1>
        <p class="lead text-muted mx-auto" style="max-width: 780px;">
            Explore our clinically organized index of symptoms aligned directly with our machine learning classification model across 65 conditions. Search, filter by body system, and seamlessly load symptoms into our AI diagnostic checker.
        </p>
    </div>
</div>

<!-- Search and Category Filter Toolbar -->
<div class="card-custom p-4 mb-4">
    <div class="row g-3 align-items-center">
        <div class="col-lg-5">
            <div class="input-group">
                <span class="input-group-text bg-card-subtle text-info border">
                    <i class="bi bi-search"></i>
                </span>
                <input 
                    type="text" 
                    id="symptomSearchInput" 
                    class="form-control" 
                    placeholder="Search symptoms by name, description, or condition..."
                    autocomplete="off"
                >
            </div>
        </div>
        <div class="col-lg-7">
            <div class="d-flex flex-wrap gap-2 justify-content-lg-end" id="categoryFilterContainer">
                <?php foreach ($categories as $idx => $cat): ?>
                    <button 
                        type="button" 
                        class="btn btn-sm symptom-filter-pill <?= $idx === 0 ? 'active btn-info text-white fw-bold' : 'btn-outline-secondary' ?>"
                        data-category="<?= strtolower($cat) ?>"
                    >
                        <?= sanitize($cat) ?>
                    </button>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

<!-- Symptoms Grid -->
<div class="row g-4" id="symptomsGuideGrid">
    <?php foreach ($symptom_guide_data as $s): ?>
        <div class="col-md-6 col-lg-4 symptom-guide-card" 
             data-name="<?= strtolower($s['name']) ?>" 
             data-category="<?= strtolower($s['category']) ?>" 
             data-desc="<?= strtolower($s['explanation'] . ' ' . $s['conditions']) ?>">
            <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                <div>
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle">
                            <i class="bi <?= $s['icon'] ?> fs-4"></i>
                        </div>
                        <span class="badge bg-secondary bg-opacity-25 text-info border border-info border-opacity-25">
                            <?= sanitize($s['category']) ?>
                        </span>
                    </div>

                    <h5 class="fw-bold mb-2"><?= sanitize($s['name']) ?></h5>
                    <p class="small text-muted mb-3" style="line-height: 1.6;">
                        <?= sanitize($s['explanation']) ?>
                    </p>

                    <div class="symptom-relation-box">
                        <div class="symptom-relation-title">
                            <i class="bi bi-diagram-3-fill text-info"></i> May occur with:
                        </div>
                        <?php 
                        $cond_list = array_filter(array_map('trim', explode(',', $s['conditions'] ?? '')));
                        if (!empty($cond_list)): ?>
                            <div class="symptom-relation-content d-flex flex-wrap gap-1 mt-2">
                                <?php foreach ($cond_list as $cond): ?>
                                    <span class="symptom-condition-tag"><?= sanitize($cond) ?></span>
                                <?php endforeach; ?>
                            </div>
                        <?php else: ?>
                            <div class="symptom-relation-empty">No associated conditions listed</div>
                        <?php endif; ?>
                    </div>

                    <div class="symptom-evaluation-box">
                        <div class="symptom-evaluation-title">
                            <i class="bi bi-shield-check"></i> When to Seek Evaluation:
                        </div>
                        <div class="symptom-evaluation-text"><?= sanitize($s['when_to_seek']) ?></div>
                    </div>
                </div>

                <div class="pt-3 border-top mt-2">
                    <a href="prediction.php?symptom=<?= urlencode($s['key']) ?>" class="btn btn-sm btn-outline-info rounded-pill w-100 py-2 fw-semibold">
                        <i class="bi bi-cpu-fill me-1"></i> Use this symptom in AI checker
                    </a>
                </div>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<!-- Empty Search Fallback -->
<div id="symptomsEmptySearch" class="card-custom p-5 text-center my-4" style="display: none;">
    <i class="bi bi-search text-muted display-4 mb-3"></i>
    <h4 class="fw-bold">No Matching Symptoms Found</h4>
    <p class="text-muted small mb-3">Try adjusting your search terms or select "All" from the body system filters above.</p>
    <button type="button" class="btn btn-outline-info rounded-pill px-4" onclick="document.getElementById('symptomSearchInput').value=''; document.querySelector('[data-category=all]').click();">
        Reset Search & Filters
    </button>
</div>

<div class="disclaimer-banner my-5 text-start p-4">
    <h5 class="fw-bold mb-2 text-warning"><i class="bi bi-info-circle-fill me-2"></i> Clinical Reference Note</h5>
    <p class="small text-muted mb-0">
        Symptoms are non-specific indicators and can arise from multiple independent or interacting physiological mechanisms. One symptom alone does not diagnose a clinical disease. Always discuss persistent or concerning symptoms with a licensed healthcare provider.
    </p>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
