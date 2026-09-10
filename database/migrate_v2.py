import pymysql
import sys

def run_migration():
    print("Connecting to MySQL ai_healthcare...")
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='ai_healthcare',
        charset='utf8mb4',
        autocommit=False
    )
    cur = conn.cursor()

    # 1. EXPAND SYMPTOMS (IDs 31-58)
    symptoms_data = [
        (31, 'Runny or Stuffy Nose (Rhinorrhea)', 'runny_nose', 'Respiratory', 'Mild'),
        (32, 'Frequent Sneezing', 'sneezing', 'Respiratory', 'Mild'),
        (33, 'Sore or Scratchy Throat', 'sore_throat', 'Respiratory', 'Mild'),
        (34, 'Dry Non-Productive Cough', 'dry_cough', 'Respiratory', 'Moderate'),
        (35, 'Sinus Pressure & Nasal Congestion', 'nasal_congestion', 'Respiratory', 'Moderate'),
        (36, 'Loss of Smell or Taste (Anosmia)', 'loss_of_smell', 'Neurological', 'Moderate'),
        (37, 'Frequent Watery Diarrhea', 'diarrhea', 'Gastrointestinal', 'Moderate'),
        (38, 'Severe or Chronic Constipation', 'constipation', 'Gastrointestinal', 'Moderate'),
        (39, 'Abdominal Bloating & Gas Distension', 'bloating', 'Gastrointestinal', 'Mild'),
        (40, 'Visible Skin Rash or Erythema', 'skin_rash', 'Dermatological', 'Moderate'),
        (41, 'Intense Pruritus / Persistent Itching', 'itching', 'Dermatological', 'Mild'),
        (42, 'Flaking or Scaly Skin Patches', 'skin_flaking', 'Dermatological', 'Moderate'),
        (43, 'Acne Papules, Pustules or Cysts', 'acne_breakouts', 'Dermatological', 'Mild'),
        (44, 'Raised Itchy Wheals / Hives (Urticaria)', 'hives_welts', 'Dermatological', 'Moderate'),
        (45, 'Localized Tissue Swelling or Edema', 'localized_swelling', 'Systemic', 'Moderate'),
        (46, 'Muscle Aches & Myalgia', 'muscle_pain', 'Musculoskeletal', 'Moderate'),
        (47, 'Lower Back Ache or Lumbar Stiffness', 'back_pain', 'Musculoskeletal', 'Moderate'),
        (48, 'Morning Joint Stiffness', 'joint_stiffness', 'Musculoskeletal', 'Moderate'),
        (49, 'Numbness, Tingling or Paresthesia', 'numbness_tingling', 'Neurological', 'Moderate'),
        (50, 'Blurred or Fluctuating Vision', 'blurred_vision', 'Neurological', 'Moderate'),
        (51, 'Excessive Hunger (Polyphagia)', 'excessive_hunger', 'Endocrine', 'Mild'),
        (52, 'Unintentional Rapid Weight Gain', 'weight_gain', 'Endocrine', 'Mild'),
        (53, 'Diffuse Hair Thinning or Hair Loss', 'hair_thinning', 'Dermatological', 'Mild'),
        (54, 'Excessive Worry, Nervousness or Panic', 'anxiety_nervousness', 'Psychological', 'Moderate'),
        (55, 'Persistent Sadness or Low Energy Mood', 'depressed_mood', 'Psychological', 'Moderate'),
        (56, 'Insomnia or Disrupted Sleep Quality', 'sleep_disturbance', 'Psychological', 'Moderate'),
        (57, 'Lower Extremity / Ankle Edema', 'leg_swelling', 'Cardiovascular', 'Moderate'),
        (58, 'Hematuria / Discolored Urine', 'blood_in_urine', 'Renal', 'Severe')
    ]

    sym_sql = """
    INSERT INTO symptoms (id, name, symptom_key, body_system, severity)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        symptom_key = VALUES(symptom_key),
        body_system = VALUES(body_system),
        severity = VALUES(severity);
    """
    for row in symptoms_data:
        cur.execute(sym_sql, row)
    print(f"Upserted {len(symptoms_data)} expanded symptoms.")

    # 2. EXPAND DISEASES (IDs 26-65)
    diseases_data = [
        (26, 'Common Cold', 'Respiratory',
         'A mild viral infectious disease of the upper respiratory tract primarily affecting the nasal mucosa and throat.',
         'Rhinoviruses, coronaviruses, adenoviruses, or enteroviruses.',
         'Exposure to infected individuals, seasonal winter changes, psychological stress, sleep deprivation.',
         'Frequent hand hygiene, avoiding touching facial mucous membranes, maintaining adequate hydration and rest.',
         'Rest, oral hydration, warm saline gargles, over-the-counter decongestants or analgesics as appropriate.',
         'Seek medical care if symptoms persist beyond 10-14 days, high fever develops, or wheezing occurs.'),

        (27, 'Allergic Rhinitis', 'Respiratory',
         'Inflammation of the interior nasal passages caused by an IgE-mediated allergic response to inhaled environmental allergens.',
         'Inhaled allergens including tree/grass pollen, house dust mites, animal dander, and fungal spores.',
         'Atopic genetic predisposition, family history of asthma or eczema, high environmental allergen exposure.',
         'Minimize exposure to identified allergens, use HEPA filtration, keep windows closed during high pollen counts.',
         'Nasal corticosteroid sprays, oral second-generation antihistamines, saline nasal rinses, allergen immunotherapy.',
         'Seek evaluation if chronic nasal obstruction causes secondary sinusitis or impairs quality of sleep.'),

        (28, 'Sinusitis', 'Respiratory',
         'Inflammation or infection of the mucosal lining of the paranasal sinuses, causing facial pressure and nasal congestion.',
         'Secondary bacterial infection following viral upper respiratory infection, allergic swelling, or anatomical nasal polyps.',
         'Recent viral cold, allergic rhinitis, structural deviated septum, environmental smoke exposure.',
         'Prompt management of colds and allergies, indoor humidification, nasal saline irrigation.',
         'Nasal saline irrigation, decongestants, intranasal steroids, oral antibiotics if bacterial infection confirmed.',
         'Seek urgent medical care if experiencing severe headache, periorbital swelling, vision changes, or high fever.'),

        (29, 'Heart Failure', 'Cardiovascular',
         'A chronic, progressive condition in which the cardiac muscle is unable to pump sufficient blood volume to meet systemic metabolic demands.',
         'Long-standing hypertension, prior myocardial infarction, coronary artery disease, cardiomyopathy, or valvular heart disease.',
         'Hypertension, history of heart attack, diabetes, obesity, smoking, excessive alcohol consumption.',
         'Strict blood pressure control, coronary disease prevention, smoking cessation, low-sodium dietary habits.',
         'ACE inhibitors/ARNs, beta-blockers, aldosterone antagonists, SGLT2 inhibitors, diuretics, fluid restriction, daily weight tracking.',
         'Seek immediate emergency care for sudden severe breathlessness, inability to lie flat, or rapid unexplained weight gain (>3 lbs in 24h).'),

        (30, 'Arrhythmia', 'Cardiovascular',
         'Disruptions or irregularities in the electrical conduction system of the heart, resulting in bradycardia, tachycardia, or fibrillatory rhythm.',
         'Ischemic heart disease, electrolyte imbalances, structural cardiac remodeling, caffeine, thyroid disease, or electrical channelopathies.',
         'Underlying coronary disease, hypertension, electrolyte disturbances (potassium/magnesium), sleep apnea, stimulant use.',
         'Limit caffeine and alcohol, avoid illicit stimulants, manage stress, monitor electrolyte balance.',
         'Anti-arrhythmic medications, rate-control agents (beta-blockers), catheter ablation, cardioversion, pacemakers or ICDs.',
         'Seek immediate emergency medical care for palpitations accompanied by syncope, chest pain, or severe dizziness.'),

        (31, 'Angina Pectoris', 'Cardiovascular',
         'Reversible chest pain or pressure resulting from transient myocardial ischemia due to inadequate coronary blood flow.',
         'Atherosclerotic coronary artery stenosis restricting oxygen delivery during times of increased myocardial workload.',
         'Coronary artery disease, hypertension, dyslipidemia, smoking, diabetes, sedentary lifestyle.',
         'Manage cardiovascular risk factors, adhere to Mediterranean-style diet, smoking cessation, regular moderate exercise.',
         'Sublingual nitroglycerin for acute episodes, beta-blockers, calcium channel blockers, statins, antiplatelet therapy.',
         'Seek emergency medical services immediately if chest pain lasts longer than 10 minutes or does not resolve with rest and nitroglycerin.'),

        (32, 'Peripheral Artery Disease', 'Cardiovascular',
         'A circulatory condition in which atherosclerotic plaque narrows peripheral arteries, severely reducing blood flow to the limbs.',
         'Systemic atherosclerosis affecting the abdominal aorta, iliac, femoral, and popliteal arterial branches.',
         'Cigarette smoking, type 2 diabetes, chronic hypertension, advanced age, hypercholesterolemia.',
         'Smoking cessation, routine walking exercise programs, glycemic and lipid control, blood pressure optimization.',
         'Supervised exercise therapy, antiplatelet medications (aspirin/clopidogrel), statin therapy, cilostazol, endovascular revascularization.',
         'Seek urgent care for resting foot pain, cold/pale extremities, or non-healing ulcers on the lower extremities.'),

        (33, 'Prediabetes', 'Endocrine',
         'A metabolic state where blood glucose levels are above normal ranges (HbA1c 5.7-6.4%) but not yet meeting the threshold for type 2 diabetes.',
         'Progressive peripheral insulin resistance coupled with relative pancreatic beta-cell secretory compensation.',
         'Overweight/obesity (BMI > 25), physical inactivity, age > 45, family history of type 2 diabetes, gestational diabetes history.',
         'Structured lifestyle interventions: 7% sustained weight reduction, 150 minutes/week moderate physical exercise, whole-food diet.',
         'Intensive dietary modification, aerobic and resistance training, routine HbA1c monitoring every 6-12 months, metformin where indicated.',
         'Consult a physician for routine screening if persistent fatigue, increased thirst, or unexplained weight shifts occur.'),

        (34, 'Obesity', 'Endocrine',
         'A complex, chronic multifactorial disease characterized by excessive adiposity that impairs physical and metabolic health.',
         'Energy imbalance between caloric consumption and metabolic expenditure, neuroendocrine appetite regulation dysregulation, genetics.',
         'Sedentary lifestyle, high-density refined food availability, endocrine disruptors, chronic sleep disruption, genetic susceptibility.',
         'Whole-food dietary patterns, regular daily physical activity, stress mitigation, adequate sleep, behavioral health support.',
         'Comprehensive lifestyle therapy, medical nutritional therapy, pharmacotherapy (GLP-1 receptor agonists), bariatric metabolic surgery.',
         'Seek healthcare consultation when excess weight contributes to joint pain, obstructive sleep apnea, or metabolic dysregulation.'),

        (35, 'Polycystic Ovary Syndrome (PCOS)', 'Endocrine',
         'A prevalent endocrine disorder in reproductive-aged females characterized by ovulatory dysfunction, hyperandrogenism, and polycystic ovarian morphology.',
         'Complex genetic, neuroendocrine, and metabolic factors with underlying hyperinsulinemia and ovarian theca-cell androgen overproduction.',
         'Family history of PCOS, insulin resistance, metabolic syndrome, obesity, sedentary lifestyle.',
         'Weight management, low-glycemic dietary habits, regular physical activity to enhance peripheral insulin sensitivity.',
         'Combined oral contraceptives, metformin for insulin resistance, lifestyle modification, anti-androgens (spironolactone), ovulation induction.',
         'Consult a gynecologist or endocrinologist for irregular menstrual cycles, severe cystic acne, or difficulty conceiving.'),

        (36, 'GERD (Acid Reflux)', 'Gastrointestinal',
         'A chronic gastrointestinal disorder where stomach acid persistently refluxes backward into the esophagus, irritating the mucosal lining.',
         'Transient lower esophageal sphincter (LES) relaxations, hiatal hernia, delayed gastric emptying, increased intra-abdominal pressure.',
         'Obesity, pregnancy, hiatal hernia, smoking, late-night heavy meals, consumption of fatty, spicy, citrus, or caffeinated foods.',
         'Elevate head of bed, avoid recumbency within 3 hours of meals, lose excess weight, avoid trigger foods, stop smoking.',
         'Proton pump inhibitors (PPIs), H2-receptor antagonists, antacids, lifestyle modifications, endoscopic or surgical fundoplication.',
         'Seek prompt evaluation for progressive dysphagia (trouble swallowing), unintentional weight loss, hematemesis, or anemia.'),

        (37, 'Peptic Ulcer Disease', 'Gastrointestinal',
         'Erosive mucosal lesions occurring in the protective inner lining of the stomach (gastric ulcer) or proximal small intestine (duodenal ulcer).',
         'Helicobacter pylori bacterial colonization, chronic usage of nonsteroidal anti-inflammatory drugs (NSAIDs), hyperacidity.',
         'H. pylori infection, regular NSAID or aspirin use, smoking, heavy alcohol consumption, severe physiological stress.',
         'Eradicate H. pylori, minimize unprescribed NSAID use, co-prescribe gastroprotection (PPIs) when chronic NSAIDs are required, avoid smoking.',
         'Antibiotic eradication therapy for H. pylori, proton pump inhibitors, mucosal protective agents, avoiding mucosal irritants.',
         'Seek immediate emergency evaluation for vomiting frank blood or coffee-ground emesis, black tarry stools, or sudden acute abdominal pain.'),

        (38, 'Gastroenteritis', 'Gastrointestinal',
         'An acute inflammation of the gastrointestinal tract mucous membranes, involving both stomach and small intestine.',
         'Viral pathogens (Norovirus, Rotavirus), bacterial toxins (Salmonella, Campylobacter, E. coli), or parasitic protozoa.',
         'Consumption of contaminated water or unpasteurized food, poor hand hygiene, crowded living conditions, international travel.',
         'Meticulous hand washing with soap and water, hygienic food storage and preparation, drinking clean treated water, rotavirus vaccination.',
         'Oral rehydration therapy with balanced electrolyte solutions, gradual reintroduction of bland diet, zinc supplementation, antiemetics if needed.',
         'Seek urgent care if signs of dehydration emerge (sunken eyes, dizziness, absence of urination), bloody stool, or inability to tolerate liquids.'),

        (39, 'Irritable Bowel Syndrome (IBS)', 'Gastrointestinal',
         'A common disorder of the brain-gut interaction characterized by recurrent abdominal pain related to defecation or changes in bowel habits.',
         'Visceral hypersensitivity, altered gut-brain communication, gastrointestinal dysmotility, post-infectious inflammation, altered gut microbiome.',
         'Female sex, severe preceding bacterial gastroenteritis, chronic psychological stress, early adverse life events.',
         'Stress reduction, identifying individual food triggers, regular meal patterns, adequate dietary fiber and hydration.',
         'Low-FODMAP dietary trial, soluble fiber (psyllium), antispasmodics, neuromodulators, gut-directed cognitive behavioral therapy.',
         'Seek medical assessment for "red flag" symptoms: nocturnal symptoms, unintended weight loss, rectal bleeding, or onset after age 50.'),

        (40, 'Chronic Constipation', 'Gastrointestinal',
         'A functional gastrointestinal condition marked by infrequent, difficult, or incomplete evacuation of dry, hardened stool.',
         'Inadequate dietary fiber, insufficient hydration, pelvic floor dyssynergia, slow transit colonic motility, side effect of medications.',
         'Low-fiber diet, sedentary lifestyle, suppressing the urge to defecate, medications (opioids, calcium channel blockers, iron supplements).',
         'High-fiber diet (25-35 grams/day), plentiful fluid intake, regular physical activity, establishing consistent toilet routines.',
         'Bulk-forming laxatives (psyllium), osmotic laxatives (polyethylene glycol), pelvic floor physical therapy, biofeedback.',
         'Consult a physician if constipation is accompanied by severe abdominal distension, vomiting, rectal bleeding, or sudden onset in older adults.'),

        (41, 'Chronic Diarrhea', 'Gastrointestinal',
         'Frequent loose, watery stools persisting continuously or intermittently for greater than four weeks in duration.',
         'Inflammatory bowel disease (Crohn\'s/Colitis), celiac disease, malabsorption syndromes, chronic parasitic infection, microscopic colitis.',
         'Autoimmune history, family history of IBD or celiac disease, prior gastrointestinal surgeries, chronic antibiotic or metformin use.',
         'Prompt investigation of dietary intolerances (gluten, lactose), hygienic water sources during travel, cautious antibiotic usage.',
         'Etiology-specific treatment (gluten-free diet for celiac, anti-inflammatory therapy for IBD), electrolyte replenishment, anti-diarrheal agents.',
         'Seek thorough clinical evaluation for chronic diarrhea accompanied by unintended weight loss, fever, anemia, or visible blood in stool.'),

        (42, 'Gallstones', 'Gastrointestinal',
         'Hardened mineral deposits formed inside the gallbladder, predominantly composed of crystallized cholesterol or bilirubin pigments.',
         'Supersaturation of bile with cholesterol, gallbladder hypomotility, excessive biliary bilirubin secretion.',
         'Female sex, age > 40, multiparity, rapid weight loss, obesity, high-fat diet, hemolytic blood disorders.',
         'Maintain a healthy body weight gradually (avoid crash starvation diets), eat a balanced fiber-rich diet with healthy unsaturated fats.',
         'Observation for asymptomatic stones; laparoscopic cholecystectomy for symptomatic recurrent biliary colic or acute cholecystitis.',
         'Seek emergency medical evaluation for severe right upper quadrant pain radiating to shoulder, fever, persistent vomiting, or jaundice.'),

        (43, 'Tension Headache', 'Neurological',
         'The most prevalent type of primary headache, presenting as mild-to-moderate dull, band-like tightening pressure across the head and neck.',
         'Myofascial trigger points, pericranial muscle tenderness, central pain sensitization, prolonged emotional stress.',
         'Chronic emotional or occupational stress, poor ergonomic posture, ocular strain, clenching jaw/teeth, sleep deprivation.',
         'Regular ergonomic breaks, adequate nocturnal sleep, stress management, hydration, stretching of cervical and shoulder muscles.',
         'Over-the-counter analgesics (acetaminophen, NSAIDs), physical therapy, stress management techniques, tricyclic antidepressants for chronic cases.',
         'Seek evaluation for sudden severe "thunderclap" headache, new headaches after age 50, or associated focal neurological deficits.'),

        (44, 'Peripheral Neuropathy', 'Neurological',
         'Damage to the peripheral nervous system leading to weakness, numbness, tingling, or burning sensations primarily in hands and feet.',
         'Diabetic microvascular axonal damage, chronic alcoholism, vitamin B12 deficiency, chemotherapy toxicity, autoimmune disorders.',
         'Poorly controlled diabetes mellitus, heavy alcohol consumption, chemotherapy treatments, nutritional deficiencies, renal disease.',
         'Strict blood glucose control in diabetes, moderation of alcohol, adequate nutritional vitamin B12 intake, foot protective care.',
         'Optimization of underlying cause, neuropathic pain agents (gabapentin, pregabalin, duloxetine), physical therapy, daily foot inspections.',
         'Seek medical attention for progressive numbness spreading upward, unhealed foot ulcers, or difficulty with balance and walking.'),

        (45, 'Kidney Stones', 'Renal / Urological',
         'Solid mineral and acid salt crystalline aggregations that form within renal calyces and pass into the urinary tract.',
         'Supersaturation of urine with calcium, oxalate, phosphate, or uric acid coupled with inadequate urinary fluid volume.',
         'Low fluid intake, high dietary sodium/animal protein, family history of nephrolithiasis, hyperparathyroidism, gout.',
         'Drink 2.5 to 3 liters of water daily to maintain clear dilute urine, limit sodium and excess animal protein, ensure normal calcium intake.',
         'Adequate hydration, alpha-blockers (tamsulosin) to aid stone passage, oral analgesia, shock-wave lithotripsy or ureteroscopy for large stones.',
         'Seek immediate emergency care for intractable flank pain, persistent vomiting, inability to urinate, or high fever with chills.'),

        (46, 'Kidney Infection (Pyelonephritis)', 'Renal / Urological',
         'An acute bacterial infection of the renal parenchyma and renal pelvis, usually ascending from the lower urinary tract.',
         'Ascending spread of uropathogenic bacteria (primarily Escherichia coli) from cystitis through ureters into the kidney.',
         'Untreated or recurrent lower urinary tract infections, female anatomy, urinary catheterization, kidney stones, pregnancy, diabetes.',
         'Prompt, complete treatment of bladder infections, generous hydration, post-coital urination, proper perineal hygiene.',
         'Empirical and culture-directed oral or intravenous antibiotics for 7-14 days, antipyretics, adequate oral or IV fluid hydration.',
         'Seek emergency medical care immediately for high fever, severe flank pain, shaking chills, nausea, or confusion.'),

        (47, 'Acne Vulgaris', 'Dermatological',
         'A chronic inflammatory dermatological disorder of the pilosebaceous units characterized by comedones, papules, pustules, or cysts.',
         'Excess sebum production, follicular hyperkeratinization, Cutibacterium acnes bacterial proliferation, and inflammatory mediator release.',
         'Adolescent hormonal surges, androgen excess, family history, high-glycemic index diets, comedogenic cosmetic products.',
         'Gentle non-abrasive facial cleansing twice daily, avoiding picking or squeezing lesions, non-comedogenic oil-free skincare.',
         'Topical retinoids, benzoyl peroxide, topical/oral antibiotics, salicylic acid, hormonal therapies (oral contraceptives, spironolactone), oral isotretinoin.',
         'Seek dermatological consultation for painful deep cysts, scarring acne lesions, or lack of response to non-prescription remedies.'),

        (48, 'Eczema (Atopic Dermatitis)', 'Dermatological',
         'A chronic, pruritic inflammatory skin condition characterized by defective epidermal barrier function and immune dysregulation.',
         'Genetic mutations in the filaggrin (FLG) gene, epidermal skin barrier disruption, Th2-skewed immune hyperreactivity.',
         'Personal or family history of atopy (asthma, allergic rhinitis), dry climates, frequent bathing with harsh soaps, environmental irritants.',
         'Frequent skin moisturization with bland thick emollient ointments, lukewarm brief baths, fragrance-free detergents, avoiding wool clothing.',
         'Liberal emollient moisturizers, topical corticosteroids, topical calcineurin inhibitors, phototherapy, biologic therapies (dupilumab).',
         'Seek prompt medical attention if eczema lesions exhibit signs of bacterial superinfection (honey-colored crusting, pustules, severe pain).'),

        (49, 'Psoriasis', 'Dermatological',
         'A chronic autoimmune inflammatory dermatosis characterized by well-demarcated erythematous plaques covered with silvery micaceous scales.',
         'Immune-mediated acceleration of epidermal keratinocyte turnover driven by the IL-23/IL-17 cytokine signaling pathway.',
         'Genetic susceptibility (HLA-Cw6), physiological or psychological stress, streptococcal pharyngeal infection, smoking, obesity, alcohol.',
         'Stress reduction, avoiding skin trauma/friction (Koebner phenomenon), maintaining healthy body weight, avoiding smoking and heavy drinking.',
         'Topical corticosteroids, topical vitamin D analogs, phototherapy (narrowband UVB), systemic methotrexate, biologic targeted agents.',
         'Consult a dermatologist for extensive cutaneous involvement, severe discomfort, or associated joint pain (psoriatic arthritis).'),

        (50, 'Contact Dermatitis', 'Dermatological',
         'An acute or chronic cutaneous inflammatory reaction elicited by direct contact with an external chemical, allergen, or physical irritant.',
         'Either direct cytotoxic irritant injury (Irritant Contact Dermatitis) or delayed Type IV cell-mediated allergy (Allergic Contact Dermatitis).',
         'Occupational chemical exposure (hairdressers, healthcare, cleaners), nickel jewelry, poison ivy/oak, fragrance ingredients, topical neomycin.',
         'Identify and rigorously avoid contact with causative allergens or irritants, wear protective barrier gloves, wash skin immediately after accidental exposure.',
         'Cool wet compresses, topical corticosteroid creams, oral antihistamines for pruritus, barrier repair creams.',
         'Seek care if dermatitis affects eyes, face, or genitalia, spreads rapidly, or develops secondary bacterial pustules or cellulitis.'),

        (51, 'Fungal Skin Infection', 'Dermatological',
         'Superficial fungal colonization of the keratinized layer of skin, hair, or nails caused by dermatophytes or yeasts.',
         'Dermatophyte fungi (Trichophyton, Microsporum, Epidermophyton) or Candida albicans yeast proliferating in warm, humid skin folds.',
         'Warm humid environments, excessive perspiration, occlusive footwear, communal showers/gyms, diabetes mellitus, compromised immunity.',
         'Keep skin clean and dry, wear breathable cotton clothing, dry thoroughly after bathing, wear sandals in public locker rooms and showers.',
         'Topical antifungal creams (clotrimazole, terbinafine, miconazole) applied for 2-4 weeks, oral antifungals for widespread or nail infections.',
         'Seek medical consultation if fungal rash does not improve after 2 weeks of over-the-counter treatment or spreads extensively.'),

        (52, 'Urticaria (Hives)', 'Dermatological',
         'A transient vascular reaction of the dermis characterized by intensely pruritic, raised, erythematous wheals with surrounding flare.',
         'Mast cell and basophil degranulation with rapid release of histamine and vasodilatory mediators triggered by allergens, infections, or physical stimuli.',
         'Viral infections, food allergies (nuts, shellfish), medications (NSAIDs, antibiotics), insect stings, physical stimuli (heat, cold, pressure).',
         'Identify and avoid known specific triggering allergens, minimize physical skin friction, avoid unneeded NSAIDs during acute flares.',
         'Second-generation H1-antihistamines (cetirizine, fexofenadine, loratadine), H2-blockers, cool compresses, oral corticosteroids for severe flares.',
         'Seek immediate emergency care if hives occur with facial/lip/tongue swelling (angioedema), difficulty breathing, or dizziness (anaphylaxis).'),

        (53, 'Osteoarthritis', 'Musculoskeletal',
         'A progressive degenerative joint disease characterized by breakdown of articular cartilage, subchondral bone remodeling, and osteophyte formation.',
         'Biomechanical joint stress, age-related chondrocyte senescence, repetitive mechanical microtrauma, low-grade joint inflammation.',
         'Advanced age, female sex, obesity (excess load on weight-bearing joints), prior traumatic joint injury, repetitive occupational joint stress.',
         'Maintain healthy body weight to reduce knee/hip mechanical loading, engage in low-impact aerobic exercise (swimming, cycling), avoid joint trauma.',
         'Physical therapy, quadriceps muscle strengthening, weight loss, acetaminophen or topical NSAIDs, intra-articular injections, joint replacement surgery.',
         'Consult an orthopedic specialist for progressive joint pain limiting ambulation or daily self-care activities.'),

        (54, 'Rheumatoid Arthritis', 'Musculoskeletal',
         'A chronic, systemic autoimmune disease characterized by symmetric inflammatory polyarthritis, synovial proliferation, and progressive joint destruction.',
         'Autoimmune targeting of synovial tissue by autoantibodies (Rheumatoid Factor, anti-CCP), leading to chronic pannus formation and cartilage erosion.',
         'Female sex, genetic predisposition (HLA-DRB1 alleles), cigarette smoking, family history of autoimmune disease.',
         'Smoking cessation, maintaining optimal dental hygiene, early diagnostic assessment upon onset of symmetric joint swelling.',
         'Disease-modifying antirheumatic drugs (DMARDs, e.g. methotrexate), biologic TNF/IL-6 inhibitors, short-term corticosteroids, physical therapy.',
         'Seek urgent rheumatology evaluation within weeks of developing persistent symmetric joint swelling, morning stiffness > 1 hour, or hand deformities.'),

        (55, 'Osteoporosis', 'Musculoskeletal',
         'A systemic skeletal disease characterized by low bone mineral density and microarchitectural deterioration, resulting in heightened bone fragility.',
         'Imbalance between osteoclastic bone resorption and osteoblastic bone formation, accelerated by postmenopausal estrogen decline or aging.',
         'Postmenopausal female status, advanced age, low body weight, calcium/vitamin D deficiency, glucocorticoid therapy, sedentary lifestyle, smoking.',
         'Adequate dietary calcium and vitamin D, regular weight-bearing and resistance training exercises, fall prevention strategies, smoking cessation.',
         'Antiresorptive medications (bisphosphonates, denosumab), anabolic agents (teriparatide), calcium and vitamin D supplementation, DEXA scans.',
         'Seek medical care following any low-trauma fall resulting in severe bone/hip pain, or progressive height loss and dorsal kyphosis.'),

        (56, 'Gout', 'Musculoskeletal',
         'A painful form of inflammatory crystal arthritis caused by the deposition of monosodium urate monohydrate crystals within articular and periarticular tissues.',
         'Persistent hyperuricemia exceeding the saturation threshold due to renal urate underexcretion or excessive purine metabolism.',
         'Male sex, high-purine diet (red meat, seafood, beer, distilled spirits), high-fructose corn syrup, obesity, hypertension, diuretics.',
         'Limit high-purine foods, eliminate beer and sweetened beverages, maintain high daily hydration, manage weight, avoid crash dieting.',
         'Acute flare: NSAIDs, colchicine, or corticosteroids. Long-term management: urate-lowering therapy (allopurinol, febuxostat) targeting uric acid < 6 mg/dL.',
         'Seek prompt care for acute, excruciating monoarticular joint swelling (commonly the first metatarsophalangeal big toe joint).'),

        (57, 'Muscle Strain', 'Musculoskeletal',
         'An acute or repetitive stretch injury causing tearing of muscle fibers or their associated myotendinous junctions.',
         'Overstretching, excessive eccentric muscular load, sudden violent contraction, or repetitive ergonomic fatigue without adequate warm-up.',
         'Poor muscle flexibility, muscular fatigue, inadequate pre-exercise warm-up, prior muscle injury, sudden resumption of vigorous exertion.',
         'Thorough dynamic warm-up before athletic activity, gradual progression of workout intensity, core muscle strengthening, ergonomic lifting form.',
         'R.I.C.E. protocol (Rest, Ice, Compression, Elevation) initially, brief course of oral NSAIDs, gentle progressive stretching, physical therapy.',
         'Seek medical evaluation for an audible muscle "pop", severe inability to bear weight, visible muscular defect, or significant hematoma.'),

        (58, 'Vitamin B12 Deficiency', 'Hematological',
         'A nutritional hematological and neurological disorder caused by insufficient cobalamin levels, leading to megaloblastic anemia and neuropathy.',
         'Pernicious anemia (autoimmune destruction of gastric parietal cells / lack of intrinsic factor), strict vegan diet without supplementation, malabsorption.',
         'Strict vegetarian/vegan diets, age > 65, chronic proton pump inhibitor or metformin use, prior gastric bypass or ileal resection, celiac disease.',
         'Incorporate B12-rich foods (eggs, dairy, fortified cereals) or take regular oral cobalamin supplements if adhering to plant-based diets.',
         'Oral high-dose vitamin B12 (1000 mcg daily) or intramuscular cyanocobalamin/hydroxocobalamin injections until stores are replenished.',
         'Seek medical evaluation for persistent numbness in extremities, unsteady gait, cognitive changes, or unexplained fatigue and pale skin.'),

        (59, 'Vitamin D Deficiency', 'Hematological',
         'A systemic nutritional insufficiency resulting from inadequate synthesis or dietary intake of calciferol, impairing calcium and bone homeostasis.',
         'Limited cutaneous synthesis from sunlight exposure, low dietary intake, malabsorption, renal/hepatic conversion impairments, pigmented skin.',
         'Living in northern latitudes, limited outdoor sun exposure, extensive sunscreen use, darker skin pigmentation, obesity, malabsorptive bowel disease.',
         'Sensible sun exposure, consuming vitamin D-fortified milk/cereals and fatty fish, routine daily supplementation of 800-2000 IU/day.',
         'High-dose oral ergocalciferol (D2) or cholecalciferol (D3) therapy, followed by long-term maintenance supplementation and serum 25(OH)D monitoring.',
         'Seek healthcare consultation for persistent diffuse musculoskeletal aching, proximal muscle weakness, or recurrent bone stress fractures.'),

        (60, 'Sickle Cell Disease', 'Hematological',
         'An inherited genetic hemoglobinopathy caused by a point mutation in the beta-globin gene, resulting in abnormal sickle-shaped red blood cells.',
         'Homozygous inheritance of the HbS allele (glutamic acid substituted by valine at position 6 of the beta-globin chain).',
         'African, Mediterranean, Middle Eastern, or South Asian ancestral descent; positive parental sickle cell carrier status.',
         'Genetic counseling and carrier screening, avoiding cold exposure, preventing dehydration, avoiding high-altitude hypoxic triggers.',
         'Hydroxyurea to boost fetal hemoglobin, routine vaccinations, prophylactic penicillin in children, hydration, multimodal pain crisis protocols.',
         'Seek immediate emergency medical care for acute vaso-occlusive pain crises, acute chest syndrome (chest pain/fever/cough), or stroke symptoms.'),

        (61, 'Generalized Anxiety', 'Psychological',
         'An educational screening category for persistent, excessive, and uncontrollable worry regarding various everyday life events and activities.',
         'Dysregulation of amygdala-prefrontal neurocircuitry, neurotransmitter imbalances (GABA, serotonin, norepinephrine), chronic psychosocial stress.',
         'Family history of anxiety, major chronic life stress, personality traits (neuroticism), chronic physical illnesses, substance use.',
         'Cognitive reframing, regular aerobic physical activity, consistent sleep hygiene, minimizing caffeine and stimulant consumption, mindfulness.',
         'Evidence-based cognitive behavioral therapy (CBT), mindfulness-based stress reduction, SSRI or SNRI medications under psychiatric guidance.',
         'Seek urgent mental health evaluation if anxiety causes panic attacks, severe functional impairment, or suicidal thoughts.'),

        (62, 'Depressive Symptoms', 'Psychological',
         'An educational screening category for persistent depressed mood, loss of interest or pleasure, low energy, and feelings of worthlessness.',
         'Interactions between genetic vulnerability, neurochemical alterations, neuroendocrine dysregulation (HPA axis), and adverse life events.',
         'Family history of mood disorders, chronic illness, severe interpersonal losses or trauma, chronic lack of social support, sleep disruption.',
         'Regular cardiovascular physical activity, maintaining social connection, structured daily routines, balanced nutrition, exposure to morning daylight.',
         'Psychotherapy (CBT, interpersonal therapy), structured exercise programs, antidepressant pharmacotherapy (SSRIs) supervised by clinicians.',
         'Seek immediate emergency support or call a crisis lifeline (988 in the US) if experiencing thoughts of self-harm or suicide.'),

        (63, 'Chronic Stress & Burnout', 'Psychological',
         'A state of chronic physical and psychological exhaustion coupled with emotional depletion caused by prolonged unmanaged stress.',
         'Sustained activation of the sympathetic-adreno-medullary and hypothalamic-pituitary-adrenal (HPA) axes without adequate recovery phases.',
         'High workload environments, lack of perceived autonomy, caregiver demands, perfectionism, chronic financial strain, insufficient sleep.',
         'Clear personal and professional boundaries, scheduled restorative downtime, peer support systems, regular physical movement, mindfulness.',
         'Workplace/lifestyle restructuring, stress reduction coaching, sleep optimization, mindfulness-based stress reduction (MBSR), clinical counseling.',
         'Seek professional psychological consultation if burnout leads to chronic depressive feelings, severe insomnia, or panic attacks.'),

        (64, 'Insomnia & Sleep Disorder', 'Psychological',
         'A condition characterized by persistent difficulty initiating, consolidating, or maintaining restorative sleep despite adequate opportunity.',
         'Hyperarousal states of the central nervous system, circadian rhythm misalignment, poor sleep ergonomics, psychological distress.',
         'Irregular sleep schedules, shift work, blue light screen use in bed, excessive caffeine/alcohol, chronic anxiety, sleep apnea.',
         'Strict sleep hygiene: consistent sleep-wake schedule, dark/cool/quiet bedroom, avoiding screens 1 hour before bed, limiting caffeine after midday.',
         'Cognitive Behavioral Therapy for Insomnia (CBT-I) as first-line gold standard, stimulus control, sleep restriction therapy, short-term sleep aids.',
         'Consult a sleep specialist or physician if sleep disruption persists over 3 months, causes daytime sleepiness, or is accompanied by loud snoring/gasping.'),

        (65, 'Metabolic Syndrome', 'Endocrine',
         'A clustering of at least three concurrent cardiometabolic risk factors including central obesity, hypertension, hypertriglyceridemia, low HDL, and impaired fasting glucose.',
         'Visceral adiposity-induced chronic low-grade inflammation, adipokine dysregulation, and systemic peripheral insulin resistance.',
         'Sedentary lifestyle, high-carbohydrate refined diet, visceral abdominal obesity, advancing age, genetic predisposition.',
         'Structured Mediterranean-style nutrition, 150 minutes/week moderate aerobic exercise plus resistance training, maintaining waist circumference < 40 in (men) or < 35 in (women).',
         'Intensive therapeutic lifestyle intervention, targeted pharmacological management of individual risk factors (statins, antihypertensives, metformin).',
         'Consult your primary healthcare provider for comprehensive cardiometabolic blood panel screening and personalized prevention planning.')
    ]

    dis_sql = """
    INSERT INTO diseases (id, name, category, short_description, causes, risk_factors, prevention, management, when_to_seek_care)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        category = VALUES(category),
        short_description = VALUES(short_description),
        causes = VALUES(causes),
        risk_factors = VALUES(risk_factors),
        prevention = VALUES(prevention),
        management = VALUES(management),
        when_to_seek_care = VALUES(when_to_seek_care);
    """
    for row in diseases_data:
        cur.execute(dis_sql, row)
    print(f"Upserted {len(diseases_data)} expanded diseases.")

    # 3. EXPAND DISEASE-SYMPTOM MAPPINGS (for all 65 diseases)
    # Map each disease to its primary clinical symptoms
    disease_symptom_relationships = [
        # Original 1-25 verified relationships
        (1, [1, 2, 21, 25, 50, 51]),          # Diabetes: high_blood_sugar, frequent_urination, fatigue, weight_loss, blurred_vision, excessive_hunger
        (2, [3, 11, 29]),                     # Hypertension: high_blood_pressure, headache, dizziness
        (3, [4, 5, 21, 24]),                  # Heart Disease: chest_pain, shortness_of_breath, fatigue, palpitations
        (4, [5, 15, 6, 34]),                  # Asthma: shortness_of_breath, wheezing, cough_with_sputum, dry_cough
        (5, [8, 6, 4, 5, 9]),                 # Pneumonia: fever, cough_with_sputum, chest_pain, shortness_of_breath, chills
        (6, [6, 7, 8, 26, 25]),               # Tuberculosis: cough_with_sputum, hemoptysis, fever, sweats, weight_loss
        (7, [8, 5, 6, 21, 36]),               # COVID-19: fever, shortness_of_breath, cough_with_sputum, fatigue, loss_of_smell
        (8, [8, 9, 11, 10, 21, 46]),          # Influenza: fever, chills, headache, joint_pain, fatigue, muscle_pain
        (9, [8, 10, 11, 21, 27, 40]),         # Dengue: fever, joint_pain, headache, fatigue, nausea, skin_rash
        (10, [8, 9, 26, 11, 27]),             # Malaria: fever, chills, sweats, headache, nausea
        (11, [8, 30, 11, 21, 27, 37]),        # Typhoid: fever, abdominal_pain, headache, fatigue, nausea, diarrhea
        (12, [11, 27, 28, 29]),               # Migraine: headache, nausea, vomiting, dizziness
        (13, [12, 29, 11]),                   # Epilepsy: seizures, dizziness, headache
        (14, [13, 21, 29]),                   # Parkinson's: resting_tremor, fatigue, dizziness
        (15, [14, 21]),                       # Alzheimer's: memory_loss, fatigue
        (16, [5, 6, 15, 21]),                 # COPD: shortness_of_breath, cough_with_sputum, wheezing, fatigue
        (17, [6, 5, 8, 21, 33]),              # Bronchitis: cough_with_sputum, shortness_of_breath, fever, fatigue, sore_throat
        (18, [16, 27, 28, 30]),               # Gastritis: heartburn, nausea, vomiting, abdominal_pain
        (19, [17, 21, 27, 30]),               # Hepatitis: jaundice, fatigue, nausea, abdominal_pain
        (20, [18, 21, 30]),                   # Fatty Liver Disease: right_upper_quadrant_pain, fatigue, abdominal_pain
        (21, [21, 19, 2, 57]),                # Chronic Kidney Disease: fatigue, flank_pain, frequent_urination, leg_swelling
        (22, [20, 2, 19, 8, 58]),             # UTI: dysuria, frequent_urination, flank_pain, fever, blood_in_urine
        (23, [21, 29, 5, 24]),                # Anemia: fatigue, dizziness, shortness_of_breath, palpitations
        (24, [21, 22, 52, 53]),               # Hypothyroidism: fatigue, cold_intolerance, weight_gain, hair_thinning
        (25, [24, 23, 25, 26]),               # Hyperthyroidism: palpitations, heat_intolerance, weight_loss, sweats

        # New 26-65 relationships
        (26, [31, 32, 33, 34]),               # Common Cold: runny_nose, sneezing, sore_throat, dry_cough
        (27, [31, 32, 41, 35]),               # Allergic Rhinitis: runny_nose, sneezing, itching, nasal_congestion
        (28, [35, 11, 6, 8]),                 # Sinusitis: nasal_congestion, headache, cough_with_sputum, fever
        (29, [5, 57, 21, 24]),                # Heart Failure: shortness_of_breath, leg_swelling, fatigue, palpitations
        (30, [24, 29, 5, 4]),                 # Arrhythmia: palpitations, dizziness, shortness_of_breath, chest_pain
        (31, [4, 5, 21]),                     # Angina Pectoris: chest_pain, shortness_of_breath, fatigue
        (32, [46, 49, 21]),                   # Peripheral Artery Disease: muscle_pain, numbness_tingling, fatigue
        (33, [1, 2, 21]),                     # Prediabetes: high_blood_sugar, frequent_urination, fatigue
        (34, [5, 21, 10, 52]),                # Obesity: shortness_of_breath, fatigue, joint_pain, weight_gain
        (35, [52, 43, 53, 21]),               # PCOS: weight_gain, acne_breakouts, hair_thinning, fatigue
        (36, [16, 30, 27, 33]),               # GERD: heartburn, abdominal_pain, nausea, sore_throat
        (37, [30, 16, 27, 28]),               # Peptic Ulcer Disease: abdominal_pain, heartburn, nausea, vomiting
        (38, [37, 28, 30, 8, 27]),            # Gastroenteritis: diarrhea, vomiting, abdominal_pain, fever, nausea
        (39, [30, 39, 37, 38]),               # IBS: abdominal_pain, bloating, diarrhea, constipation
        (40, [38, 39, 30]),                   # Chronic Constipation: constipation, bloating, abdominal_pain
        (41, [37, 30, 21, 27]),               # Chronic Diarrhea: diarrhea, abdominal_pain, fatigue, nausea
        (42, [18, 30, 27, 28]),               # Gallstones: right_upper_quadrant_pain, abdominal_pain, nausea, vomiting
        (43, [11, 46, 21]),                   # Tension Headache: headache, muscle_pain, fatigue
        (44, [49, 46, 21]),                   # Peripheral Neuropathy: numbness_tingling, muscle_pain, fatigue
        (45, [19, 20, 58, 27]),               # Kidney Stones: flank_pain, dysuria, blood_in_urine, nausea
        (46, [8, 9, 19, 20]),                 # Kidney Infection: fever, chills, flank_pain, dysuria
        (47, [43, 40]),                       # Acne Vulgaris: acne_breakouts, skin_rash
        (48, [41, 40, 42]),                   # Eczema: itching, skin_rash, skin_flaking
        (49, [40, 42, 10]),                   # Psoriasis: skin_rash, skin_flaking, joint_pain
        (50, [40, 41, 45]),                   # Contact Dermatitis: skin_rash, itching, localized_swelling
        (51, [41, 40, 42]),                   # Fungal Skin Infection: itching, skin_rash, skin_flaking
        (52, [44, 41, 45]),                   # Urticaria (Hives): hives_welts, itching, localized_swelling
        (53, [10, 48]),                       # Osteoarthritis: joint_pain, joint_stiffness
        (54, [10, 48, 45, 21]),               # Rheumatoid Arthritis: joint_pain, joint_stiffness, localized_swelling, fatigue
        (55, [47, 10]),                       # Osteoporosis: back_pain, joint_pain
        (56, [10, 45, 40]),                   # Gout: joint_pain, localized_swelling, skin_rash
        (57, [46, 45, 47]),                   # Muscle Strain: muscle_pain, localized_swelling, back_pain
        (58, [21, 49, 29, 14]),               # Vitamin B12 Deficiency: fatigue, numbness_tingling, dizziness, memory_loss
        (59, [21, 10, 46, 55]),               # Vitamin D Deficiency: fatigue, joint_pain, muscle_pain, depressed_mood
        (60, [10, 21, 5, 8]),                 # Sickle Cell Disease: joint_pain, fatigue, shortness_of_breath, fever
        (61, [54, 24, 56, 46]),               # Generalized Anxiety: anxiety_nervousness, palpitations, sleep_disturbance, muscle_pain
        (62, [55, 21, 56, 25]),               # Depressive Symptoms: depressed_mood, fatigue, sleep_disturbance, weight_loss
        (63, [21, 11, 56, 54]),               # Chronic Stress & Burnout: fatigue, headache, sleep_disturbance, anxiety_nervousness
        (64, [56, 21, 11]),                   # Insomnia: sleep_disturbance, fatigue, headache
        (65, [1, 3, 52, 21])                  # Metabolic Syndrome: high_blood_sugar, high_blood_pressure, weight_gain, fatigue
    ]

    map_sql = "INSERT IGNORE INTO disease_symptoms (disease_id, symptom_id) VALUES (%s, %s)"
    mapping_count = 0
    for dis_id, sym_ids in disease_symptom_relationships:
        for sym_id in sym_ids:
            cur.execute(map_sql, (dis_id, sym_id))
            mapping_count += 1
    print(f"Ensured {mapping_count} symptom-disease mappings.")

    conn.commit()

    # Final verification counts
    cur.execute("SELECT COUNT(*) FROM diseases")
    num_dis = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM symptoms")
    num_sym = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM disease_symptoms")
    num_map = cur.fetchone()[0]

    print(f"\nMigration successful!")
    print(f"Database 'ai_healthcare' now contains:")
    print(f"  - Diseases: {num_dis} (Expected: 65)")
    print(f"  - Symptoms: {num_sym} (Expected: 58)")
    print(f"  - Relationships: {num_map}")

    conn.close()

if __name__ == '__main__':
    run_migration()
