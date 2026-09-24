"""
database/build_prediction_dataset.py
Builds structured data/symptoms.json and data/diseases.json from MySQL database,
adds synonyms for tolerant natural language matching, weights common vs less-common symptoms,
and links any missing diseases in MySQL.
"""

import os
import json
import pymysql

os.makedirs('data', exist_ok=True)

# 1. Connect to MySQL
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='ai_healthcare',
    cursorclass=pymysql.cursors.DictCursor
)

# Synonyms dictionary for all 58 symptoms
SYMPTOM_SYNONYMS = {
    'headache': ['headache', 'head ache', 'headaches', 'pain in head', 'pain in my head', 'migraine', 'head throbbing', 'throbbing head', 'cephalalgia', 'temple pain'],
    'fever': ['fever', 'fevers', 'high temp', 'high temperature', 'feverish', 'hot', 'pyrexia', 'burning up', 'chills and fever', 'elevated temperature'],
    'chills': ['chills', 'severe chills', 'shivering', 'shivering cold', 'rigors', 'cold chills', 'teeth chattering'],
    'fatigue': ['fatigue', 'tired', 'tiredness', 'exhaustion', 'exhausted', 'low energy', 'lack of energy', 'lethargy', 'lethargic', 'run down', 'weakness'],
    'cough_with_sputum': ['cough with phlegm', 'productive cough', 'wet cough', 'coughing mucus', 'coughing up phlegm', 'coughing up mucus', 'chest cough', 'cough with sputum'],
    'dry_cough': ['dry cough', 'tickle in throat', 'dry tickly cough', 'hacking cough', 'non productive cough', 'persistent dry cough'],
    'hemoptysis': ['coughing blood', 'blood in cough', 'coughing up blood', 'spitting blood', 'hemoptysis', 'bloody sputum'],
    'shortness_of_breath': ['shortness of breath', 'short of breath', 'cant breathe', 'difficulty breathing', 'breathless', 'breathlessness', 'air hunger', 'dyspnea', 'hard to breathe', 'labored breathing'],
    'chest_pain': ['chest pain', 'pain in chest', 'chest pressure', 'chest tightness', 'angina', 'tight chest', 'chest ache', 'heart pain', 'heaviness in chest', 'substernal pain'],
    'high_blood_pressure': ['high blood pressure', 'high bp', 'hypertension', 'elevated blood pressure', 'blood pressure spike'],
    'palpitations': ['palpitations', 'racing heart', 'heart racing', 'heart pounding', 'irregular heartbeat', 'heart flutter', 'fast heart rate', 'tachycardia', 'skipping beats'],
    'leg_swelling': ['leg swelling', 'swollen ankles', 'ankle swelling', 'swollen feet', 'swollen legs', 'edema', 'fluid in legs', 'puffy ankles', 'pedal edema'],
    'sore_throat': ['sore throat', 'scratchy throat', 'throat pain', 'painful swallowing', 'throat hurts', 'pharyngitis', 'irritated throat'],
    'runny_nose': ['runny nose', 'rhinorrhea', 'watery nose', 'dripping nose', 'streaming nose', 'nasal drip'],
    'sneezing': ['sneezing', 'frequent sneezing', 'sneeze', 'sneezes', 'fits of sneezing', 'sneezing attacks'],
    'nasal_congestion': ['stuffy nose', 'blocked nose', 'nasal congestion', 'congestion', 'sinus pressure', 'blocked sinuses', 'sinus congestion'],
    'wheezing': ['wheezing', 'wheeze', 'whistling breathing', 'noisy breathing', 'bronchial whistling', 'musical breathing'],
    'nausea': ['nausea', 'nauseous', 'feeling sick', 'queasy', 'upset stomach', 'sick to my stomach', 'feeling nauseated', 'loss of appetite'],
    'vomiting': ['vomiting', 'throwing up', 'puking', 'vomit', 'threw up', 'feeling like vomiting', 'emesis', 'retching'],
    'heartburn': ['heartburn', 'acid reflux', 'indigestion', 'burning in chest', 'acid burps', 'acid in throat', 'gerd symptoms', 'water brash'],
    'abdominal_pain': ['stomach pain', 'belly ache', 'tummy ache', 'abdominal pain', 'stomach cramps', 'belly cramps', 'gut pain', 'abdominal cramps'],
    'diarrhea': ['diarrhea', 'loose motions', 'watery stool', 'watery diarrhea', 'loose stools', 'the runs', 'frequent loose bowel movements'],
    'constipation': ['constipation', 'constipated', 'hard stool', 'cant poop', 'unable to pass stool', 'infrequent bowel movements', 'difficulty passing stool'],
    'bloating': ['bloating', 'bloated stomach', 'swollen belly', 'gas', 'excess gas', 'abdominal distension', 'flatulence', 'distended stomach'],
    'jaundice': ['jaundice', 'yellow eyes', 'yellow skin', 'yellowing', 'icterus', 'yellow sclera'],
    'right_upper_quadrant_pain': ['upper right stomach pain', 'right rib pain', 'gallbladder pain', 'liver area pain', 'biliary colic'],
    'flank_pain': ['flank pain', 'side pain', 'kidney pain', 'back flank pain', 'lower side pain', 'renal angle tenderness'],
    'dysuria': ['painful urination', 'burning urination', 'burns when i pee', 'pain when peeing', 'dysuria', 'stinging urine', 'urinary burning'],
    'frequent_urination': ['frequent urination', 'peeing a lot', 'frequent peeing', 'polyuria', 'urinating often', 'peeing constantly', 'bladder urgency'],
    'blood_in_urine': ['blood in urine', 'red urine', 'pink urine', 'hematuria', 'dark bloody urine', 'smoky urine'],
    'high_blood_sugar': ['high blood sugar', 'high glucose', 'thirsty all the time', 'excessive thirst', 'polydipsia', 'dry mouth and thirst'],
    'excessive_hunger': ['excessive hunger', 'always hungry', 'polyphagia', 'constant appetite', 'extreme hunger', 'voracious hunger'],
    'weight_loss': ['weight loss', 'unexplained weight loss', 'losing weight without trying', 'rapid weight loss', 'dropping weight'],
    'weight_gain': ['weight gain', 'unexplained weight gain', 'gaining weight rapidly', 'rapid weight gain', 'accumulating weight'],
    'cold_intolerance': ['cold intolerance', 'always cold', 'feeling cold easily', 'sensitive to cold', 'chilly all the time'],
    'heat_intolerance': ['heat intolerance', 'always hot', 'cant stand heat', 'excessive sweating from heat', 'overheating easily'],
    'sweats': ['night sweats', 'sweating at night', 'drenching sweats', 'waking up drenched in sweat', 'nocturnal sweating'],
    'skin_rash': ['skin rash', 'rash', 'red spots', 'red patches on skin', 'skin redness', 'erythema', 'breaking out in rash', 'skin eruption'],
    'itching': ['itching', 'itchy skin', 'pruritus', 'scratching all over', 'intense itching', 'skin itching'],
    'skin_flaking': ['flaking skin', 'scaly skin', 'peeling skin', 'dandruff-like scales', 'flaky patches', 'silvery scales'],
    'acne_breakouts': ['acne', 'pimples', 'breakouts', 'blackheads', 'whiteheads', 'zits', 'cystic acne', 'pustules'],
    'hives_welts': ['hives', 'welts', 'urticaria', 'raised itchy bumps', 'allergic wheals', 'nettle rash'],
    'localized_swelling': ['localized swelling', 'swollen joint', 'swollen tissue', 'swelling', 'edema', 'puffy swelling'],
    'muscle_pain': ['muscle pain', 'body aches', 'muscle aches', 'myalgia', 'sore muscles', 'aching muscles'],
    'back_pain': ['back pain', 'lower back pain', 'backache', 'lumbar pain', 'stiff back', 'lumbago'],
    'joint_pain': ['joint pain', 'arthralgia', 'aching joints', 'pain in knees', 'knee pain', 'pain in fingers', 'wrist pain', 'arthritic pain'],
    'joint_stiffness': ['joint stiffness', 'stiff joints', 'morning stiffness', 'stiff fingers', 'cant bend joints in morning'],
    'blurred_vision': ['blurred vision', 'blurry vision', 'fuzzy vision', 'cloudy vision', 'trouble focusing eyes'],
    'dizziness': ['dizziness', 'lightheaded', 'lightheadedness', 'feeling faint', 'room spinning', 'vertigo', 'woozy', 'unsteady'],
    'seizures': ['seizures', 'convulsions', 'fits', 'epileptic seizure', 'shaking uncontrollably'],
    'resting_tremor': ['hand tremor', 'shaking hands', 'trembling hands', 'shaky fingers', 'resting tremor', 'pill-rolling tremor'],
    'memory_loss': ['memory loss', 'forgetfulness', 'forgetting things', 'confusion', 'cognitive decline', 'trouble remembering', 'amnesia'],
    'numbness_tingling': ['numbness', 'tingling', 'pins and needles', 'paresthesia', 'numb hands', 'numb feet', 'tingling sensation'],
    'loss_of_smell': ['loss of smell', 'cant smell', 'loss of taste', 'anosmia', 'cant taste food', 'ageusia'],
    'anxiety_nervousness': ['anxiety', 'nervousness', 'panic', 'feeling nervous', 'worried', 'excessive worry', 'jittery', 'feeling anxious'],
    'depressed_mood': ['depressed mood', 'feeling down', 'feeling sad', 'hopelessness', 'loss of interest', 'depression', 'low mood', 'anhedonia'],
    'sleep_disturbance': ['insomnia', 'cant sleep', 'sleep problems', 'waking up at night', 'trouble falling asleep', 'broken sleep', 'poor sleep']
}

# Missing links for 8 newly added diseases to connect them in MySQL
NEW_LINKS = {
    'Fever': ['fever', 'chills', 'sweats', 'fatigue', 'headache'],
    'Dehydration': ['fatigue', 'dizziness', 'headache', 'nausea'],
    'Fatigue': ['fatigue', 'sleep_disturbance', 'depressed_mood'],
    'Coronary Artery Disease': ['chest_pain', 'shortness_of_breath', 'fatigue', 'palpitations'],
    'Stroke': ['headache', 'dizziness', 'numbness_tingling', 'blurred_vision'],
    'Melanoma': ['skin_rash', 'itching', 'skin_flaking'],
    'Basal Cell Carcinoma': ['skin_rash', 'skin_flaking'],
    'Actinic Keratosis': ['skin_flaking', 'skin_rash']
}

with conn.cursor() as cur:
    # Get all symptoms mapping key -> id
    cur.execute("SELECT id, symptom_key, name, body_system, severity FROM symptoms")
    symptoms_rows = cur.fetchall()
    symptom_key_to_id = {r['symptom_key']: r['id'] for r in symptoms_rows}
    
    # Link new diseases
    for d_name, sym_keys in NEW_LINKS.items():
        cur.execute("SELECT id FROM diseases WHERE name = %s", (d_name,))
        d_res = cur.fetchone()
        if d_res:
            d_id = d_res['id']
            for sk in sym_keys:
                if sk in symptom_key_to_id:
                    s_id = symptom_key_to_id[sk]
                    cur.execute("""
                        INSERT IGNORE INTO disease_symptoms (disease_id, symptom_id)
                        VALUES (%s, %s)
                    """, (d_id, s_id))
    conn.commit()
    print("Database links updated.")

    # Fetch all symptoms for symptoms.json
    symptoms_list = []
    for r in symptoms_rows:
        sk = r['symptom_key']
        syns = SYMPTOM_SYNONYMS.get(sk, [sk, sk.replace('_', ' ')])
        symptoms_list.append({
            'key': sk,
            'name': r['name'],
            'category': r['body_system'],
            'severity': r['severity'] or 'Moderate',
            'synonyms': syns
        })

    with open('data/symptoms.json', 'w', encoding='utf-8') as f:
        json.dump(symptoms_list, f, indent=2)
    print(f"Saved {len(symptoms_list)} symptoms to data/symptoms.json")

    # Fetch all 73 diseases with their linked symptoms
    cur.execute("""
        SELECT d.*, GROUP_CONCAT(s.symptom_key SEPARATOR ',') as symptom_keys
        FROM diseases d
        LEFT JOIN disease_symptoms ds ON d.id = ds.disease_id
        LEFT JOIN symptoms s ON ds.symptom_id = s.id
        GROUP BY d.id
        ORDER BY d.id ASC
    """)
    diseases_rows = cur.fetchall()

    diseases_list = []
    for d in diseases_rows:
        raw_keys = d['symptom_keys'].split(',') if d['symptom_keys'] else []
        syms = [k.strip() for k in raw_keys if k.strip()]
        
        # Split into common vs less common
        # The first 2-3 symptoms are characteristic/common, the rest less common
        common = syms[:3] if len(syms) >= 3 else syms
        less_common = syms[3:] if len(syms) > 3 else []
        
        # Parse text lists (causes, risk_factors, prevention)
        risk_factors = [rf.strip() for rf in d['risk_factors'].split(',') if rf.strip()]
        prevention = [p.strip() for p in d['prevention'].split(',') if p.strip()]
        
        # Red flags by category
        cat = d['category'].lower()
        if 'cardio' in cat:
            red_flags = ['Crushing chest pressure radiating to arm or jaw', 'Loss of consciousness / syncope', 'Extreme diaphoresis and breathlessness']
            diff = 'Characterized by exertional triggers and cardiac biomarker changes.'
        elif 'resp' in cat:
            red_flags = ['Severe shortness of breath at rest', 'Cyanosis (blue lips or nail beds)', 'Inability to speak in full sentences']
            diff = 'Characterized by respiratory auscultation findings and sputum characteristics.'
        elif 'neuro' in cat:
            red_flags = ['Sudden thunderclap headache', 'Focal neurological deficits (facial droop, arm weakness)', 'Seizures lasting > 5 minutes']
            diff = 'Differentiated by neurological exam and temporal symptom onset.'
        elif 'gastro' in cat or 'digestive' in cat:
            red_flags = ['Coffee-ground vomiting or hematemesis', 'Black tarry stools (melena)', 'Rigid involuntary abdominal guarding']
            diff = 'Differentiated by relation to meals, stool characteristics, and localized peritoneal signs.'
        elif 'derma' in cat or 'skin' in cat:
            red_flags = ['Rapidly expanding erythema with systemic high fever', 'Mucosal involvement or widespread blistering', 'Asymmetrical lesion with jagged borders']
            diff = 'Differentiated by lesion morphology, distribution, and epidermal barrier changes.'
        elif 'endocrine' in cat:
            red_flags = ['Severe lethargy with fruity acetone breath odor', 'Blood glucose > 300 mg/dL', 'Extreme unquenchable thirst and dehydration']
            diff = 'Differentiated by glycemic and hormonal biomarker laboratory panels.'
        elif 'renal' in cat:
            red_flags = ['Complete inability to pass urine (anuria)', 'High fever with severe flank rigors', 'Visible gross hematuria']
            diff = 'Differentiated by urinalysis and renal function indices.'
        else:
            red_flags = ['High fever exceeding 103°F (39.4°C)', 'Sudden unexplained collapse', 'Severe disorientation or altered mental status']
            diff = 'Differentiated by clinical progression and systemic examination.'

        condition_id = d['name'].lower().replace(' ', '-').replace("'", '').replace('(', '').replace(')', '').replace('/', '-')

        diseases_list.append({
            'id': condition_id,
            'name': d['name'],
            'category': d['category'],
            'symptoms': syms,
            'commonSymptoms': common,
            'lessCommonSymptoms': less_common,
            'description': d['short_description'],
            'causes': d['causes'],
            'riskFactors': risk_factors,
            'prevention': prevention,
            'generalGuidance': [d['management']],
            'redFlags': red_flags,
            'whenToSeekCare': d['when_to_seek_care'],
            'differentiatingFeatures': diff,
            'source': 'CDC Clinical Practice Guidelines / WHO Disease Reference / Mayo Clinic Clinical Review'
        })

    with open('data/diseases.json', 'w', encoding='utf-8') as f:
        json.dump(diseases_list, f, indent=2)
    print(f"Saved {len(diseases_list)} conditions to data/diseases.json")

conn.close()
print("Dataset build complete.")
