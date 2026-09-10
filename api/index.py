import os
import sys
import json
import secrets
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.prediction.predict import predict_disease, predict_symptoms
from ml.vision.scanner import compute_vision_metrics
import base64
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Prevent caching on Vercel
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

DISEASES_DB = [
    {"id": 1, "name": "Diabetes", "category": "Endocrine", "short_description": "A chronic metabolic disease characterized by elevated blood glucose levels leading to vascular and organ complications.", "causes": "Insulin resistance or insufficient insulin production by pancreatic beta cells.", "risk_factors": "Obesity, physical inactivity, genetic predisposition, high-refined sugar diets.", "prevention": "Maintain healthy body weight, engage in 150 mins/week exercise, consume fiber-rich foods.", "management": "Blood glucose monitoring, dietary management, insulin therapy under physician guidance.", "when_to_seek_care": "Seek immediate care for severe confusion, rapid breathing, or blood glucose > 300 mg/dL."},
    {"id": 2, "name": "Hypertension", "category": "Cardiovascular", "short_description": "Long-term high blood pressure against arterial walls causing increased cardiac workload.", "causes": "Arterial stiffening, genetic factors, excessive sodium intake, renal dysfunction.", "risk_factors": "High sodium diet, chronic stress, smoking, excessive alcohol, family history.", "prevention": "Reduce salt intake, exercise regularly, manage stress, avoid tobacco.", "management": "Periodic blood pressure tracking, DASH diet, anti-hypertensive medications.", "when_to_seek_care": "Seek urgent care for blood pressure > 180/120 mm Hg or sudden severe headache/chest pain."},
    {"id": 3, "name": "Heart Disease", "category": "Cardiovascular", "short_description": "Range of cardiac conditions including coronary artery disease and heart muscle dysfunction.", "causes": "Atherosclerotic plaque accumulation narrowing coronary arteries.", "risk_factors": "High cholesterol, smoking, diabetes, hypertension, sedentary lifestyle.", "prevention": "Cardio-healthy diet, smoking cessation, lipid monitoring, regular physical activity.", "management": "Cardiac rehabilitation, lipid-lowering medication, lifestyle modification.", "when_to_seek_care": "Seek emergency care immediately for crushing chest pain, arm radiation, or severe shortness of breath."},
    {"id": 4, "name": "Asthma", "category": "Respiratory", "short_description": "Chronic inflammatory disease of airway passages causing episodic wheezing and bronchospasm.", "causes": "Environmental allergens, airway hyper-responsiveness, respiratory viral infections.", "risk_factors": "Family history, allergen exposure, air pollution, secondhand smoke.", "prevention": "Identify and avoid allergen triggers, use prophylactic inhalers as directed.", "management": "Inhaled corticosteroids, quick-relief bronchodilators, asthma action plan.", "when_to_seek_care": "Seek emergency care for severe chest tightness, inability to speak full sentences, or blue lips."},
    {"id": 5, "name": "Pneumonia", "category": "Respiratory", "short_description": "Inflammatory infection of pulmonary alveoli filled with fluid or purulent exudate.", "causes": "Bacterial (Streptococcus pneumoniae), viral (Influenza, RSV), or fungal pathogens.", "risk_factors": "Advanced age, immunocompromised status, chronic lung disease, smoking.", "prevention": "Pneumococcal vaccination, annual flu vaccine, hand hygiene.", "management": "Targeted antibiotic or antiviral therapy, adequate hydration, fever management.", "when_to_seek_care": "Seek urgent medical attention for high fever, chest pain during breathing, or severe oxygen drop."},
    {"id": 6, "name": "Tuberculosis", "category": "Respiratory / Infectious", "short_description": "Contagious bacterial infection affecting pulmonary tissue caused by Mycobacterium tuberculosis.", "causes": "Inhalation of airborne droplet nuclei containing M. tuberculosis.", "risk_factors": "Immunosuppression (HIV), close contact with active TB cases, malnutrition.", "prevention": "BCG vaccination where indicated, infection control in crowded environments.", "management": "Strict 6-month anti-tubercular drug regimen (DOTS protocol).", "when_to_seek_care": "Seek immediate evaluation for coughing up blood, persistent night sweats, or unexplained weight loss."},
    {"id": 7, "name": "COVID-19", "category": "Respiratory / Infectious", "short_description": "Acute infectious disease caused by the SARS-CoV-2 coronavirus variant.", "causes": "Respiratory transmission of SARS-CoV-2 viral particles.", "risk_factors": "Unvaccinated status, older age, underlying pulmonary/cardiac comorbidities.", "prevention": "Vaccination, indoor ventilation, mask usage during outbreaks, hand hygiene.", "management": "Symptomatic control, hydration, antiviral drugs for high-risk patients.", "when_to_seek_care": "Seek emergency care for persistent chest pressure, oxygen saturation < 94%, or confusion."},
    {"id": 8, "name": "Influenza", "category": "Respiratory / Infectious", "short_description": "Acute viral infection of upper and lower respiratory tracts caused by influenza viruses.", "causes": "Infection by Influenza A or B viral strains.", "risk_factors": "Seasonal outbreaks, immunocompromised health, extreme ages.", "prevention": "Annual influenza vaccination, hand washing, avoiding close contact with sick persons.", "management": "Rest, fluid intake, antiviral treatment (Oseltamivir) within 48 hours of onset.", "when_to_seek_care": "Seek medical attention if fever persists over 4 days or severe breathing difficulty develops."},
    {"id": 9, "name": "Dengue", "category": "Infectious / Tropical", "short_description": "Mosquito-borne viral infection causing severe flu-like illness and low blood platelets.", "causes": "Transmission of Dengue virus (DENV-1-4) by infected Aedes aegypti mosquitoes.", "risk_factors": "Living in tropical endemic areas, standing water reservoirs.", "prevention": "Mosquito repellent usage, eliminating standing water containers, wearing long clothing.", "management": "Supportive care, continuous hydration, monitoring blood platelet count.", "when_to_seek_care": "Seek emergency care for severe abdominal pain, persistent vomiting, or mucosal bleeding."},
    {"id": 10, "name": "Malaria", "category": "Infectious / Tropical", "short_description": "Life-threatening parasitic infection transmitted by female Anopheles mosquitoes.", "causes": "Plasmodium parasite infection (P. falciparum, P. vivax).", "risk_factors": "Travel to endemic tropical regions, lack of bednet protection.", "prevention": "Prophylactic antimalarial medication, insecticide-treated mosquito nets.", "management": "Artemisinin-based combination therapies (ACT) prescribed by physicians.", "when_to_seek_care": "Seek immediate medical attention for high cyclical fever, severe chills, or jaundice."},
    {"id": 11, "name": "Typhoid", "category": "Infectious / Gastrointestinal", "short_description": "Systemic bacterial fever caused by Salmonella enterica serovar Typhi.", "causes": "Ingestion of food or water contaminated with S. Typhi bacteria.", "risk_factors": "Poor sanitation, unhygienic street food, lack of clean drinking water.", "prevention": "Typhoid vaccination, drinking boiled/filtered water, hygienic food preparation.", "management": "Targeted oral/intravenous antibiotics and fever control.", "when_to_seek_care": "Seek medical care for continuous high fever, Rose spots on abdomen, or severe lethargy."},
    {"id": 12, "name": "Migraine", "category": "Neurological", "short_description": "Recurrent neurological headache disorder characterized by moderate-to-severe throbbing pain.", "causes": "Neurovascular reactivity, trigeminal nerve activation, serotonin level fluctuations.", "risk_factors": "Stress, hormonal changes, sleep disruption, dietary triggers (caffeine, monosodium glutamate).", "prevention": "Maintain consistent sleep schedules, stress reduction, trigger diary tracking.", "management": "Acute triptan therapy, preventive medications, dark room rest.", "when_to_seek_care": "Seek urgent evaluation for a sudden \"thunderclap\" headache or accompanied facial numbness/weakness."},
    {"id": 13, "name": "Epilepsy", "category": "Neurological", "short_description": "Central nervous system disorder characterized by recurrent unprovoked electrical seizures.", "causes": "Abnormal brain electrical activity due to genetics, head trauma, stroke, or structural brain lesions.", "risk_factors": "Family history, prior head injury, central nervous system infections.", "prevention": "Head injury prevention (helmets), consistent medication adherence.", "management": "Antiepileptic drugs (AEDs), regular neurological monitoring.", "when_to_seek_care": "Seek emergency services if a seizure lasts longer than 5 minutes or consecutive seizures occur."},
    {"id": 14, "name": "Parkinson's Disease", "category": "Neurological", "short_description": "Progressive neurodegenerative disorder characterized by loss of dopamine-producing brain cells.", "causes": "Degeneration of substantia nigra dopaminergic neurons, alpha-synuclein accumulation.", "risk_factors": "Advanced age, male sex, pesticide/environmental toxin exposure.", "prevention": "Regular aerobic exercise, neuroprotective lifestyle habits.", "management": "Levodopa/Carbidopa medication, physical therapy, occupational assistance.", "when_to_seek_care": "Seek medical advice upon noticing resting hand tremors, muscle rigidity, or gait disturbance."},
    {"id": 15, "name": "Alzheimer's Disease", "category": "Neurological", "short_description": "Progressive neurodegenerative disease causing memory impairment and cognitive decline.", "causes": "Accumulation of extracellular amyloid-beta plaques and intracellular tau tangles.", "risk_factors": "Age over 65, APOE-e4 gene variant, cardiovascular comorbidities, low cognitive reserve.", "prevention": "Cardiovascular health management, lifelong mental stimulation, Mediterranean diet.", "management": "Cholinesterase inhibitors, supportive cognitive care, safety modifications.", "when_to_seek_care": "Seek neurological assessment for progressive short-term memory loss interfering with daily living."},
    {"id": 16, "name": "COPD", "category": "Respiratory", "short_description": "Progressive airflow limitation caused by emphysema and chronic bronchitis.", "causes": "Long-term exposure to irritating gases, primarily cigarette smoke or biomass fuel.", "risk_factors": "Cigarette smoking, occupational dust exposure, alpha-1 antitrypsin deficiency.", "prevention": "Complete smoking cessation, avoiding workplace respiratory irritants.", "management": "Inhaled bronchodilators, pulmonary rehabilitation, supplemental oxygen therapy.", "when_to_seek_care": "Seek immediate emergency care for acute exacerbation with severe breathlessness and cyanosis."},
    {"id": 17, "name": "Bronchitis", "category": "Respiratory", "short_description": "Inflammation of bronchial mucosal lining leading to productive cough.", "causes": "Viral respiratory infections (rhinovirus, influenza) or acute chemical irritants.", "risk_factors": "Smoking exposure, air pollution, weakened immune defense.", "prevention": "Avoid smoking exposure, practice hand hygiene, get vaccinated.", "management": "Expectorants, hydration, rest, avoiding respiratory irritants.", "when_to_seek_care": "Seek medical consultation if cough persists over 3 weeks or sputum contains blood."},
    {"id": 18, "name": "Gastritis", "category": "Gastrointestinal", "short_description": "Inflammation or erosion of the protective gastric mucosal lining.", "causes": "Helicobacter pylori bacterial infection, chronic NSAID use, excessive alcohol.", "risk_factors": "Frequent painkiller use, severe physiological stress, H. pylori exposure.", "prevention": "Limit NSAID usage, avoid excessive alcohol and spicy trigger foods.", "management": "Proton pump inhibitors (PPIs), antacids, H. pylori antibiotic eradication.", "when_to_seek_care": "Seek immediate medical care for vomiting blood, dark tarry stools, or severe stomach pain."},
    {"id": 19, "name": "Hepatitis", "category": "Gastrointestinal / Hepatic", "short_description": "Inflammation of liver tissue caused primarily by viral pathogens or toxins.", "causes": "Hepatitis viruses (A, B, C, D, E), heavy alcohol consumption, autoimmune reactions.", "risk_factors": "Unprotected exposure to bodily fluids, contaminated water, heavy alcohol intake.", "prevention": "Hepatitis A & B vaccination, safe needle protocols, clean water consumption.", "management": "Antiviral medications, supportive liver care, complete alcohol abstinence.", "when_to_seek_care": "Seek urgent medical attention for yellowing skin/eyes (jaundice) or dark brown urine."},
    {"id": 20, "name": "Fatty Liver Disease", "category": "Gastrointestinal / Hepatic", "short_description": "Excessive accumulation of triglycerides within hepatic cells (steatosis).", "causes": "Metabolic dysfunction, insulin resistance, high fructose intake, heavy alcohol consumption.", "risk_factors": "Obesity, type 2 diabetes, high cholesterol, metabolic syndrome.", "prevention": "Weight reduction (7-10%), low-carb diet, regular aerobic exercise.", "management": "Dietary modification, lifestyle intervention, managing blood glucose.", "when_to_seek_care": "Seek medical evaluation if experiencing persistent right upper quadrant abdominal discomfort."},
    {"id": 21, "name": "Chronic Kidney Disease", "category": "Renal", "short_description": "Gradual loss of renal filtration function over months to years.", "causes": "Uncontrolled diabetes mellitus, long-standing hypertension, glomerulonephritis.", "risk_factors": "Diabetes, hypertension, family history of renal disease, prolonged NSAID use.", "prevention": "Strict blood sugar and blood pressure control, avoiding nephrotoxic drugs.", "management": "Renoprotective medications (ACE inhibitors), renal diet, dialysis in advanced stages.", "when_to_seek_care": "Seek medical evaluation for swelling in legs/ankles, decreased urine output, or persistent nausea."},
    {"id": 22, "name": "Urinary Tract Infection (UTI)", "category": "Renal / Urological", "short_description": "Infection of urinary structures, most commonly the urinary bladder (cystitis).", "causes": "Bacterial colonization (Escherichia coli) ascending through urethra into urinary bladder.", "risk_factors": "Female anatomy, sexual activity, urinary catheterization, inadequate hydration.", "prevention": "Adequate fluid intake, voiding after intercourse, maintaining personal hygiene.", "management": "Targeted antibiotic therapy, increased water intake.", "when_to_seek_care": "Seek urgent medical attention if experiencing high fever, flank/back pain, or severe chills."},
    {"id": 23, "name": "Anemia", "category": "Hematological", "short_description": "Deficiency in healthy red blood cells or hemoglobin concentration impaired oxygen delivery.", "causes": "Iron deficiency, vitamin B12/folate deficiency, chronic blood loss, bone marrow failure.", "risk_factors": "Inadequate iron diet, heavy menstrual bleeding, gastrointestinal bleeding.", "prevention": "Iron-rich balanced diet (leafy greens, meat), vitamin C intake.", "management": "Iron/vitamin supplementation, addressing underlying blood loss cause.", "when_to_seek_care": "Seek immediate care for severe shortness of breath, dizziness upon standing, or chest tightness."},
    {"id": 24, "name": "Hypothyroidism", "category": "Endocrine", "short_description": "Underactive thyroid gland producing insufficient thyroid hormones (T3/T4).", "causes": "Hashimoto autoimmune thyroiditis, thyroidectomy, iodine deficiency.", "risk_factors": "Female sex, middle age, autoimmune conditions, personal history of radiation.", "prevention": "Adequate dietary iodine intake, periodic TSH screening.", "management": "Daily levothyroxine hormone replacement therapy.", "when_to_seek_care": "Seek medical review for progressive unexplained weight gain, extreme fatigue, or cold intolerance."},
    {"id": 25, "name": "Hyperthyroidism", "category": "Endocrine", "short_description": "Overactive thyroid gland producing excessive thyroid hormones.", "causes": "Graves autoimmune disease, toxic multinodular goiter, thyroiditis.", "risk_factors": "Female sex, family history of Graves disease, high iodine exposure.", "prevention": "Regular thyroid monitoring, stress management.", "management": "Anti-thyroid medications (Methimazole), beta-blockers, radioactive iodine.", "when_to_seek_care": "Seek immediate medical attention for rapid irregular heart rate (palpitations) or severe tremors."},
    {"id": 26, "name": "Common Cold", "category": "Respiratory", "short_description": "A mild viral infectious disease of the upper respiratory tract primarily affecting the nasal mucosa and throat.", "causes": "Rhinoviruses, coronaviruses, adenoviruses, or enteroviruses.", "risk_factors": "Exposure to infected individuals, seasonal winter changes, psychological stress, sleep deprivation.", "prevention": "Frequent hand hygiene, avoiding touching facial mucous membranes, maintaining adequate hydration and rest.", "management": "Rest, oral hydration, warm saline gargles, over-the-counter decongestants or analgesics as appropriate.", "when_to_seek_care": "Seek medical care if symptoms persist beyond 10-14 days, high fever develops, or wheezing occurs."},
    {"id": 27, "name": "Allergic Rhinitis", "category": "Respiratory", "short_description": "Inflammation of the interior nasal passages caused by an IgE-mediated allergic response to inhaled environmental allergens.", "causes": "Inhaled allergens including tree/grass pollen, house dust mites, animal dander, and fungal spores.", "risk_factors": "Atopic genetic predisposition, family history of asthma or eczema, high environmental allergen exposure.", "prevention": "Minimize exposure to identified allergens, use HEPA filtration, keep windows closed during high pollen counts.", "management": "Nasal corticosteroid sprays, oral second-generation antihistamines, saline nasal rinses, allergen immunotherapy.", "when_to_seek_care": "Seek evaluation if chronic nasal obstruction causes secondary sinusitis or impairs quality of sleep."},
    {"id": 28, "name": "Sinusitis", "category": "Respiratory", "short_description": "Inflammation or infection of the mucosal lining of the paranasal sinuses, causing facial pressure and nasal congestion.", "causes": "Secondary bacterial infection following viral upper respiratory infection, allergic swelling, or anatomical nasal polyps.", "risk_factors": "Recent viral cold, allergic rhinitis, structural deviated septum, environmental smoke exposure.", "prevention": "Prompt management of colds and allergies, indoor humidification, nasal saline irrigation.", "management": "Nasal saline irrigation, decongestants, intranasal steroids, oral antibiotics if bacterial infection confirmed.", "when_to_seek_care": "Seek urgent medical care if experiencing severe headache, periorbital swelling, vision changes, or high fever."},
    {"id": 29, "name": "Heart Failure", "category": "Cardiovascular", "short_description": "A chronic, progressive condition in which the cardiac muscle is unable to pump sufficient blood volume to meet systemic metabolic demands.", "causes": "Long-standing hypertension, prior myocardial infarction, coronary artery disease, cardiomyopathy, or valvular heart disease.", "risk_factors": "Hypertension, history of heart attack, diabetes, obesity, smoking, excessive alcohol consumption.", "prevention": "Strict blood pressure control, coronary disease prevention, smoking cessation, low-sodium dietary habits.", "management": "ACE inhibitors/ARNs, beta-blockers, aldosterone antagonists, SGLT2 inhibitors, diuretics, fluid restriction, daily weight tracking.", "when_to_seek_care": "Seek immediate emergency care for sudden severe breathlessness, inability to lie flat, or rapid unexplained weight gain (>3 lbs in 24h)."},
    {"id": 30, "name": "Arrhythmia", "category": "Cardiovascular", "short_description": "Disruptions or irregularities in the electrical conduction system of the heart, resulting in bradycardia, tachycardia, or fibrillatory rhythm.", "causes": "Ischemic heart disease, electrolyte imbalances, structural cardiac remodeling, caffeine, thyroid disease, or electrical channelopathies.", "risk_factors": "Underlying coronary disease, hypertension, electrolyte disturbances (potassium/magnesium), sleep apnea, stimulant use.", "prevention": "Limit caffeine and alcohol, avoid illicit stimulants, manage stress, monitor electrolyte balance.", "management": "Anti-arrhythmic medications, rate-control agents (beta-blockers), catheter ablation, cardioversion, pacemakers or ICDs.", "when_to_seek_care": "Seek immediate emergency medical care for palpitations accompanied by syncope, chest pain, or severe dizziness."},
    {"id": 31, "name": "Angina Pectoris", "category": "Cardiovascular", "short_description": "Reversible chest pain or pressure resulting from transient myocardial ischemia due to inadequate coronary blood flow.", "causes": "Atherosclerotic coronary artery stenosis restricting oxygen delivery during times of increased myocardial workload.", "risk_factors": "Coronary artery disease, hypertension, dyslipidemia, smoking, diabetes, sedentary lifestyle.", "prevention": "Manage cardiovascular risk factors, adhere to Mediterranean-style diet, smoking cessation, regular moderate exercise.", "management": "Sublingual nitroglycerin for acute episodes, beta-blockers, calcium channel blockers, statins, antiplatelet therapy.", "when_to_seek_care": "Seek emergency medical services immediately if chest pain lasts longer than 10 minutes or does not resolve with rest and nitroglycerin."},
    {"id": 32, "name": "Peripheral Artery Disease", "category": "Cardiovascular", "short_description": "A circulatory condition in which atherosclerotic plaque narrows peripheral arteries, severely reducing blood flow to the limbs.", "causes": "Systemic atherosclerosis affecting the abdominal aorta, iliac, femoral, and popliteal arterial branches.", "risk_factors": "Cigarette smoking, type 2 diabetes, chronic hypertension, advanced age, hypercholesterolemia.", "prevention": "Smoking cessation, routine walking exercise programs, glycemic and lipid control, blood pressure optimization.", "management": "Supervised exercise therapy, antiplatelet medications (aspirin/clopidogrel), statin therapy, cilostazol, endovascular revascularization.", "when_to_seek_care": "Seek urgent care for resting foot pain, cold/pale extremities, or non-healing ulcers on the lower extremities."},
    {"id": 33, "name": "Prediabetes", "category": "Endocrine", "short_description": "A metabolic state where blood glucose levels are above normal ranges (HbA1c 5.7-6.4%) but not yet meeting the threshold for type 2 diabetes.", "causes": "Progressive peripheral insulin resistance coupled with relative pancreatic beta-cell secretory compensation.", "risk_factors": "Overweight/obesity (BMI > 25), physical inactivity, age > 45, family history of type 2 diabetes, gestational diabetes history.", "prevention": "Structured lifestyle interventions: 7% sustained weight reduction, 150 minutes/week moderate physical exercise, whole-food diet.", "management": "Intensive dietary modification, aerobic and resistance training, routine HbA1c monitoring every 6-12 months, metformin where indicated.", "when_to_seek_care": "Consult a physician for routine screening if persistent fatigue, increased thirst, or unexplained weight shifts occur."},
    {"id": 34, "name": "Obesity", "category": "Endocrine", "short_description": "A complex, chronic multifactorial disease characterized by excessive adiposity that impairs physical and metabolic health.", "causes": "Energy imbalance between caloric consumption and metabolic expenditure, neuroendocrine appetite regulation dysregulation, genetics.", "risk_factors": "Sedentary lifestyle, high-density refined food availability, endocrine disruptors, chronic sleep disruption, genetic susceptibility.", "prevention": "Whole-food dietary patterns, regular daily physical activity, stress mitigation, adequate sleep, behavioral health support.", "management": "Comprehensive lifestyle therapy, medical nutritional therapy, pharmacotherapy (GLP-1 receptor agonists), bariatric metabolic surgery.", "when_to_seek_care": "Seek healthcare consultation when excess weight contributes to joint pain, obstructive sleep apnea, or metabolic dysregulation."},
    {"id": 35, "name": "Polycystic Ovary Syndrome (PCOS)", "category": "Endocrine", "short_description": "A prevalent endocrine disorder in reproductive-aged females characterized by ovulatory dysfunction, hyperandrogenism, and polycystic ovarian morphology.", "causes": "Complex genetic, neuroendocrine, and metabolic factors with underlying hyperinsulinemia and ovarian theca-cell androgen overproduction.", "risk_factors": "Family history of PCOS, insulin resistance, metabolic syndrome, obesity, sedentary lifestyle.", "prevention": "Weight management, low-glycemic dietary habits, regular physical activity to enhance peripheral insulin sensitivity.", "management": "Combined oral contraceptives, metformin for insulin resistance, lifestyle modification, anti-androgens (spironolactone), ovulation induction.", "when_to_seek_care": "Consult a gynecologist or endocrinologist for irregular menstrual cycles, severe cystic acne, or difficulty conceiving."},
    {"id": 36, "name": "GERD (Acid Reflux)", "category": "Gastrointestinal", "short_description": "A chronic gastrointestinal disorder where stomach acid persistently refluxes backward into the esophagus, irritating the mucosal lining.", "causes": "Transient lower esophageal sphincter (LES) relaxations, hiatal hernia, delayed gastric emptying, increased intra-abdominal pressure.", "risk_factors": "Obesity, pregnancy, hiatal hernia, smoking, late-night heavy meals, consumption of fatty, spicy, citrus, or caffeinated foods.", "prevention": "Elevate head of bed, avoid recumbency within 3 hours of meals, lose excess weight, avoid trigger foods, stop smoking.", "management": "Proton pump inhibitors (PPIs), H2-receptor antagonists, antacids, lifestyle modifications, endoscopic or surgical fundoplication.", "when_to_seek_care": "Seek prompt evaluation for progressive dysphagia (trouble swallowing), unintentional weight loss, hematemesis, or anemia."},
    {"id": 37, "name": "Peptic Ulcer Disease", "category": "Gastrointestinal", "short_description": "Erosive mucosal lesions occurring in the protective inner lining of the stomach (gastric ulcer) or proximal small intestine (duodenal ulcer).", "causes": "Helicobacter pylori bacterial colonization, chronic usage of nonsteroidal anti-inflammatory drugs (NSAIDs), hyperacidity.", "risk_factors": "H. pylori infection, regular NSAID or aspirin use, smoking, heavy alcohol consumption, severe physiological stress.", "prevention": "Eradicate H. pylori, minimize unprescribed NSAID use, co-prescribe gastroprotection (PPIs) when chronic NSAIDs are required, avoid smoking.", "management": "Antibiotic eradication therapy for H. pylori, proton pump inhibitors, mucosal protective agents, avoiding mucosal irritants.", "when_to_seek_care": "Seek immediate emergency evaluation for vomiting frank blood or coffee-ground emesis, black tarry stools, or sudden acute abdominal pain."},
    {"id": 38, "name": "Gastroenteritis", "category": "Gastrointestinal", "short_description": "An acute inflammation of the gastrointestinal tract mucous membranes, involving both stomach and small intestine.", "causes": "Viral pathogens (Norovirus, Rotavirus), bacterial toxins (Salmonella, Campylobacter, E. coli), or parasitic protozoa.", "risk_factors": "Consumption of contaminated water or unpasteurized food, poor hand hygiene, crowded living conditions, international travel.", "prevention": "Meticulous hand washing with soap and water, hygienic food storage and preparation, drinking clean treated water, rotavirus vaccination.", "management": "Oral rehydration therapy with balanced electrolyte solutions, gradual reintroduction of bland diet, zinc supplementation, antiemetics if needed.", "when_to_seek_care": "Seek urgent care if signs of dehydration emerge (sunken eyes, dizziness, absence of urination), bloody stool, or inability to tolerate liquids."},
    {"id": 39, "name": "Irritable Bowel Syndrome (IBS)", "category": "Gastrointestinal", "short_description": "A common disorder of the brain-gut interaction characterized by recurrent abdominal pain related to defecation or changes in bowel habits.", "causes": "Visceral hypersensitivity, altered gut-brain communication, gastrointestinal dysmotility, post-infectious inflammation, altered gut microbiome.", "risk_factors": "Female sex, severe preceding bacterial gastroenteritis, chronic psychological stress, early adverse life events.", "prevention": "Stress reduction, identifying individual food triggers, regular meal patterns, adequate dietary fiber and hydration.", "management": "Low-FODMAP dietary trial, soluble fiber (psyllium), antispasmodics, neuromodulators, gut-directed cognitive behavioral therapy.", "when_to_seek_care": "Seek medical assessment for \"red flag\" symptoms: nocturnal symptoms, unintended weight loss, rectal bleeding, or onset after age 50."},
    {"id": 40, "name": "Chronic Constipation", "category": "Gastrointestinal", "short_description": "A functional gastrointestinal condition marked by infrequent, difficult, or incomplete evacuation of dry, hardened stool.", "causes": "Inadequate dietary fiber, insufficient hydration, pelvic floor dyssynergia, slow transit colonic motility, side effect of medications.", "risk_factors": "Low-fiber diet, sedentary lifestyle, suppressing the urge to defecate, medications (opioids, calcium channel blockers, iron supplements).", "prevention": "High-fiber diet (25-35 grams/day), plentiful fluid intake, regular physical activity, establishing consistent toilet routines.", "management": "Bulk-forming laxatives (psyllium), osmotic laxatives (polyethylene glycol), pelvic floor physical therapy, biofeedback.", "when_to_seek_care": "Consult a physician if constipation is accompanied by severe abdominal distension, vomiting, rectal bleeding, or sudden onset in older adults."},
    {"id": 41, "name": "Chronic Diarrhea", "category": "Gastrointestinal", "short_description": "Frequent loose, watery stools persisting continuously or intermittently for greater than four weeks in duration.", "causes": "Inflammatory bowel disease (Crohn's/Colitis), celiac disease, malabsorption syndromes, chronic parasitic infection, microscopic colitis.", "risk_factors": "Autoimmune history, family history of IBD or celiac disease, prior gastrointestinal surgeries, chronic antibiotic or metformin use.", "prevention": "Prompt investigation of dietary intolerances (gluten, lactose), hygienic water sources during travel, cautious antibiotic usage.", "management": "Etiology-specific treatment (gluten-free diet for celiac, anti-inflammatory therapy for IBD), electrolyte replenishment, anti-diarrheal agents.", "when_to_seek_care": "Seek thorough clinical evaluation for chronic diarrhea accompanied by unintended weight loss, fever, anemia, or visible blood in stool."},
    {"id": 42, "name": "Gallstones", "category": "Gastrointestinal", "short_description": "Hardened mineral deposits formed inside the gallbladder, predominantly composed of crystallized cholesterol or bilirubin pigments.", "causes": "Supersaturation of bile with cholesterol, gallbladder hypomotility, excessive biliary bilirubin secretion.", "risk_factors": "Female sex, age > 40, multiparity, rapid weight loss, obesity, high-fat diet, hemolytic blood disorders.", "prevention": "Maintain a healthy body weight gradually (avoid crash starvation diets), eat a balanced fiber-rich diet with healthy unsaturated fats.", "management": "Observation for asymptomatic stones; laparoscopic cholecystectomy for symptomatic recurrent biliary colic or acute cholecystitis.", "when_to_seek_care": "Seek emergency medical evaluation for severe right upper quadrant pain radiating to shoulder, fever, persistent vomiting, or jaundice."},
    {"id": 43, "name": "Tension Headache", "category": "Neurological", "short_description": "The most prevalent type of primary headache, presenting as mild-to-moderate dull, band-like tightening pressure across the head and neck.", "causes": "Myofascial trigger points, pericranial muscle tenderness, central pain sensitization, prolonged emotional stress.", "risk_factors": "Chronic emotional or occupational stress, poor ergonomic posture, ocular strain, clenching jaw/teeth, sleep deprivation.", "prevention": "Regular ergonomic breaks, adequate nocturnal sleep, stress management, hydration, stretching of cervical and shoulder muscles.", "management": "Over-the-counter analgesics (acetaminophen, NSAIDs), physical therapy, stress management techniques, tricyclic antidepressants for chronic cases.", "when_to_seek_care": "Seek evaluation for sudden severe \"thunderclap\" headache, new headaches after age 50, or associated focal neurological deficits."},
    {"id": 44, "name": "Peripheral Neuropathy", "category": "Neurological", "short_description": "Damage to the peripheral nervous system leading to weakness, numbness, tingling, or burning sensations primarily in hands and feet.", "causes": "Diabetic microvascular axonal damage, chronic alcoholism, vitamin B12 deficiency, chemotherapy toxicity, autoimmune disorders.", "risk_factors": "Poorly controlled diabetes mellitus, heavy alcohol consumption, chemotherapy treatments, nutritional deficiencies, renal disease.", "prevention": "Strict blood glucose control in diabetes, moderation of alcohol, adequate nutritional vitamin B12 intake, foot protective care.", "management": "Optimization of underlying cause, neuropathic pain agents (gabapentin, pregabalin, duloxetine), physical therapy, daily foot inspections.", "when_to_seek_care": "Seek medical attention for progressive numbness spreading upward, unhealed foot ulcers, or difficulty with balance and walking."},
    {"id": 45, "name": "Kidney Stones", "category": "Renal / Urological", "short_description": "Solid mineral and acid salt crystalline aggregations that form within renal calyces and pass into the urinary tract.", "causes": "Supersaturation of urine with calcium, oxalate, phosphate, or uric acid coupled with inadequate urinary fluid volume.", "risk_factors": "Low fluid intake, high dietary sodium/animal protein, family history of nephrolithiasis, hyperparathyroidism, gout.", "prevention": "Drink 2.5 to 3 liters of water daily to maintain clear dilute urine, limit sodium and excess animal protein, ensure normal calcium intake.", "management": "Adequate hydration, alpha-blockers (tamsulosin) to aid stone passage, oral analgesia, shock-wave lithotripsy or ureteroscopy for large stones.", "when_to_seek_care": "Seek immediate emergency care for intractable flank pain, persistent vomiting, inability to urinate, or high fever with chills."},
    {"id": 46, "name": "Kidney Infection (Pyelonephritis)", "category": "Renal / Urological", "short_description": "An acute bacterial infection of the renal parenchyma and renal pelvis, usually ascending from the lower urinary tract.", "causes": "Ascending spread of uropathogenic bacteria (primarily Escherichia coli) from cystitis through ureters into the kidney.", "risk_factors": "Untreated or recurrent lower urinary tract infections, female anatomy, urinary catheterization, kidney stones, pregnancy, diabetes.", "prevention": "Prompt, complete treatment of bladder infections, generous hydration, post-coital urination, proper perineal hygiene.", "management": "Empirical and culture-directed oral or intravenous antibiotics for 7-14 days, antipyretics, adequate oral or IV fluid hydration.", "when_to_seek_care": "Seek emergency medical care immediately for high fever, severe flank pain, shaking chills, nausea, or confusion."},
    {"id": 47, "name": "Acne Vulgaris", "category": "Dermatological", "short_description": "A chronic inflammatory dermatological disorder of the pilosebaceous units characterized by comedones, papules, pustules, or cysts.", "causes": "Excess sebum production, follicular hyperkeratinization, Cutibacterium acnes bacterial proliferation, and inflammatory mediator release.", "risk_factors": "Adolescent hormonal surges, androgen excess, family history, high-glycemic index diets, comedogenic cosmetic products.", "prevention": "Gentle non-abrasive facial cleansing twice daily, avoiding picking or squeezing lesions, non-comedogenic oil-free skincare.", "management": "Topical retinoids, benzoyl peroxide, topical/oral antibiotics, salicylic acid, hormonal therapies (oral contraceptives, spironolactone), oral isotretinoin.", "when_to_seek_care": "Seek dermatological consultation for painful deep cysts, scarring acne lesions, or lack of response to non-prescription remedies."},
    {"id": 48, "name": "Eczema (Atopic Dermatitis)", "category": "Dermatological", "short_description": "A chronic, pruritic inflammatory skin condition characterized by defective epidermal barrier function and immune dysregulation.", "causes": "Genetic mutations in the filaggrin (FLG) gene, epidermal skin barrier disruption, Th2-skewed immune hyperreactivity.", "risk_factors": "Personal or family history of atopy (asthma, allergic rhinitis), dry climates, frequent bathing with harsh soaps, environmental irritants.", "prevention": "Frequent skin moisturization with bland thick emollient ointments, lukewarm brief baths, fragrance-free detergents, avoiding wool clothing.", "management": "Liberal emollient moisturizers, topical corticosteroids, topical calcineurin inhibitors, phototherapy, biologic therapies (dupilumab).", "when_to_seek_care": "Seek prompt medical attention if eczema lesions exhibit signs of bacterial superinfection (honey-colored crusting, pustules, severe pain)."},
    {"id": 49, "name": "Psoriasis", "category": "Dermatological", "short_description": "A chronic autoimmune inflammatory dermatosis characterized by well-demarcated erythematous plaques covered with silvery micaceous scales.", "causes": "Immune-mediated acceleration of epidermal keratinocyte turnover driven by the IL-23/IL-17 cytokine signaling pathway.", "risk_factors": "Genetic susceptibility (HLA-Cw6), physiological or psychological stress, streptococcal pharyngeal infection, smoking, obesity, alcohol.", "prevention": "Stress reduction, avoiding skin trauma/friction (Koebner phenomenon), maintaining healthy body weight, avoiding smoking and heavy drinking.", "management": "Topical corticosteroids, topical vitamin D analogs, phototherapy (narrowband UVB), systemic methotrexate, biologic targeted agents.", "when_to_seek_care": "Consult a dermatologist for extensive cutaneous involvement, severe discomfort, or associated joint pain (psoriatic arthritis)."},
    {"id": 50, "name": "Contact Dermatitis", "category": "Dermatological", "short_description": "An acute or chronic cutaneous inflammatory reaction elicited by direct contact with an external chemical, allergen, or physical irritant.", "causes": "Either direct cytotoxic irritant injury (Irritant Contact Dermatitis) or delayed Type IV cell-mediated allergy (Allergic Contact Dermatitis).", "risk_factors": "Occupational chemical exposure (hairdressers, healthcare, cleaners), nickel jewelry, poison ivy/oak, fragrance ingredients, topical neomycin.", "prevention": "Identify and rigorously avoid contact with causative allergens or irritants, wear protective barrier gloves, wash skin immediately after accidental exposure.", "management": "Cool wet compresses, topical corticosteroid creams, oral antihistamines for pruritus, barrier repair creams.", "when_to_seek_care": "Seek care if dermatitis affects eyes, face, or genitalia, spreads rapidly, or develops secondary bacterial pustules or cellulitis."},
    {"id": 51, "name": "Fungal Skin Infection", "category": "Dermatological", "short_description": "Superficial fungal colonization of the keratinized layer of skin, hair, or nails caused by dermatophytes or yeasts.", "causes": "Dermatophyte fungi (Trichophyton, Microsporum, Epidermophyton) or Candida albicans yeast proliferating in warm, humid skin folds.", "risk_factors": "Warm humid environments, excessive perspiration, occlusive footwear, communal showers/gyms, diabetes mellitus, compromised immunity.", "prevention": "Keep skin clean and dry, wear breathable cotton clothing, dry thoroughly after bathing, wear sandals in public locker rooms and showers.", "management": "Topical antifungal creams (clotrimazole, terbinafine, miconazole) applied for 2-4 weeks, oral antifungals for widespread or nail infections.", "when_to_seek_care": "Seek medical consultation if fungal rash does not improve after 2 weeks of over-the-counter treatment or spreads extensively."},
    {"id": 52, "name": "Urticaria (Hives)", "category": "Dermatological", "short_description": "A transient vascular reaction of the dermis characterized by intensely pruritic, raised, erythematous wheals with surrounding flare.", "causes": "Mast cell and basophil degranulation with rapid release of histamine and vasodilatory mediators triggered by allergens, infections, or physical stimuli.", "risk_factors": "Viral infections, food allergies (nuts, shellfish), medications (NSAIDs, antibiotics), insect stings, physical stimuli (heat, cold, pressure).", "prevention": "Identify and avoid known specific triggering allergens, minimize physical skin friction, avoid unneeded NSAIDs during acute flares.", "management": "Second-generation H1-antihistamines (cetirizine, fexofenadine, loratadine), H2-blockers, cool compresses, oral corticosteroids for severe flares.", "when_to_seek_care": "Seek immediate emergency care if hives occur with facial/lip/tongue swelling (angioedema), difficulty breathing, or dizziness (anaphylaxis)."},
    {"id": 53, "name": "Osteoarthritis", "category": "Musculoskeletal", "short_description": "A progressive degenerative joint disease characterized by breakdown of articular cartilage, subchondral bone remodeling, and osteophyte formation.", "causes": "Biomechanical joint stress, age-related chondrocyte senescence, repetitive mechanical microtrauma, low-grade joint inflammation.", "risk_factors": "Advanced age, female sex, obesity (excess load on weight-bearing joints), prior traumatic joint injury, repetitive occupational joint stress.", "prevention": "Maintain healthy body weight to reduce knee/hip mechanical loading, engage in low-impact aerobic exercise (swimming, cycling), avoid joint trauma.", "management": "Physical therapy, quadriceps muscle strengthening, weight loss, acetaminophen or topical NSAIDs, intra-articular injections, joint replacement surgery.", "when_to_seek_care": "Consult an orthopedic specialist for progressive joint pain limiting ambulation or daily self-care activities."},
    {"id": 54, "name": "Rheumatoid Arthritis", "category": "Musculoskeletal", "short_description": "A chronic, systemic autoimmune disease characterized by symmetric inflammatory polyarthritis, synovial proliferation, and progressive joint destruction.", "causes": "Autoimmune targeting of synovial tissue by autoantibodies (Rheumatoid Factor, anti-CCP), leading to chronic pannus formation and cartilage erosion.", "risk_factors": "Female sex, genetic predisposition (HLA-DRB1 alleles), cigarette smoking, family history of autoimmune disease.", "prevention": "Smoking cessation, maintaining optimal dental hygiene, early diagnostic assessment upon onset of symmetric joint swelling.", "management": "Disease-modifying antirheumatic drugs (DMARDs, e.g. methotrexate), biologic TNF/IL-6 inhibitors, short-term corticosteroids, physical therapy.", "when_to_seek_care": "Seek urgent rheumatology evaluation within weeks of developing persistent symmetric joint swelling, morning stiffness > 1 hour, or hand deformities."},
    {"id": 55, "name": "Osteoporosis", "category": "Musculoskeletal", "short_description": "A systemic skeletal disease characterized by low bone mineral density and microarchitectural deterioration, resulting in heightened bone fragility.", "causes": "Imbalance between osteoclastic bone resorption and osteoblastic bone formation, accelerated by postmenopausal estrogen decline or aging.", "risk_factors": "Postmenopausal female status, advanced age, low body weight, calcium/vitamin D deficiency, glucocorticoid therapy, sedentary lifestyle, smoking.", "prevention": "Adequate dietary calcium and vitamin D, regular weight-bearing and resistance training exercises, fall prevention strategies, smoking cessation.", "management": "Antiresorptive medications (bisphosphonates, denosumab), anabolic agents (teriparatide), calcium and vitamin D supplementation, DEXA scans.", "when_to_seek_care": "Seek medical care following any low-trauma fall resulting in severe bone/hip pain, or progressive height loss and dorsal kyphosis."},
    {"id": 56, "name": "Gout", "category": "Musculoskeletal", "short_description": "A painful form of inflammatory crystal arthritis caused by the deposition of monosodium urate monohydrate crystals within articular and periarticular tissues.", "causes": "Persistent hyperuricemia exceeding the saturation threshold due to renal urate underexcretion or excessive purine metabolism.", "risk_factors": "Male sex, high-purine diet (red meat, seafood, beer, distilled spirits), high-fructose corn syrup, obesity, hypertension, diuretics.", "prevention": "Limit high-purine foods, eliminate beer and sweetened beverages, maintain high daily hydration, manage weight, avoid crash dieting.", "management": "Acute flare: NSAIDs, colchicine, or corticosteroids. Long-term management: urate-lowering therapy (allopurinol, febuxostat) targeting uric acid < 6 mg/dL.", "when_to_seek_care": "Seek prompt care for acute, excruciating monoarticular joint swelling (commonly the first metatarsophalangeal big toe joint)."},
    {"id": 57, "name": "Muscle Strain", "category": "Musculoskeletal", "short_description": "An acute or repetitive stretch injury causing tearing of muscle fibers or their associated myotendinous junctions.", "causes": "Overstretching, excessive eccentric muscular load, sudden violent contraction, or repetitive ergonomic fatigue without adequate warm-up.", "risk_factors": "Poor muscle flexibility, muscular fatigue, inadequate pre-exercise warm-up, prior muscle injury, sudden resumption of vigorous exertion.", "prevention": "Thorough dynamic warm-up before athletic activity, gradual progression of workout intensity, core muscle strengthening, ergonomic lifting form.", "management": "R.I.C.E. protocol (Rest, Ice, Compression, Elevation) initially, brief course of oral NSAIDs, gentle progressive stretching, physical therapy.", "when_to_seek_care": "Seek medical evaluation for an audible muscle \"pop\", severe inability to bear weight, visible muscular defect, or significant hematoma."},
    {"id": 58, "name": "Vitamin B12 Deficiency", "category": "Hematological", "short_description": "A nutritional hematological and neurological disorder caused by insufficient cobalamin levels, leading to megaloblastic anemia and neuropathy.", "causes": "Pernicious anemia (autoimmune destruction of gastric parietal cells / lack of intrinsic factor), strict vegan diet without supplementation, malabsorption.", "risk_factors": "Strict vegetarian/vegan diets, age > 65, chronic proton pump inhibitor or metformin use, prior gastric bypass or ileal resection, celiac disease.", "prevention": "Incorporate B12-rich foods (eggs, dairy, fortified cereals) or take regular oral cobalamin supplements if adhering to plant-based diets.", "management": "Oral high-dose vitamin B12 (1000 mcg daily) or intramuscular cyanocobalamin/hydroxocobalamin injections until stores are replenished.", "when_to_seek_care": "Seek medical evaluation for persistent numbness in extremities, unsteady gait, cognitive changes, or unexplained fatigue and pale skin."},
    {"id": 59, "name": "Vitamin D Deficiency", "category": "Hematological", "short_description": "A systemic nutritional insufficiency resulting from inadequate synthesis or dietary intake of calciferol, impairing calcium and bone homeostasis.", "causes": "Limited cutaneous synthesis from sunlight exposure, low dietary intake, malabsorption, renal/hepatic conversion impairments, pigmented skin.", "risk_factors": "Living in northern latitudes, limited outdoor sun exposure, extensive sunscreen use, darker skin pigmentation, obesity, malabsorptive bowel disease.", "prevention": "Sensible sun exposure, consuming vitamin D-fortified milk/cereals and fatty fish, routine daily supplementation of 800-2000 IU/day.", "management": "High-dose oral ergocalciferol (D2) or cholecalciferol (D3) therapy, followed by long-term maintenance supplementation and serum 25(OH)D monitoring.", "when_to_seek_care": "Seek healthcare consultation for persistent diffuse musculoskeletal aching, proximal muscle weakness, or recurrent bone stress fractures."},
    {"id": 60, "name": "Sickle Cell Disease", "category": "Hematological", "short_description": "An inherited genetic hemoglobinopathy caused by a point mutation in the beta-globin gene, resulting in abnormal sickle-shaped red blood cells.", "causes": "Homozygous inheritance of the HbS allele (glutamic acid substituted by valine at position 6 of the beta-globin chain).", "risk_factors": "African, Mediterranean, Middle Eastern, or South Asian ancestral descent; positive parental sickle cell carrier status.", "prevention": "Genetic counseling and carrier screening, avoiding cold exposure, preventing dehydration, avoiding high-altitude hypoxic triggers.", "management": "Hydroxyurea to boost fetal hemoglobin, routine vaccinations, prophylactic penicillin in children, hydration, multimodal pain crisis protocols.", "when_to_seek_care": "Seek immediate emergency medical care for acute vaso-occlusive pain crises, acute chest syndrome (chest pain/fever/cough), or stroke symptoms."},
    {"id": 61, "name": "Generalized Anxiety", "category": "Psychological", "short_description": "An educational screening category for persistent, excessive, and uncontrollable worry regarding various everyday life events and activities.", "causes": "Dysregulation of amygdala-prefrontal neurocircuitry, neurotransmitter imbalances (GABA, serotonin, norepinephrine), chronic psychosocial stress.", "risk_factors": "Family history of anxiety, major chronic life stress, personality traits (neuroticism), chronic physical illnesses, substance use.", "prevention": "Cognitive reframing, regular aerobic physical activity, consistent sleep hygiene, minimizing caffeine and stimulant consumption, mindfulness.", "management": "Evidence-based cognitive behavioral therapy (CBT), mindfulness-based stress reduction, SSRI or SNRI medications under psychiatric guidance.", "when_to_seek_care": "Seek urgent mental health evaluation if anxiety causes panic attacks, severe functional impairment, or suicidal thoughts."},
    {"id": 62, "name": "Depressive Symptoms", "category": "Psychological", "short_description": "An educational screening category for persistent depressed mood, loss of interest or pleasure, low energy, and feelings of worthlessness.", "causes": "Interactions between genetic vulnerability, neurochemical alterations, neuroendocrine dysregulation (HPA axis), and adverse life events.", "risk_factors": "Family history of mood disorders, chronic illness, severe interpersonal losses or trauma, chronic lack of social support, sleep disruption.", "prevention": "Regular cardiovascular physical activity, maintaining social connection, structured daily routines, balanced nutrition, exposure to morning daylight.", "management": "Psychotherapy (CBT, interpersonal therapy), structured exercise programs, antidepressant pharmacotherapy (SSRIs) supervised by clinicians.", "when_to_seek_care": "Seek immediate emergency support or call a crisis lifeline (988 in the US) if experiencing thoughts of self-harm or suicide."},
    {"id": 63, "name": "Chronic Stress & Burnout", "category": "Psychological", "short_description": "A state of chronic physical and psychological exhaustion coupled with emotional depletion caused by prolonged unmanaged stress.", "causes": "Sustained activation of the sympathetic-adreno-medullary and hypothalamic-pituitary-adrenal (HPA) axes without adequate recovery phases.", "risk_factors": "High workload environments, lack of perceived autonomy, caregiver demands, perfectionism, chronic financial strain, insufficient sleep.", "prevention": "Clear personal and professional boundaries, scheduled restorative downtime, peer support systems, regular physical movement, mindfulness.", "management": "Workplace/lifestyle restructuring, stress reduction coaching, sleep optimization, mindfulness-based stress reduction (MBSR), clinical counseling.", "when_to_seek_care": "Seek professional psychological consultation if burnout leads to chronic depressive feelings, severe insomnia, or panic attacks."},
    {"id": 64, "name": "Insomnia & Sleep Disorder", "category": "Psychological", "short_description": "A condition characterized by persistent difficulty initiating, consolidating, or maintaining restorative sleep despite adequate opportunity.", "causes": "Hyperarousal states of the central nervous system, circadian rhythm misalignment, poor sleep ergonomics, psychological distress.", "risk_factors": "Irregular sleep schedules, shift work, blue light screen use in bed, excessive caffeine/alcohol, chronic anxiety, sleep apnea.", "prevention": "Strict sleep hygiene: consistent sleep-wake schedule, dark/cool/quiet bedroom, avoiding screens 1 hour before bed, limiting caffeine after midday.", "management": "Cognitive Behavioral Therapy for Insomnia (CBT-I) as first-line gold standard, stimulus control, sleep restriction therapy, short-term sleep aids.", "when_to_seek_care": "Consult a sleep specialist or physician if sleep disruption persists over 3 months, causes daytime sleepiness, or is accompanied by loud snoring/gasping."},
    {"id": 65, "name": "Metabolic Syndrome", "category": "Endocrine", "short_description": "A clustering of at least three concurrent cardiometabolic risk factors including central obesity, hypertension, hypertriglyceridemia, low HDL, and impaired fasting glucose.", "causes": "Visceral adiposity-induced chronic low-grade inflammation, adipokine dysregulation, and systemic peripheral insulin resistance.", "risk_factors": "Sedentary lifestyle, high-carbohydrate refined diet, visceral abdominal obesity, advancing age, genetic predisposition.", "prevention": "Structured Mediterranean-style nutrition, 150 minutes/week moderate aerobic exercise plus resistance training, maintaining waist circumference < 40 in (men) or < 35 in (women).", "management": "Intensive therapeutic lifestyle intervention, targeted pharmacological management of individual risk factors (statins, antihypertensives, metformin).", "when_to_seek_care": "Consult your primary healthcare provider for comprehensive cardiometabolic blood panel screening and personalized prevention planning."}
]

def render_page(content_html, **kwargs):
    user = session.get('user')
    base_template = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Healthcare - Intelligent Disease Prediction & Health Assistance System</title>
    <!-- Early theme initializer to prevent FOUC & Bulletproof Theme Engine -->
    <script>
        function applyTheme(theme) {
            var valid = (theme === 'light') ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', valid);
            document.documentElement.setAttribute('data-bs-theme', valid);
            try {
                localStorage.setItem('ai_healthcare_theme', valid);
                localStorage.setItem('theme', valid);
            } catch(e) {}

            var btns = document.querySelectorAll('.theme-toggle-btn, #themeToggleBtn');
            btns.forEach(function(btn) {
                var darkIcon = btn.querySelector('.theme-icon-dark');
                var lightIcon = btn.querySelector('.theme-icon-light');
                var text = btn.querySelector('.theme-text');
                if (valid === 'light') {
                    if (darkIcon) darkIcon.classList.add('d-none');
                    if (lightIcon) lightIcon.classList.remove('d-none');
                    if (text) text.textContent = 'Light';
                    btn.setAttribute('title', 'Switch to Dark Mode');
                    btn.setAttribute('aria-label', 'Switch to Dark Mode');
                } else {
                    if (darkIcon) darkIcon.classList.remove('d-none');
                    if (lightIcon) lightIcon.classList.add('d-none');
                    if (text) text.textContent = 'Dark';
                    btn.setAttribute('title', 'Switch to Light Mode');
                    btn.setAttribute('aria-label', 'Switch to Light Mode');
                }
            });
        }

        function toggleSiteTheme() {
            var current = document.documentElement.getAttribute('data-theme') || 'dark';
            var next = (current === 'dark') ? 'light' : 'dark';
            applyTheme(next);
        }

        (function() {
            var urlParams = new URLSearchParams(window.location.search);
            var urlTheme = urlParams.get('theme');
            var saved = urlTheme || localStorage.getItem('ai_healthcare_theme') || localStorage.getItem('theme');
            var theme = (saved === 'light' || saved === 'dark') ? saved : 'dark';
            if (urlTheme === 'light' || urlTheme === 'dark') {
                try {
                    localStorage.setItem('ai_healthcare_theme', urlTheme);
                    localStorage.setItem('theme', urlTheme);
                } catch(e) {}
            }
            document.documentElement.setAttribute('data-theme', theme);
            document.documentElement.setAttribute('data-bs-theme', theme);
        })();
    </script>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root,
        [data-theme="dark"],
        [data-bs-theme="dark"] {
            --bg-primary: #0b1624;
            --bg-secondary: #111f30;
            --bg-card: #17283a;
            --bg-card-hover: #1c2e42;
            --bg-card-subtle: #0f1c2b;
            --bg-input: #0f1c2b;
            --text-input: #ffffff;
            
            --bg-body: #0b1624;
            --bg-main: #0b1624;
            --bg-surface: #111f30;
            --card-bg: #17283a;
            --card-border: #2b4054;
            --surface: #17283a;
            --surface-secondary: #0f1c2b;

            --border-color: #2b4054;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-card: #2b4054;
            --border-input: #334a60;
            --border-focus: #12bfe3;

            --text-primary: #ffffff;
            --text-heading: #ffffff;
            --text-secondary: #c3cfdd;
            --text-main: #c3cfdd;
            --text-muted: #9aaabd;

            --accent-primary: #12bfe3;
            --accent-secondary: #0d9488;
            --accent: #12bfe3;
            --accent-dark: #0aa6c5;
            --button-text: #ffffff;

            --navbar-bg: rgba(11, 22, 36, 0.94);
            --navbar-text: #c3cfdd;
            --footer-bg: #070e17;
            --footer-heading: #ffffff;
            --footer-text: #9aaabd;
            --footer-border: #1a2938;

            --hero-bg: linear-gradient(135deg, #0b1624 0%, #17283a 55%, #0f3545 100%);
            --hero-heading: #ffffff;
            --hero-text: #c3cfdd;
            --hero-badge-bg: rgba(18, 191, 227, 0.15);
            --hero-badge-text: #38d3f2;
            --hero-badge-border: rgba(18, 191, 227, 0.35);
            --hero-btn-sec-color: #ffffff;
            --hero-btn-sec-border: rgba(255, 255, 255, 0.35);
            --hero-btn-sec-hover: rgba(255, 255, 255, 0.12);

            --shadow: rgba(0, 0, 0, 0.3);

            --tile-bg-matte: #111f30;
            --tile-border-matte: #1f3347;
            --tile-selected-bg: linear-gradient(135deg, rgba(18, 191, 227, 0.18) 0%, rgba(13, 148, 136, 0.28) 100%);
            --tile-selected-border: #12bfe3;
            --tile-selected-shadow: 0 8px 24px -4px rgba(18, 191, 227, 0.35);
            --gloss-reflection: linear-gradient(180deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.03) 50%, rgba(255, 255, 255, 0) 100%);
        }

        [data-theme="light"],
        [data-bs-theme="light"] {
            --accent-primary: #0aa6c5;
            --accent-secondary: #0d9488;
            --accent: #0aa6c5;
            --accent-dark: #088b9a;
            --button-text: #ffffff;

            --bg-primary: #f5f9fc;
            --bg-secondary: #ffffff;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-card-subtle: #edf3f8;
            --bg-input: #ffffff;
            --text-input: #172033;

            --bg-body: #f5f9fc;
            --bg-main: #f5f9fc;
            --bg-surface: #ffffff;
            --card-bg: #ffffff;
            --card-border: #d9e2ec;
            --surface: #ffffff;
            --surface-secondary: #edf3f8;

            --border-color: #d9e2ec;
            --border-subtle: #d9e2ec;
            --border-card: #d9e2ec;
            --border-input: #cbd5e1;
            --border-focus: #0aa6c5;

            --text-primary: #172033;
            --text-heading: #172033;
            --text-secondary: #526071;
            --text-main: #405063;
            --text-muted: #6b7280;

            --navbar-bg: rgba(255, 255, 255, 0.96);
            --navbar-text: #172033;
            --footer-bg: #f0f4f9;
            --footer-heading: #172033;
            --footer-text: #6b7280;
            --footer-border: #d9e2ec;

            --hero-bg: linear-gradient(135deg, #e8f2f8 0%, #edf4f9 60%, #f0f6fa 100%);
            --hero-heading: #172033;
            --hero-text: #526071;
            --hero-badge-bg: rgba(10, 166, 197, 0.1);
            --hero-badge-text: #0aa6c5;
            --hero-badge-border: rgba(10, 166, 197, 0.25);
            --hero-btn-sec-color: #172033;
            --hero-btn-sec-border: #94a3b8;
            --hero-btn-sec-hover: rgba(15, 23, 42, 0.06);

            --shadow: rgba(0, 0, 0, 0.08);

            --tile-bg-matte: #ffffff;
            --tile-border-matte: #cbd5e1;
            --tile-selected-bg: linear-gradient(135deg, rgba(10, 166, 197, 0.12) 0%, rgba(13, 148, 136, 0.18) 100%);
            --tile-selected-border: #0aa6c5;
            --tile-selected-shadow: 0 8px 24px -4px rgba(10, 166, 197, 0.25);
            --gloss-reflection: linear-gradient(180deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0) 100%);
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            transition: background-color 0.25s ease, color 0.25s ease;
        }

        h1, h2, h3, h4, h5, h6, .text-heading {
            color: var(--text-heading);
            transition: color 0.2s ease;
        }

        .text-primary-theme {
            color: var(--text-primary) !important;
        }

        .text-secondary-theme {
            color: var(--text-secondary) !important;
        }

        .navbar-custom {
            background: var(--navbar-bg);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--card-border);
        }

        [data-theme="light"] .navbar-custom .nav-link {
            color: #172033 !important;
        }

        [data-theme="light"] .navbar-brand {
            color: #172033 !important;
        }

        .card-custom {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            color: var(--text-primary);
            transition: background 0.25s ease, border 0.25s ease, color 0.25s ease;
        }

        .hero-banner {
            background: var(--hero-bg);
            color: var(--text-primary);
            border-radius: 24px;
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: background 0.25s ease, border-color 0.25s ease;
        }

        .hero-banner h1, .hero-banner .hero-heading {
            color: var(--hero-heading) !important;
        }

        .hero-banner p, .hero-banner .hero-lead {
            color: var(--hero-text) !important;
        }

        .hero-badge {
            background: var(--hero-badge-bg) !important;
            color: var(--hero-badge-text) !important;
            border: 1px solid var(--hero-badge-border) !important;
            font-weight: 700;
        }

        .btn-hero-secondary, .btn-explore {
            color: var(--hero-btn-sec-color) !important;
            border: 1.5px solid var(--hero-btn-sec-border) !important;
            background-color: transparent !important;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .btn-hero-secondary:hover, .btn-explore:hover {
            color: var(--hero-btn-sec-color) !important;
            background-color: var(--hero-btn-sec-hover) !important;
            border-color: var(--accent-primary) !important;
        }

        [data-theme="light"] .btn-outline-light,
        [data-bs-theme="light"] .btn-outline-light {
            color: var(--hero-btn-sec-color) !important;
            border-color: var(--hero-btn-sec-border) !important;
            background-color: transparent !important;
        }

        [data-theme="light"] .btn-outline-light:hover,
        [data-bs-theme="light"] .btn-outline-light:hover {
            color: var(--hero-btn-sec-color) !important;
            background-color: var(--hero-btn-sec-hover) !important;
            border-color: var(--accent-primary) !important;
        }

        /* Light mode contrast safety */
        [data-theme="light"] h1.text-white,
        [data-theme="light"] h2.text-white,
        [data-theme="light"] h3.text-white,
        [data-theme="light"] h4.text-white,
        [data-theme="light"] h5.text-white,
        [data-theme="light"] h6.text-white,
        [data-theme="light"] .hero-banner h1.text-white,
        [data-theme="light"] .form-label.text-white,
        [data-theme="light"] .form-label.text-light,
        [data-theme="light"] p.text-white,
        [data-theme="light"] p.text-light,
        [data-theme="light"] p.text-white-50,
        [data-theme="light"] span.text-white:not(.badge):not(.btn *),
        [data-theme="light"] strong.text-white {
            color: var(--text-primary) !important;
        }

        [data-theme="light"] p.lead.text-white-50,
        [data-theme="light"] p.lead.text-light {
            color: var(--text-secondary) !important;
        }

        [data-theme="dark"] h1.text-dark,
        [data-theme="dark"] h2.text-dark,
        [data-theme="dark"] h3.text-dark,
        [data-theme="dark"] h4.text-dark,
        [data-theme="dark"] h5.text-dark,
        [data-theme="dark"] h6.text-dark,
        [data-theme="dark"] .form-label.text-dark {
            color: var(--text-heading) !important;
        }

        .btn-info, .btn-primary, .btn-danger, .btn-success, .btn-primary-custom {
            color: #ffffff !important;
            font-weight: 600;
        }

        /* AI Scanner styles */
        .scanner-dropzone {
            border: 2px dashed var(--card-border);
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .scanner-dropzone:hover, .scanner-dropzone.dragover {
            border-color: var(--accent-primary);
            background: rgba(6, 182, 212, 0.08);
        }
        .scanner-preview-wrapper {
            position: relative;
            max-width: 480px;
            margin: 0 auto;
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid var(--card-border);
            background: #000;
        }
        .scanner-preview-img {
            width: 100%;
            max-height: 400px;
            object-fit: contain;
            display: block;
        }
        .scanner-laser-beam {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent 0%, #06b6d4 25%, #22d3ee 50%, #06b6d4 75%, transparent 100%);
            box-shadow: 0 0 16px 4px rgba(6, 182, 212, 0.85);
            z-index: 10;
            display: none;
        }
        .scanning-active .scanner-laser-beam {
            display: block;
            animation: laserScanSweep 2.2s ease-in-out infinite alternate;
        }
        @keyframes laserScanSweep {
            0% { top: 0%; }
            100% { top: calc(100% - 4px); }
        }
        .badge-category {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 18px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .badge-category-infection { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.35); }
        .badge-category-inflammation { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.35); }
        .badge-category-injury { background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.35); }
        .badge-category-rash { background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.35); }
        .badge-category-swelling { background: rgba(13, 148, 136, 0.15); color: #0d9488; border: 1px solid rgba(13, 148, 136, 0.35); }
        .badge-category-unable { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.35); }
        .metric-pill-card {
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 12px 14px;
            text-align: center;
        }
        .metric-pill-val { font-size: 1.3rem; font-weight: 800; color: var(--text-primary); }
        .metric-pill-lbl { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }
        .warning-sign-card {
            background: rgba(239, 68, 68, 0.05);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 4px solid #ef4444;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.88rem;
        }

        .bg-card-subtle {
            background-color: var(--bg-card-subtle) !important;
        }
        .border-theme {
            border-color: var(--border-color) !important;
        }

        /* Symptom Relation & Card Sub-Elements */
        .symptom-relation-box {
            background-color: var(--bg-card-subtle);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 1rem;
            transition: background-color 0.25s ease, border-color 0.25s ease;
        }
        .symptom-relation-title {
            color: var(--text-primary);
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.01em;
        }
        .symptom-relation-content {
            color: var(--text-secondary);
            font-size: 0.85rem;
            line-height: 1.5;
        }
        .symptom-condition-tag {
            display: inline-flex;
            align-items: center;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.78rem;
            font-weight: 500;
            padding: 3px 9px;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        .symptom-condition-tag:hover {
            border-color: var(--accent-primary);
            color: var(--text-primary);
        }
        .symptom-relation-empty {
            color: var(--text-muted);
            font-style: italic;
            font-size: 0.82rem;
        }

        .symptom-evaluation-box {
            background-color: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            transition: background-color 0.25s ease, border-color 0.25s ease;
        }
        .symptom-evaluation-title {
            color: var(--accent-amber);
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .symptom-evaluation-text {
            color: var(--text-secondary);
            font-size: 0.85rem;
            line-height: 1.5;
        }

        [data-theme="dark"] .bg-light {
            background-color: #131d33 !important;
            color: #f8fafc !important;
        }

        [data-theme="dark"] .form-control,
        [data-theme="dark"] .form-select {
            background-color: #0e1626;
            border-color: #1e293b;
            color: #f8fafc;
        }

        [data-theme="dark"] .form-control:focus,
        [data-theme="dark"] .form-select:focus {
            background-color: #131d33;
            color: #ffffff;
            border-color: #06b6d4;
            box-shadow: 0 0 0 0.25rem rgba(6, 182, 212, 0.25);
        }

        [data-theme="dark"] .form-select option {
            background-color: #0f172a;
            color: #f8fafc;
        }

        [data-theme="light"] .form-control,
        [data-theme="light"] .form-select {
            background-color: #ffffff;
            border-color: #cbd5e1;
            color: #0f172a;
        }

        [data-theme="light"] .form-select option {
            background-color: #ffffff;
            color: #0f172a;
        }

        .btn-primary-custom {
            background: var(--accent-secondary);
            color: #fff;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            padding: 10px 24px;
            transition: all 0.2s ease;
        }

        .btn-primary-custom:hover {
            background: #0f766e;
            color: #fff;
        }

        .disclaimer-banner {
            background: rgba(245, 158, 11, 0.12);
            border-left: 4px solid #f59e0b;
            color: #d97706;
            padding: 14px 18px;
            border-radius: 10px;
            font-size: 0.875rem;
        }

        [data-theme="dark"] .disclaimer-banner {
            color: #fbbf24;
        }

        .symptom-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
            gap: 12px;
        }

        /* Pure Tile Design (No Checkmarks, Matte to Glossy) */
        .symptom-tile {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 14px 16px;
            min-height: 54px;
            border-radius: 12px;
            cursor: pointer;
            background: var(--tile-bg-matte);
            border: 1.5px solid var(--tile-border-matte);
            overflow: hidden;
            user-select: none;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            outline: none;
        }

        .symptom-tile:hover {
            border-color: rgba(6, 182, 212, 0.5);
            transform: translateY(-1px);
        }

        .symptom-tile:focus-visible {
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.4);
            border-color: var(--accent-primary);
        }

        .symptom-tile input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
            pointer-events: none;
        }

        .symptom-tile-gloss {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 48%;
            background: var(--gloss-reflection);
            opacity: 0;
            pointer-events: none;
            border-radius: 10px 10px 0 0;
            transition: opacity 0.25s ease;
        }

        .symptom-tile-name {
            position: relative;
            z-index: 2;
            font-size: 0.90rem;
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.3;
            transition: color 0.2s ease, font-weight 0.2s ease;
        }

        /* Selected State (Glossy + Elevated + Prominent Border, NO Checkmarks) */
        .symptom-tile.selected {
            background: var(--tile-selected-bg) !important;
            border-color: var(--tile-selected-border) !important;
            box-shadow: var(--tile-selected-shadow);
            transform: translateY(-2px);
        }

        .symptom-tile.selected .symptom-tile-gloss {
            opacity: 1;
        }

        .symptom-tile.selected .symptom-tile-name {
            font-weight: 700;
            color: var(--accent-primary);
        }

        /* Custom Range Slider */
        .form-range {
            cursor: pointer;
        }
        .form-range::-webkit-slider-thumb {
            background: var(--accent-primary);
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.6);
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }

        .slider-val-badge {
            display: inline-block;
            min-width: 48px;
            text-align: center;
            font-weight: 700;
            border-radius: 6px;
            padding: 2px 8px;
        }

        .counter-animating {
            display: inline-block;
            transition: transform 0.05s ease;
        }

        footer {
            margin-top: auto;
            background: var(--footer-bg);
            color: var(--text-muted);
            padding: 35px 0 20px;
            border-top: 1px solid var(--card-border);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-xl navbar-custom sticky-top py-3">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center me-4" href="/">
                <i class="bi bi-heart-pulse-fill text-info me-2 fs-4"></i>
                <span class="fs-4 fw-bold">AI Healthcare<span class="text-info">.</span></span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMain">
                <ul class="navbar-nav ms-auto align-items-center gap-1 small fw-medium">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
                    <li class="nav-item"><a class="nav-link" href="/prediction">AI Prediction</a></li>
                    <li class="nav-item"><a class="nav-link" href="/scanner"><i class="bi bi-camera me-1"></i>Injury Scanner</a></li>
                    <li class="nav-item"><a class="nav-link" href="/assessment">Clinical Risk</a></li>
                    <li class="nav-item"><a class="nav-link" href="/simulator">Simulator</a></li>
                    <li class="nav-item"><a class="nav-link" href="/diseases">Diseases Library</a></li>
                    <li class="nav-item"><a class="nav-link" href="/symptoms">Symptoms Guide</a></li>
                    <li class="nav-item"><a class="nav-link" href="/prevention">Prevention</a></li>
                    <li class="nav-item"><a class="nav-link" href="/dataset-info">Dataset & AI</a></li>
                    
                    <!-- Theme Toggle Button -->
                    <li class="nav-item mx-xl-2">
                        <button type="button" class="btn btn-outline-secondary btn-sm rounded-pill px-3 theme-toggle-btn d-flex align-items-center gap-1" id="themeToggleBtn" onclick="toggleSiteTheme()" title="Toggle Dark/Light Mode" aria-label="Toggle dark/light theme">
                            <i class="bi bi-moon-stars-fill theme-icon-dark text-info"></i>
                            <i class="bi bi-sun-fill theme-icon-light text-warning d-none"></i>
                            <span class="theme-text small fw-semibold">Dark</span>
                        </button>
                    </li>

                    {% if user %}
                        <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item ms-xl-1">
                            <a class="btn btn-outline-danger btn-sm rounded-pill px-3" href="/logout">Logout ({{ user.name }})</a>
                        </li>
                    {% else %}
                        <li class="nav-item ms-xl-1"><a class="btn btn-outline-info btn-sm rounded-pill px-3" href="/login">Login</a></li>
                        <li class="nav-item ms-xl-1"><a class="btn btn-info text-white btn-sm rounded-pill px-3" href="/register">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="py-4">
        <div class="container">
            """ + content_html + """
        </div>
    </main>

    <footer>
        <div class="container text-center">
            <p class="small text-muted mb-1">&copy; 2026 AI Healthcare – Intelligent Disease Prediction & Health Assistance System.</p>
            <p class="small text-warning">Educational College Project — Not a Medical Diagnosis System.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Theme Engine
        function initTheme() {
            var current = document.documentElement.getAttribute('data-theme') || 'dark';
            if (typeof applyTheme === 'function') {
                applyTheme(current);
            }

            var btn = document.getElementById('themeToggleBtn');
            if (!btn) return;
            btn.removeAttribute('onclick');
            btn.onclick = function(e) {
                if (e) e.preventDefault();
                toggleSiteTheme();
            };
        }

        // Accessible Symptom Tiles Interaction (No Checkmarks)
        function initTiles() {
            var tiles = document.querySelectorAll('.symptom-tile');
            var urlParams = new URLSearchParams(window.location.search);
            var pre = urlParams.get('symptom');

            tiles.forEach(function(tile) {
                var cb = tile.querySelector('input[type="checkbox"]');
                if (!cb) return;

                if (pre && cb.value.toLowerCase() === pre.toLowerCase()) {
                    cb.checked = true;
                }

                if (cb.checked) {
                    tile.classList.add('selected');
                    tile.setAttribute('aria-checked', 'true');
                } else {
                    tile.classList.remove('selected');
                    tile.setAttribute('aria-checked', 'false');
                }

                function toggleTile(e) {
                    if (e.target !== cb) {
                        e.preventDefault();
                        cb.checked = !cb.checked;
                    }
                    if (cb.checked) {
                        tile.classList.add('selected');
                        tile.setAttribute('aria-checked', 'true');
                    } else {
                        tile.classList.remove('selected');
                        tile.setAttribute('aria-checked', 'false');
                    }
                }

                tile.addEventListener('click', toggleTile);
                tile.addEventListener('keydown', function(e) {
                    if (e.key === ' ' || e.key === 'Enter') {
                        e.preventDefault();
                        toggleTile(e);
                    }
                });
            });
        }

        // Interactive Live Sliders with Badges (Touch & Mouse)
        function initSliders() {
            var sliders = document.querySelectorAll('.form-range');
            sliders.forEach(function(slider) {
                var targetId = 'val_' + (slider.getAttribute('data-target') || slider.name || slider.id);
                var badge = document.getElementById(targetId);
                function update() {
                    if (badge) {
                        badge.textContent = slider.value;
                    }
                }
                slider.addEventListener('input', update);
                slider.addEventListener('change', update);
                slider.addEventListener('touchmove', update);
                update();
            });
        }

        // Upward Digital Counter Animation
        function animateCounter(el, target, durationMs) {
            if (!el || isNaN(target)) return;
            var start = 0.0;
            var startTime = performance.now();
            function step(time) {
                var elapsed = time - startTime;
                var progress = Math.min(elapsed / durationMs, 1.0);
                var ease = 1 - Math.pow(1 - progress, 3);
                var cur = start + (target - start) * ease;
                el.textContent = cur.toFixed(1) + '%';
                if (progress < 1.0) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = target.toFixed(1) + '%';
                }
            }
            requestAnimationFrame(step);
        }

        // Symptoms Guide Live Search & Category Filtering
        function initSymptomsGuideSearch() {
            var searchInput = document.getElementById('symptomSearchInput');
            var filterPills = document.querySelectorAll('.symptom-filter-pill');
            var symptomCards = document.querySelectorAll('.symptom-guide-card');
            if (!symptomCards.length) return;

            function applyFilter() {
                var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
                var activePill = document.querySelector('.symptom-filter-pill.active');
                var selectedCategory = activePill ? activePill.getAttribute('data-category').toLowerCase() : 'all';

                var visibleCount = 0;
                symptomCards.forEach(function(card) {
                    var name = card.getAttribute('data-name') || '';
                    var category = card.getAttribute('data-category') || '';
                    var desc = card.getAttribute('data-desc') || '';

                    var matchesSearch = query === '' || name.toLowerCase().indexOf(query) !== -1 || desc.toLowerCase().indexOf(query) !== -1;
                    var matchesCategory = selectedCategory === 'all' || category.toLowerCase() === selectedCategory;

                    if (matchesSearch && matchesCategory) {
                        card.style.display = 'block';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });

                var emptyMsg = document.getElementById('symptomsEmptySearch');
                if (emptyMsg) {
                    emptyMsg.style.display = visibleCount === 0 ? 'block' : 'none';
                }
            }

            if (searchInput) {
                searchInput.addEventListener('input', applyFilter);
            }

            filterPills.forEach(function(pill) {
                pill.addEventListener('click', function() {
                    filterPills.forEach(function(p) {
                        p.classList.remove('active', 'btn-info', 'text-white', 'fw-bold');
                        p.classList.add('btn-outline-secondary');
                    });
                    this.classList.remove('btn-outline-secondary');
                    this.classList.add('active', 'btn-info', 'text-white', 'fw-bold');
                    applyFilter();
                });
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            initTheme();
            initTiles();
            initSliders();
            initSymptomsGuideSearch();
            var counters = document.querySelectorAll('.animate-counter');
            counters.forEach(function(c) {
                var tgt = parseFloat(c.getAttribute('data-target'));
                if (!isNaN(tgt)) {
                    animateCounter(c, tgt, 1300);
                }
            });
        });
    </script>
</body>
</html>
    """
    return render_template_string(base_template, **kwargs)

@app.route('/')
@app.route('/index.php')
@app.route('/api')
@app.route('/api/')
def home():
    content = """
    <div class="row align-items-center my-4 py-5 px-4 rounded-4 hero-banner shadow-lg">
        <div class="col-lg-7">
            <span class="badge hero-badge fw-bold px-3 py-2 rounded-pill mb-3">AI & Machine Learning Platform</span>
            <h1 class="display-4 fw-extrabold hero-heading mb-3">Smarter Healthcare Powered by Artificial Intelligence</h1>
            <p class="lead hero-lead mb-4 opacity-90">
                Analyze symptoms and assess potential conditions across <strong>65 conditions</strong> using trained classification models.
            </p>
            <div class="d-flex flex-wrap gap-3">
                <a href="/prediction" class="btn btn-primary-custom btn-lg rounded-pill px-4">Check Symptoms Now</a>
                <a href="/diseases" class="btn btn-hero-secondary btn-lg rounded-pill px-4">Explore Diseases</a>
            </div>
        </div>
        <div class="col-lg-5 text-center mt-4 mt-lg-0">
            <div class="card-custom p-4 border-info">
                <i class="bi bi-heart-pulse-fill display-1 text-info mb-3"></i>
                <h4 class="fw-bold hero-heading mb-2">65 Condition Records</h4>
                <p class="small text-muted">Multi-symptom classification engine & structured medical database.</p>
            </div>
        </div>
    </div>

    <div class="disclaimer-banner my-4 p-4 text-center">
        <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
        <strong>Educational Disclaimer:</strong> This system provides educational/informational AI predictions only and is not a medical diagnosis. Please consult a qualified healthcare professional for diagnosis and treatment.
    </div>
    """
    return render_page(content)

@app.route('/about')
@app.route('/about.php')
@app.route('/api/about')
def about():
    content = """
    <div class="card-custom p-5 text-center my-4">
        <span class="badge hero-badge px-3 py-1 rounded-pill mb-3">ABOUT PLATFORM</span>
        <h2 class="fw-bold hero-heading mb-3">AI Healthcare Platform Overview</h2>
        <p class="lead text-muted max-w-xl mx-auto mb-4">
            Demonstrating how Machine Learning assists healthcare users by analyzing symptoms and evaluating statistical likelihoods of 25 medical conditions.
        </p>
    </div>
    """
    return render_page(content)

@app.route('/prediction', methods=['GET', 'POST'])
@app.route('/prediction.php', methods=['GET', 'POST'])
@app.route('/api/prediction', methods=['GET', 'POST'])
def prediction():
    result = None
    selected_symptoms = []
    
    # Preselection via URL query string
    pre_symptom = request.args.get('symptom', '').strip()
    if pre_symptom:
        selected_symptoms.append(pre_symptom)
        
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        if selected_symptoms:
            result = predict_symptoms(selected_symptoms)

    symptoms_catalog = [
        ("General & Systemic", [
            ("fatigue", "Chronic Lethargy & Fatigue"),
            ("fever", "Fever (>100.4°F)"),
            ("chills", "Severe Chills & Rigors"),
            ("weight_loss", "Unexplained Rapid Weight Loss"),
            ("sweats", "Drenching Night Sweats"),
            ("localized_swelling", "Localized Swelling / Edema")
        ]),
        ("Respiratory System", [
            ("shortness_of_breath", "Shortness of Breath (Dyspnea)"),
            ("cough_with_sputum", "Persistent Productive Cough"),
            ("dry_cough", "Dry Non-Productive Cough"),
            ("wheezing", "Respiratory Wheezing"),
            ("hemoptysis", "Hemoptysis (Coughing Blood)"),
            ("runny_nose", "Runny Nose (Rhinorrhea)"),
            ("sneezing", "Frequent Sneezing"),
            ("sore_throat", "Sore or Scratchy Throat"),
            ("nasal_congestion", "Sinus Pressure & Congestion")
        ]),
        ("Cardiovascular System", [
            ("chest_pain", "Chest Pain / Tightness"),
            ("high_blood_pressure", "Hypertension Indicators"),
            ("palpitations", "Rapid Heart Palpitations"),
            ("leg_swelling", "Lower Extremity / Ankle Edema")
        ]),
        ("Gastrointestinal & Hepatic", [
            ("heartburn", "Heartburn / Acid Reflux"),
            ("abdominal_pain", "Abdominal Pain & Cramping"),
            ("nausea", "Persistent Nausea"),
            ("vomiting", "Persistent Vomiting"),
            ("diarrhea", "Frequent Watery Diarrhea"),
            ("constipation", "Chronic Constipation"),
            ("bloating", "Abdominal Bloating & Gas"),
            ("jaundice", "Jaundice (Yellowing Eyes/Skin)"),
            ("right_upper_quadrant_pain", "Right Upper Quadrant Pain")
        ]),
        ("Neurological System", [
            ("headache", "Severe Throbbing Headache"),
            ("dizziness", "Dizziness & Lightheadedness"),
            ("seizures", "Involuntary Seizures"),
            ("resting_tremor", "Resting Hand / Limb Tremor"),
            ("memory_loss", "Progressive Memory Decline"),
            ("numbness_tingling", "Numbness & Paresthesia"),
            ("blurred_vision", "Blurred or Fluctuating Vision"),
            ("loss_of_smell", "Loss of Smell / Taste (Anosmia)")
        ]),
        ("Endocrine & Metabolic", [
            ("high_blood_sugar", "High Blood Sugar & Thirst"),
            ("excessive_hunger", "Excessive Hunger (Polyphagia)"),
            ("weight_gain", "Unintentional Rapid Weight Gain"),
            ("cold_intolerance", "Cold Intolerance"),
            ("heat_intolerance", "Heat Intolerance / Sweating")
        ]),
        ("Renal & Urinary", [
            ("frequent_urination", "Frequent Urination (Polyuria)"),
            ("dysuria", "Dysuria (Painful Urination)"),
            ("flank_pain", "Flank / Low Back Pain"),
            ("blood_in_urine", "Blood in Urine (Hematuria)")
        ]),
        ("Dermatological System", [
            ("skin_rash", "Visible Skin Rash or Redness"),
            ("itching", "Intense Pruritus / Itching"),
            ("skin_flaking", "Flaking or Scaly Skin Patches"),
            ("acne_breakouts", "Acne Papules, Pustules or Cysts"),
            ("hives_welts", "Raised Itchy Wheals / Hives"),
            ("hair_thinning", "Diffuse Hair Thinning / Loss")
        ]),
        ("Musculoskeletal System", [
            ("joint_pain", "Severe Joint / Bone Pain"),
            ("joint_stiffness", "Morning Joint Stiffness"),
            ("muscle_pain", "Muscle Aches & Myalgia"),
            ("back_pain", "Lower Back Ache or Stiffness")
        ]),
        ("Psychological & Well-being", [
            ("anxiety_nervousness", "Excessive Worry & Nervousness"),
            ("depressed_mood", "Persistent Depressed Mood"),
            ("sleep_disturbance", "Insomnia & Sleep Disruption")
        ])
    ]

    tiles_html = ""
    for category, syms in symptoms_catalog:
        tiles_html += f'<div class="mb-4"><h6 class="text-info text-uppercase fw-bold small tracking-wider mb-3 pb-1 border-bottom border-secondary border-opacity-25"><i class="bi bi-activity me-1"></i> {category}</h6><div class="symptom-grid">'
        for key, name in syms:
            checked = "checked" if key in selected_symptoms else ""
            selected_cls = "selected" if key in selected_symptoms else ""
            aria_checked = "true" if key in selected_symptoms else "false"
            tiles_html += f"""
            <label class="symptom-tile {selected_cls}" tabindex="0" role="checkbox" aria-checked="{aria_checked}">
                <input type="checkbox" name="symptoms" value="{key}" class="symptom-checkbox" {checked}>
                <div class="symptom-tile-gloss"></div>
                <div class="symptom-tile-content">
                    <span class="symptom-tile-name">{name}</span>
                </div>
            </label>
            """
        tiles_html += '</div></div>'

    res_card = ""
    if result:
        status = result.get('status')
        if status == 'insufficient_information' or result.get('prediction') == 'Insufficient Information':
            msg = result.get('message', 'A single symptom or non-specific combination does not provide enough statistical evidence across our 65 condition categories. Please select 2 or more symptoms to evaluate.')
            res_card = f"""
            <div class="card-custom p-4 p-md-5 text-center border-warning mt-4">
                <span class="badge bg-warning bg-opacity-20 text-warning border border-warning border-opacity-25 mb-3 px-3 py-1 fw-bold">
                    <i class="bi bi-exclamation-circle-fill me-1"></i> INSUFFICIENT INFORMATION
                </span>
                <h3 class="fw-bold mb-2">Additional Symptoms Needed</h3>
                <p class="text-muted small mb-3">{msg}</p>
                <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 text-start small mb-3">
                    <strong class="text-info d-block mb-2"><i class="bi bi-lightbulb-fill me-1"></i> Suggested Actions:</strong>
                    <ul class="mb-0 ps-3 text-muted">
                        <li>Select additional co-occurring symptoms from the tiles.</li>
                        <li>Browse our <a href="/symptoms" class="text-info text-decoration-underline">Symptoms Guide</a> for associated signs.</li>
                        <li>Consult a healthcare professional for persistent health concerns.</li>
                    </ul>
                </div>
                <div class="d-flex justify-content-between text-muted small border-top border-secondary border-opacity-25 pt-2">
                    <span>Model: {result.get('model_version', 'Multi-Disease Model v2')}</span>
                    <span class="badge bg-secondary bg-opacity-25 text-info">65 Supported Conditions</span>
                </div>
                <div class="disclaimer-banner small text-start my-3">
                    <h6 class="fw-bold mb-1 text-warning"><i class="bi bi-shield-exclamation me-1"></i> Medical Disclaimer</h6>
                    {result.get('disclaimer')}
                </div>
            </div>
            """
        else:
            prob = result.get('probability', 0.0)
            influencing = "".join([f'<span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 px-2 py-1 me-1">{s}</span>' for s in result.get('influencing_symptoms', [])])
            runner_ups_html = ""
            if result.get('runner_ups'):
                ru_items = "".join([f'<li class="d-flex justify-content-between py-1 border-bottom border-secondary border-opacity-10 text-muted"><span>{r.get("disease")}</span><span class="fw-bold text-primary-theme">{r.get("probability")}%</span></li>' for r in result.get('runner_ups', [])])
                runner_ups_html = f'<div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 my-3 text-start small"><strong class="d-block mb-2"><i class="bi bi-bar-chart me-1 text-warning"></i> Other Possible Matches Considered:</strong><ul class="list-unstyled mb-0">{ru_items}</ul></div>'

            pred_name = result.get('prediction')
            res_card = f"""
            <div class="card-custom p-4 text-center border-info mt-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-secondary px-3 py-1">AI MODEL OUTPUT</span>
                    <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 small">{result.get('model_version', 'Multi-Disease Model v2')}</span>
                </div>
                <h5 class="text-muted text-uppercase fw-bold small mt-2">Most Likely Condition (AI Classification)</h5>
                <h2 class="display-6 fw-bold my-2">{pred_name}</h2>
                
                <div class="my-3 py-2 border-top border-bottom border-secondary border-opacity-25">
                    <span class="display-3 fw-extrabold text-info counter-text animate-counter" data-target="{prob}">00.0%</span>
                    <p class="small text-muted mb-0 mt-1">Calculated model likelihood score across 65 conditions</p>
                </div>

                <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 my-3 text-start small">
                    <strong class="d-block mb-1"><i class="bi bi-bounding-box-circles me-1 text-info"></i> Influencing Symptoms Detected:</strong>
                    <div class="d-flex flex-wrap gap-1 mt-1">{influencing}</div>
                </div>

                {runner_ups_html}

                <a href="/disease_detail.php?name={pred_name}" class="btn btn-outline-info rounded-pill px-4 w-100 my-2">
                    <i class="bi bi-book me-1"></i> Learn More About {pred_name}
                </a>

                <div class="disclaimer-banner small text-start my-3">
                    <h6 class="fw-bold mb-1 text-warning"><i class="bi bi-shield-exclamation me-1"></i> Medical Disclaimer</h6>
                    {result.get('disclaimer')}
                </div>
            </div>
            """

    content = f"""
    <div class="row py-3">
        <div class="col-lg-12 text-center mb-4">
            <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">AI SYMPTOM CHECKER</span>
            <h1 class="display-5 fw-extrabold mb-2">Intelligent Multi-Symptom Disease Prediction</h1>
            <p class="lead text-muted mx-auto" style="max-width: 750px;">
                Select your experienced indicators using our tactile symptom tiles. Unselected tiles are matte; selected tiles become glossy with real-time feedback.
            </p>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-7">
            <div class="card-custom p-4 p-md-5">
                <h4 class="fw-bold mb-3 d-flex align-items-center">
                    <i class="bi bi-grid-3x3-gap-fill text-info me-2"></i> Select Present Symptoms
                </h4>
                <p class="small text-muted mb-4">Click tiles to toggle symptom presence:</p>
                <form method="POST" action="/prediction">
                    {tiles_html}
                    <div class="disclaimer-banner my-4">
                        <i class="bi bi-info-circle-fill me-1 text-info"></i> Predictions are generated using an automated Random Forest classifier. Results are strictly educational.
                    </div>
                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                        <i class="bi bi-cpu-fill me-2"></i> Submit Symptoms & Predict Condition
                    </button>
                </form>
            </div>
        </div>
        <div class="col-lg-5">
            {res_card if res_card else '''
            <div class="card-custom p-5 text-center h-100 d-flex flex-column justify-content-center align-items-center">
                <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                <h4 class="fw-bold">Awaiting Symptom Selection</h4>
                <p class="text-muted small max-w-sm mb-0">
                    Click on the symptom tiles on the left to select your active indicators, then click "Submit Symptoms" to evaluate with our AI diagnostic model.
                </p>
            </div>
            '''}
        </div>
    </div>
    """
    return render_page(content)

@app.route('/assessment', methods=['GET', 'POST'])
@app.route('/assessment.php', methods=['GET', 'POST'])
@app.route('/api/assessment', methods=['GET', 'POST'])
def assessment():
    result = None
    disease_type = request.form.get('disease_type', 'diabetes') if request.method == 'POST' else request.args.get('type', 'diabetes')
    
    if request.method == 'POST':
        if disease_type == 'diabetes':
            input_data = {
                'Pregnancies': float(request.form.get('Pregnancies', 1)),
                'Glucose': float(request.form.get('Glucose', 120)),
                'BloodPressure': float(request.form.get('BloodPressure', 75)),
                'SkinThickness': float(request.form.get('SkinThickness', 22)),
                'Insulin': float(request.form.get('Insulin', 80)),
                'BMI': float(request.form.get('BMI', 28.4)),
                'DiabetesPedigreeFunction': float(request.form.get('DiabetesPedigreeFunction', 0.47)),
                'Age': float(request.form.get('Age', 42))
            }
        elif disease_type == 'heart':
            input_data = {
                'age': float(request.form.get('age', 52)),
                'sex': int(request.form.get('sex', 1)),
                'cp': int(request.form.get('cp', 0)),
                'trestbps': float(request.form.get('trestbps', 132)),
                'chol': float(request.form.get('chol', 235)),
                'fbs': int(request.form.get('fbs', 0)),
                'restecg': int(request.form.get('restecg', 0)),
                'thalach': float(request.form.get('thalach', 150)),
                'exang': int(request.form.get('exang', 0)),
                'oldpeak': float(request.form.get('oldpeak', 1.2)),
                'slope': int(request.form.get('slope', 1)),
                'ca': int(request.form.get('ca', 0)),
                'thal': int(request.form.get('thal', 2))
            }
        elif disease_type == 'hypertension':
            input_data = {
                'systolic': float(request.form.get('systolic', 135)),
                'diastolic': float(request.form.get('diastolic', 88)),
                'Age': float(request.form.get('Age', 48)),
                'BMI': float(request.form.get('BMI', 27.2)),
                'sodium': float(request.form.get('sodium', 2800)),
                'smoking': int(request.form.get('smoking', 0)),
                'stress': int(request.form.get('stress', 1))
            }
        elif disease_type == 'respiratory':
            input_data = {
                'Age': float(request.form.get('Age', 50)),
                'pack_years': float(request.form.get('pack_years', 8)),
                'dyspnea': int(request.form.get('dyspnea', 1)),
                'cough_weeks': float(request.form.get('cough_weeks', 3)),
                'env_exposure': int(request.form.get('env_exposure', 1))
            }
        else: # lifestyle
            input_data = {
                'age_group': int(request.form.get('age_group', 2)),
                'smoking': int(request.form.get('smoking', 0)),
                'physical_activity': int(request.form.get('physical_activity', 1)),
                'family_history': int(request.form.get('family_history', 0)),
                'bp_category': int(request.form.get('bp_category', 1)),
                'bmi_category': int(request.form.get('bmi_category', 2)),
                'blood_sugar': int(request.form.get('blood_sugar', 1)),
                'cholesterol': int(request.form.get('cholesterol', 1)),
                'diet_quality': int(request.form.get('diet_quality', 1)),
                'sleep_stress': int(request.form.get('sleep_stress', 1)),
                'chronic_conditions': int(request.form.get('chronic_conditions', 0))
            }
            
        result = predict_disease(disease_type, input_data)
        result['input_data'] = input_data
        result['disease_type'] = disease_type
        session['latest_assessment'] = result
        history = session.get('history', [])
        history.append({
            'disease': result.get('disease'),
            'risk_level': result.get('risk_level'),
            'probability': result.get('probability'),
            'timestamp': 'Recent'
        })
        session['history'] = history

    result_card = ""
    if result:
        risk_color = "success" if result.get('risk_level') == "LOW" else ("warning" if result.get('risk_level') == "MODERATE" else "danger")
        recs_html = "".join([f"<li class='mb-2'>{r}</li>" for r in result.get('recommendations', [])])
        feat_html = "".join([
            f"<div class='mb-2'><div class='d-flex justify-content-between small text-muted'><span>{k}</span><span>{round(v*100, 1)}%</span></div><div class='progress' style='height:6px;'><div class='progress-bar bg-info' style='width:{min(100, v*100)}%'></div></div></div>"
            for k, v in list(result.get('feature_importance', {}).items())[:5]
        ])
        
        result_card = f"""
        <div class="card-custom p-4 p-md-5 my-4 border-{risk_color}">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="badge bg-secondary">{result.get('disease')}</span>
                <span class="badge bg-{risk_color} fs-6 px-3 py-1">Risk Level: {result.get('risk_level')}</span>
            </div>
            <div class="text-center my-4">
                <h1 class="display-3 fw-extrabold text-{risk_color} mb-1">{result.get('probability')}%</h1>
                <p class="text-muted small">AI Model Statistical Risk Probability</p>
            </div>
            <div class="row g-4 my-2">
                <div class="col-md-6">
                    <h5 class="fw-bold mb-3"><i class="bi bi-bar-chart-line text-info me-2"></i>Explainable AI (Top Risk Drivers)</h5>
                    {feat_html}
                </div>
                <div class="col-md-6">
                    <h5 class="fw-bold mb-3"><i class="bi bi-check-circle text-success me-2"></i>Personalized Guidance</h5>
                    <ul class="text-muted small ps-3 mb-0">{recs_html}</ul>
                </div>
            </div>
            <div class="disclaimer-banner small my-3">{result.get('disclaimer')}</div>
            <div class="d-flex flex-wrap gap-2 mt-4">
                <a href="/simulator?type={disease_type}" class="btn btn-outline-info rounded-pill px-4">
                    <i class="bi bi-sliders me-1"></i> Open in What-If Simulator
                </a>
                <a href="/report" class="btn btn-outline-secondary rounded-pill px-4">
                    <i class="bi bi-printer me-1"></i> View Printable Summary
                </a>
                <a href="/assessment" class="btn btn-primary-custom rounded-pill px-4 ms-auto">New Assessment</a>
            </div>
        </div>
        """

    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <div class="card-custom p-4 p-md-5">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="bg-info bg-opacity-10 p-3 rounded-circle text-info me-3">
                        <i class="bi bi-clipboard-pulse fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0">Clinical Health Risk Assessment</h3>
                        <p class="text-muted small mb-0">Evaluate quantitative biomarkers against trained Scikit-Learn classification pipelines</p>
                    </div>
                </div>

                <form method="POST" action="/assessment">
                    <div class="mb-4 bg-card-subtle p-3 rounded-3 border border-secondary border-opacity-25">
                        <label class="form-label fw-bold fs-6 mb-2">
                            <i class="bi bi-activity text-info me-2"></i>Select Assessment Target Condition
                        </label>
                        <select class="form-select" id="disease_type" name="disease_type" onchange="toggleFields(this.value)">
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>1. Diabetes Risk Assessment (Pima Clinical Model)</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>2. Heart Disease Risk Assessment (Cleveland Cardiac Model)</option>
                            <option value="hypertension" {'selected' if disease_type == 'hypertension' else ''}>3. Hypertension Risk Assessment (Hemodynamic Model)</option>
                            <option value="respiratory" {'selected' if disease_type == 'respiratory' else ''}>4. Chronic Respiratory Risk Assessment (Spirometry & Exposure)</option>
                            <option value="lifestyle" {'selected' if disease_type == 'lifestyle' else ''}>5. Comprehensive 11-Factor Health & Lifestyle Assessment</option>
                        </select>
                    </div>

                    <!-- 1. Diabetes Fields -->
                    <div id="diabetes_fields" class="condition-section" style="display: {'block' if disease_type == 'diabetes' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Biomarkers (Pima Clinical Model)</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small">Glucose Level (mg/dL)</label>
                                <input type="number" step="0.1" name="Glucose" class="form-control" value="120">
                                <small class="text-muted">Normal fasting: 70-140 mg/dL</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="28.4">
                                <small class="text-muted">Normal: 18.5-24.9</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="BloodPressure" class="form-control" value="75">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Age (Years)</label>
                                <input type="number" name="Age" class="form-control" value="42">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Pregnancies</label>
                                <input type="number" name="Pregnancies" class="form-control" value="1">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Insulin Level (mu U/ml)</label>
                                <input type="number" step="0.1" name="Insulin" class="form-control" value="80">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Skin Thickness (mm)</label>
                                <input type="number" step="0.1" name="SkinThickness" class="form-control" value="22">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Diabetes Pedigree Function</label>
                                <input type="number" step="0.001" name="DiabetesPedigreeFunction" class="form-control" value="0.47">
                            </div>
                        </div>
                    </div>

                    <!-- 2. Heart Fields -->
                    <div id="heart_fields" class="condition-section" style="display: {'block' if disease_type == 'heart' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Cardiovascular Biomarkers (Cleveland Cardiac Model)</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small">Age (Years)</label>
                                <input type="number" name="age" class="form-control" value="52">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Sex</label>
                                <select name="sex" class="form-select"><option value="1">Male</option><option value="0">Female</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Chest Pain Type</label>
                                <select name="cp" class="form-select"><option value="0">Typical Angina (0)</option><option value="1">Atypical Angina (1)</option><option value="2">Non-anginal Pain (2)</option><option value="3">Asymptomatic (3)</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Resting Blood Pressure (mm Hg)</label>
                                <input type="number" step="0.1" name="trestbps" class="form-control" value="132">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Serum Cholesterol (mg/dL)</label>
                                <input type="number" step="0.1" name="chol" class="form-control" value="235">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Max Heart Rate Achieved</label>
                                <input type="number" step="0.1" name="thalach" class="form-control" value="150">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Exercise-Induced Angina</label>
                                <select name="exang" class="form-select"><option value="0">No</option><option value="1">Yes</option></select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">ST Depression (Oldpeak)</label>
                                <input type="number" step="0.1" name="oldpeak" class="form-control" value="1.2">
                            </div>
                        </div>
                    </div>

                    <!-- 3. Hypertension Fields -->
                    <div id="hypertension_fields" class="condition-section" style="display: {'block' if disease_type == 'hypertension' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-speedometer2 me-2 text-warning"></i>Hypertension & Hemodynamic Biomarkers</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small">Systolic Blood Pressure (mm Hg)</label>
                                <input type="number" step="1" name="systolic" class="form-control" value="135">
                                <small class="text-muted">Target: &lt;120 mm Hg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Diastolic Blood Pressure (mm Hg)</label>
                                <input type="number" step="1" name="diastolic" class="form-control" value="88">
                                <small class="text-muted">Target: &lt;80 mm Hg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Body Mass Index (BMI)</label>
                                <input type="number" step="0.1" name="BMI" class="form-control" value="27.2">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Daily Dietary Sodium (mg/day)</label>
                                <input type="number" step="50" name="sodium" class="form-control" value="2800">
                                <small class="text-muted">AHA recommendation: &lt;2,300 mg</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Smoking Status</label>
                                <select name="smoking" class="form-select">
                                    <option value="0">Non-Smoker</option>
                                    <option value="1">Occasional / Former</option>
                                    <option value="2">Regular Smoker</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Perceived Stress Level</label>
                                <select name="stress" class="form-select">
                                    <option value="0">Low Stress</option>
                                    <option value="1" selected>Moderate Stress</option>
                                    <option value="2">High / Chronic Stress</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- 4. Respiratory Fields -->
                    <div id="respiratory_fields" class="condition-section" style="display: {'block' if disease_type == 'respiratory' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-wind me-2 text-primary"></i>Respiratory & Pulmonary Risk Profile</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small">Smoking Pack-Years</label>
                                <input type="number" step="0.5" name="pack_years" class="form-control" value="8">
                                <small class="text-muted">Packs per day &times; years smoked</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Dyspnea / Breathlessness Scale</label>
                                <select name="dyspnea" class="form-select">
                                    <option value="0">Grade 0: None except strenuous exercise</option>
                                    <option value="1" selected>Grade 1: Short of breath when hurrying</option>
                                    <option value="2">Grade 2: Walks slower than peers due to breathlessness</option>
                                    <option value="3">Grade 3: Stops for breath after 100 meters</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Chronic Cough Duration (Weeks)</label>
                                <input type="number" step="1" name="cough_weeks" class="form-control" value="3">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Environmental / Dust Exposure</label>
                                <select name="env_exposure" class="form-select">
                                    <option value="0">Low / Clean indoor</option>
                                    <option value="1" selected>Moderate (Urban traffic / occasional dust)</option>
                                    <option value="2">High (Occupational chemical, fumes, heavy biomass)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- 5. Lifestyle Multi-Risk Fields (11 Factors) -->
                    <div id="lifestyle_fields" class="condition-section" style="display: {'block' if disease_type == 'lifestyle' else 'none'};">
                        <h5 class="fw-bold text-info mb-3"><i class="bi bi-person-lines-fill me-2 text-success"></i>11-Factor Health &amp; Lifestyle Multi-Risk Assessment</h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small">1. Age Group</label>
                                <select name="age_group" class="form-select">
                                    <option value="0">Under 30 years</option>
                                    <option value="1">30 - 45 years</option>
                                    <option value="2" selected>46 - 60 years</option>
                                    <option value="3">Over 60 years</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">2. Smoking &amp; Tobacco</label>
                                <select name="smoking" class="form-select">
                                    <option value="0">Never smoked</option>
                                    <option value="1">Former smoker</option>
                                    <option value="2">Current smoker (&lt; 1 pack/day)</option>
                                    <option value="3">Heavy smoker (&gt; 1 pack/day)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">3. Physical Activity Level</label>
                                <select name="physical_activity" class="form-select">
                                    <option value="3">Active (&gt; 150 mins/week)</option>
                                    <option value="2">Moderate (60 - 150 mins/week)</option>
                                    <option value="1" selected>Light (&lt; 60 mins/week)</option>
                                    <option value="0">Sedentary (No regular exercise)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">4. Family History of Chronic Disease</label>
                                <select name="family_history" class="form-select">
                                    <option value="0">No known family history</option>
                                    <option value="1">One first-degree relative</option>
                                    <option value="2">Multiple first-degree relatives</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">5. Blood Pressure Category</label>
                                <select name="bp_category" class="form-select">
                                    <option value="0">Optimal (&lt; 120/80 mm Hg)</option>
                                    <option value="1" selected>Elevated (120-129 / &lt;80)</option>
                                    <option value="2">Stage 1 Hypertension (130-139 / 80-89)</option>
                                    <option value="3">Stage 2 Hypertension (&ge; 140/90)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">6. BMI / Weight Category</label>
                                <select name="bmi_category" class="form-select">
                                    <option value="0">Normal weight (18.5 - 24.9)</option>
                                    <option value="1">Overweight (25.0 - 29.9)</option>
                                    <option value="2" selected>Obesity Class I (30.0 - 34.9)</option>
                                    <option value="3">Obesity Class II/III (&ge; 35.0)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">7. Blood Sugar Level</label>
                                <select name="blood_sugar" class="form-select">
                                    <option value="0">Normal (&lt; 100 mg/dL fasting)</option>
                                    <option value="1" selected>Impaired / Prediabetic (100 - 125 mg/dL)</option>
                                    <option value="2">Elevated / Diabetic range (&ge; 126 mg/dL)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">8. Cholesterol Profile</label>
                                <select name="cholesterol" class="form-select">
                                    <option value="0">Desirable (&lt; 200 mg/dL)</option>
                                    <option value="1" selected>Borderline high (200 - 239 mg/dL)</option>
                                    <option value="2">High (&ge; 240 mg/dL)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">9. Diet &amp; Nutritional Quality</label>
                                <select name="diet_quality" class="form-select">
                                    <option value="0">Healthy / Whole-food balanced</option>
                                    <option value="1" selected>Average / Mixed diet</option>
                                    <option value="2">High in processed foods &amp; sugar</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">10. Stress &amp; Sleep Health</label>
                                <select name="sleep_stress" class="form-select">
                                    <option value="0">Restful sleep (7-9h) &amp; low stress</option>
                                    <option value="1" selected>Occasional insomnia / moderate stress</option>
                                    <option value="2">Chronic short sleep (&lt; 6h) &amp; high stress</option>
                                </select>
                            </div>
                            <div class="col-md-12">
                                <label class="form-label small">11. Existing Chronic Conditions</label>
                                <select name="chronic_conditions" class="form-select">
                                    <option value="0">None diagnosed</option>
                                    <option value="1">One chronic condition managed</option>
                                    <option value="2">Multiple chronic conditions</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="disclaimer-banner my-3 small">
                        <i class="bi bi-info-circle-fill me-1"></i> Data will be evaluated using our trained machine learning pipeline. Results are informational and educational only.
                    </div>

                    <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                        <i class="bi bi-cpu-fill me-2"></i> Compute AI Health Risk Assessment
                    </button>
                </form>

                <script>
                function toggleFields(val) {{
                    var ids = ['diabetes_fields', 'heart_fields', 'hypertension_fields', 'respiratory_fields', 'lifestyle_fields'];
                    ids.forEach(function(id) {{
                        var el = document.getElementById(id);
                        if (el) {{
                            el.style.display = (id === val + '_fields') ? 'block' : 'none';
                        }}
                    }});
                }}
                </script>
            </div>
            {result_card}
        </div>
    </div>
    """
    return render_page(content)

@app.route('/simulator', methods=['GET', 'POST'])
@app.route('/simulator.php', methods=['GET', 'POST'])
@app.route('/api/simulator', methods=['GET', 'POST'])
def simulator():
    disease_type = request.form.get('disease_type', 'diabetes') if request.method == 'POST' else request.args.get('type', 'diabetes')
    
    # 5 Models Support with Fixed Sliders & Exact Case Matching
    if disease_type == 'diabetes':
        glucose = float(request.form.get('Glucose', 145))
        bmi = float(request.form.get('BMI', 31.0))
        bp = float(request.form.get('BloodPressure', 82))
        age = float(request.form.get('Age') or request.form.get('age', 45))
        input_data = {
            'Pregnancies': 2,
            'Glucose': glucose,
            'BloodPressure': bp,
            'SkinThickness': 25,
            'Insulin': 90,
            'BMI': bmi,
            'DiabetesPedigreeFunction': 0.52,
            'Age': age
        }
    elif disease_type == 'heart':
        chol = float(request.form.get('chol', 250))
        trestbps = float(request.form.get('trestbps', 140))
        thalach = float(request.form.get('thalach', 130))
        age = float(request.form.get('age') or request.form.get('Age', 58))
        input_data = {
            'age': age,
            'sex': 1,
            'cp': 0,
            'trestbps': trestbps,
            'chol': chol,
            'fbs': 0,
            'restecg': 0,
            'thalach': thalach,
            'exang': 0,
            'oldpeak': 1.0,
            'slope': 1,
            'ca': 0,
            'thal': 2
        }
    elif disease_type == 'hypertension':
        systolic = float(request.form.get('systolic', 145))
        diastolic = float(request.form.get('diastolic', 92))
        bmi = float(request.form.get('BMI', 29.5))
        sodium = float(request.form.get('sodium', 3400))
        age = float(request.form.get('Age') or request.form.get('age', 52))
        input_data = {
            'systolic': systolic,
            'diastolic': diastolic,
            'BMI': bmi,
            'sodium': sodium,
            'Age': age,
            'smoking': 0,
            'stress': 1
        }
    elif disease_type == 'respiratory':
        pack_years = float(request.form.get('pack_years', 18))
        dyspnea = int(request.form.get('dyspnea', 2))
        cough_weeks = float(request.form.get('cough_weeks', 4))
        age = float(request.form.get('Age') or request.form.get('age', 56))
        input_data = {
            'Age': age,
            'pack_years': pack_years,
            'dyspnea': dyspnea,
            'cough_weeks': cough_weeks,
            'env_exposure': 1
        }
    else: # lifestyle
        activity = int(request.form.get('physical_activity', 1))
        sleep_stress = int(request.form.get('sleep_stress', 2))
        diet = int(request.form.get('diet_quality', 1))
        age = float(request.form.get('Age') or request.form.get('age', 46))
        input_data = {
            'age_group': 2 if age < 55 else 3,
            'smoking': 0,
            'physical_activity': activity,
            'family_history': 1,
            'bp_category': 1,
            'bmi_category': 2,
            'blood_sugar': 1,
            'cholesterol': 1,
            'diet_quality': diet,
            'sleep_stress': sleep_stress,
            'chronic_conditions': 0
        }

    sim_result = predict_disease(disease_type, input_data)
    risk_color = "success" if sim_result['risk_level'] == "LOW" else ("warning" if sim_result['risk_level'] == "MODERATE" else "danger")
    
    # Sliders markup based on selected model
    if disease_type == 'diabetes':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Fasting Glucose (mg/dL)</label>
                <span id="val_Glucose" class="slider-val-badge bg-info text-dark">{int(glucose)}</span>
            </div>
            <input type="range" class="form-range" name="Glucose" id="slider_glucose" data-target="Glucose" min="70" max="250" value="{int(glucose)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Body Mass Index (BMI)</label>
                <span id="val_BMI" class="slider-val-badge bg-info text-dark">{bmi:.1f}</span>
            </div>
            <input type="range" class="form-range" name="BMI" id="slider_bmi" data-target="BMI" min="15" max="50" step="0.5" value="{bmi}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Blood Pressure (mm Hg)</label>
                <span id="val_BloodPressure" class="slider-val-badge bg-info text-dark">{int(bp)}</span>
            </div>
            <input type="range" class="form-range" name="BloodPressure" id="slider_bp" data-target="BloodPressure" min="50" max="130" value="{int(bp)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'heart':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Serum Cholesterol (mg/dL)</label>
                <span id="val_chol" class="slider-val-badge bg-info text-dark">{int(chol)}</span>
            </div>
            <input type="range" class="form-range" name="chol" id="slider_chol" data-target="chol" min="120" max="400" value="{int(chol)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Resting Blood Pressure (mm Hg)</label>
                <span id="val_trestbps" class="slider-val-badge bg-info text-dark">{int(trestbps)}</span>
            </div>
            <input type="range" class="form-range" name="trestbps" id="slider_trestbps" data-target="trestbps" min="90" max="200" value="{int(trestbps)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Max Heart Rate (bpm)</label>
                <span id="val_thalach" class="slider-val-badge bg-info text-dark">{int(thalach)}</span>
            </div>
            <input type="range" class="form-range" name="thalach" id="slider_thalach" data-target="thalach" min="80" max="210" value="{int(thalach)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'hypertension':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Systolic Blood Pressure (mm Hg)</label>
                <span id="val_systolic" class="slider-val-badge bg-info text-dark">{int(systolic)}</span>
            </div>
            <input type="range" class="form-range" name="systolic" id="slider_systolic" data-target="systolic" min="90" max="200" value="{int(systolic)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Diastolic Blood Pressure (mm Hg)</label>
                <span id="val_diastolic" class="slider-val-badge bg-info text-dark">{int(diastolic)}</span>
            </div>
            <input type="range" class="form-range" name="diastolic" id="slider_diastolic" data-target="diastolic" min="60" max="120" value="{int(diastolic)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Daily Sodium Intake (mg)</label>
                <span id="val_sodium" class="slider-val-badge bg-info text-dark">{int(sodium)}</span>
            </div>
            <input type="range" class="form-range" name="sodium" id="slider_sodium" data-target="sodium" min="1000" max="5000" step="50" value="{int(sodium)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    elif disease_type == 'respiratory':
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Smoking Pack-Years</label>
                <span id="val_pack_years" class="slider-val-badge bg-info text-dark">{int(pack_years)}</span>
            </div>
            <input type="range" class="form-range" name="pack_years" id="slider_pack_years" data-target="pack_years" min="0" max="50" value="{int(pack_years)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Dyspnea Breathlessness Grade (0-3)</label>
                <span id="val_dyspnea" class="slider-val-badge bg-info text-dark">{int(dyspnea)}</span>
            </div>
            <input type="range" class="form-range" name="dyspnea" id="slider_dyspnea" data-target="dyspnea" min="0" max="3" value="{int(dyspnea)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Chronic Cough Duration (Weeks)</label>
                <span id="val_cough_weeks" class="slider-val-badge bg-info text-dark">{int(cough_weeks)}</span>
            </div>
            <input type="range" class="form-range" name="cough_weeks" id="slider_cough_weeks" data-target="cough_weeks" min="0" max="12" value="{int(cough_weeks)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """
    else: # lifestyle
        sliders_markup = f"""
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Physical Activity Grade (0=Sedentary, 3=High)</label>
                <span id="val_physical_activity" class="slider-val-badge bg-info text-dark">{int(activity)}</span>
            </div>
            <input type="range" class="form-range" name="physical_activity" id="slider_activity" data-target="physical_activity" min="0" max="3" value="{int(activity)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Sleep &amp; Stress Scale (0=Optimal, 2=Poor)</label>
                <span id="val_sleep_stress" class="slider-val-badge bg-info text-dark">{int(sleep_stress)}</span>
            </div>
            <input type="range" class="form-range" name="sleep_stress" id="slider_sleep_stress" data-target="sleep_stress" min="0" max="2" value="{int(sleep_stress)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Diet Quality (0=Balanced, 2=Unhealthy)</label>
                <span id="val_diet_quality" class="slider-val-badge bg-info text-dark">{int(diet)}</span>
            </div>
            <input type="range" class="form-range" name="diet_quality" id="slider_diet" data-target="diet_quality" min="0" max="2" value="{int(diet)}">
        </div>
        <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="form-label small fw-bold mb-0">Age (Years)</label>
                <span id="val_Age" class="slider-val-badge bg-info text-dark">{int(age)}</span>
            </div>
            <input type="range" class="form-range" name="Age" id="slider_age" data-target="Age" min="20" max="85" value="{int(age)}">
        </div>
        """

    content = f"""
    <div class="row justify-content-center py-4">
        <div class="col-lg-10">
            <div class="card-custom p-4 p-md-5 mb-4">
                <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                    <div class="bg-success bg-opacity-10 p-3 rounded-circle text-success me-3">
                        <i class="bi bi-sliders fs-2"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold mb-0">What-If Clinical Risk Simulator</h3>
                        <p class="text-muted small mb-0">Simulate lifestyle or biometric adjustments to observe real-time risk score changes</p>
                    </div>
                </div>

                <form method="POST" action="/simulator">
                    <div class="mb-4">
                        <label class="form-label fw-bold">Select Target Condition Model:</label>
                        <select name="disease_type" class="form-select" onchange="this.form.submit()">
                            <option value="diabetes" {'selected' if disease_type == 'diabetes' else ''}>1. Diabetes Risk Simulator (Pima Clinical Model)</option>
                            <option value="heart" {'selected' if disease_type == 'heart' else ''}>2. Heart Disease Risk Simulator (Cleveland Cardiac Model)</option>
                            <option value="hypertension" {'selected' if disease_type == 'hypertension' else ''}>3. Hypertension Risk Simulator (Hemodynamic Model)</option>
                            <option value="respiratory" {'selected' if disease_type == 'respiratory' else ''}>4. Chronic Respiratory Risk Simulator</option>
                            <option value="lifestyle" {'selected' if disease_type == 'lifestyle' else ''}>5. Multi-Factor Lifestyle Risk Simulator</option>
                        </select>
                    </div>

                    <div class="row g-4 my-2">
                        {sliders_markup}
                    </div>

                    <button type="submit" class="btn btn-primary-custom w-100 py-3 mt-3">
                        <i class="bi bi-arrow-repeat me-2"></i> Recalculate Simulated Risk Score
                    </button>
                </form>

                <div class="card-custom p-4 text-center border-{risk_color} mt-4">
                    <span class="badge bg-secondary mb-2">SIMULATED RISK OUTPUT</span>
                    <h3 class="fw-bold">{sim_result.get('disease')}</h3>
                    <h1 class="display-3 fw-extrabold text-{risk_color} my-2">{sim_result.get('probability')}%</h1>
                    <span class="badge bg-{risk_color} fs-6 px-3 py-1">Risk Category: {sim_result.get('risk_level')}</span>
                    <div class="disclaimer-banner small text-start my-3">{sim_result.get('disclaimer')}</div>
                </div>
            </div>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/result')
@app.route('/result.php')
def result():
    return redirect('/assessment')

@app.route('/history')
@app.route('/history.php')
def history():
    records = session.get('history', [])
    rows = "".join([f"<tr><td>{r['disease']}</td><td><span class='badge bg-info'>{r['risk_level']}</span></td><td>{r['probability']}%</td><td>{r['timestamp']}</td></tr>" for r in records])
    if not rows:
        rows = "<tr><td colspan='4' class='text-center text-muted'>No previous assessments recorded in this session.</td></tr>"
    content = f"""
    <div class="card-custom p-4 p-md-5 my-4">
        <h3 class="fw-bold text-white mb-3">Assessment History Log</h3>
        <table class="table table-dark table-hover"><thead><tr><th>Condition</th><th>Risk Level</th><th>Probability</th><th>Time</th></tr></thead><tbody>{rows}</tbody></table>
        <a href="/assessment" class="btn btn-primary-custom rounded-pill mt-3">New Assessment</a>
    </div>
    """
    return render_page(content)

@app.route('/report')
@app.route('/report.php')
def report():
    res = session.get('latest_assessment', {
        'disease': 'Diabetes Risk Assessment',
        'risk_level': 'HIGH',
        'probability': 97.4,
        'recommendations': ['Maintain low glycemic diet.', 'Regular physical activity (30 mins/day).', 'Periodic blood glucose screening.'],
        'disclaimer': 'Educational informational report only. Consult a qualified medical practitioner.'
    })
    recs = "".join([f"<li class='mb-2'>{r}</li>" for r in res.get('recommendations', [])])
    return f"""
    <!DOCTYPE html><html><head><title>Health Assessment Report</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-4 p-md-5 bg-light text-dark">
        <div class="container" style="max-width:800px;background:#fff;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <h2 class="fw-bold mb-0">AI Healthcare Clinical Assessment Report</h2>
                <button onclick="window.print()" class="btn btn-primary rounded-pill px-4">Print / Save PDF</button>
            </div>
            <h4>Condition: {res.get('disease')}</h4>
            <p><strong>Predicted Risk Level:</strong> <span class="badge bg-danger">{res.get('risk_level')}</span></p>
            <p><strong>Statistical Probability Score:</strong> {res.get('probability')}%</p>
            <h5 class="mt-4">Personalized Recommendations:</h5>
            <ul>{recs}</ul>
            <div class="alert alert-warning mt-4">{res.get('disclaimer')}</div>
            <a href="/assessment" class="btn btn-outline-secondary mt-3">Back to Platform</a>
        </div>
    </body></html>
    """

@app.route('/diseases')
@app.route('/diseases.php')
@app.route('/api/diseases')
def diseases():
    items_html = "".join([f'<div class="col-md-6 col-lg-4"><div class="card-custom p-4 h-100"><span class="badge bg-info bg-opacity-20 text-info mb-2">{d["category"]}</span><h4 class="fw-bold text-white mb-2">{d["name"]}</h4><p class="small text-muted mb-3">{d["short_description"][:90]}...</p><a href="/disease/{d["id"]}" class="btn btn-outline-info btn-sm rounded-pill w-100">View Details</a></div></div>' for d in DISEASES_DB])
    content = f"""
    <h2 class="fw-bold text-white mb-4 text-center">Disease Information Database (65 Conditions)</h2>
    <div class="row g-4">{items_html}</div>
    """
    return render_page(content)

@app.route('/disease/<int:did>')
@app.route('/disease_detail.php')
@app.route('/api/disease/<int:did>')
def disease_detail(did=1):
    name_param = request.args.get('name', '').strip().lower()
    if name_param:
        disease = next((d for d in DISEASES_DB if name_param in d['name'].lower()), None)
        if disease:
            did = disease['id']
    if not did or did == 1:
        did = request.args.get('id', type=int) or (disease['id'] if 'disease' in locals() and disease else 1)
    disease = next((d for d in DISEASES_DB if d['id'] == did), DISEASES_DB[0])
    content = f"""
    <div class="card-custom p-4 p-md-5 my-3">
        <span class="badge bg-info text-dark mb-2">{disease['category']}</span>
        <h1 class="display-5 fw-bold text-white mb-3">{disease['name']}</h1>
        <p class="lead text-muted mb-4">{disease['short_description']}</p>
        
        <h5 class="fw-bold text-white mb-2">Causes</h5>
        <p class="text-muted small mb-4">{disease['causes']}</p>
        
        <h5 class="fw-bold text-white mb-2">Risk Factors</h5>
        <p class="text-muted small mb-4">{disease['risk_factors']}</p>

        <h5 class="fw-bold text-white mb-2">Prevention</h5>
        <p class="text-muted small mb-4">{disease['prevention']}</p>

        <h5 class="fw-bold text-white mb-2">Management & Care</h5>
        <p class="text-muted small mb-4">{disease['management']}</p>
    </div>
    """
    return render_page(content)

@app.route('/symptoms')
@app.route('/symptoms_guide.php')
@app.route('/api/symptoms')
def symptoms_guide():
    symptoms_list = [
        {"key": "fatigue", "name": "Chronic Lethargy & Fatigue", "cat": "General", "icon": "bi-battery-half", "desc": "Persistent extreme physical exhaustion not resolved by rest.", "cond": "Anemia, Chronic Kidney Disease, Diabetes, Hypothyroidism"},
        {"key": "fever", "name": "Fever (>100.4°F / 38°C)", "cat": "General", "icon": "bi-thermometer-high", "desc": "Elevated core temperature signaling acute immune response or infection.", "cond": "Pneumonia, COVID-19, Malaria, Typhoid, UTI"},
        {"key": "chills", "name": "Severe Chills & Rigors", "cat": "General", "icon": "bi-snow", "desc": "Involuntary muscular shivering accompanied by intense cold sensations.", "cond": "Pneumonia, Malaria, Sepsis, Pyelonephritis"},
        {"key": "weight_loss", "name": "Unexplained Rapid Weight Loss", "cat": "General", "icon": "bi-graph-down-arrow", "desc": "Losing >5% body weight unintentionally without dietary changes.", "cond": "Type 1 Diabetes, Hyperthyroidism, Tuberculosis"},
        {"key": "sweats", "name": "Drenching Night Sweats", "cat": "General", "icon": "bi-droplet-half", "desc": "Repeated episodes of extreme perspiration during sleep.", "cond": "Tuberculosis, Malaria, Hyperthyroidism"},
        {"key": "localized_swelling", "name": "Localized Tissue Swelling / Edema", "cat": "General", "icon": "bi-bounding-box", "desc": "Visible accumulation of fluid within soft tissues or joints.", "cond": "Gout, Rheumatoid Arthritis, Urticaria (Hives), Muscle Strain"},
        {"key": "shortness_of_breath", "name": "Shortness of Breath (Dyspnea)", "cat": "Respiratory", "icon": "bi-wind", "desc": "Labored respiration, air hunger, or inability to complete a breath.", "cond": "Asthma, COPD, Pneumonia, Heart Failure"},
        {"key": "cough_with_sputum", "name": "Persistent Productive Cough", "cat": "Respiratory", "icon": "bi-lungs", "desc": "Cough producing phlegm or mucus lasting longer than two weeks.", "cond": "Bacterial Pneumonia, Chronic Bronchitis, Asthma"},
        {"key": "dry_cough", "name": "Dry Non-Productive Cough", "cat": "Respiratory", "icon": "bi-soundwave", "desc": "Tickling persistent cough that produces no phlegm.", "cond": "Common Cold, Asthma, COVID-19"},
        {"key": "wheezing", "name": "Respiratory Wheezing", "cat": "Respiratory", "icon": "bi-soundwave", "desc": "Whistling expiratory sound caused by narrowed bronchial passages.", "cond": "Bronchial Asthma, COPD, Allergic Bronchospasm"},
        {"key": "hemoptysis", "name": "Hemoptysis (Coughing Blood)", "cat": "Respiratory", "icon": "bi-exclamation-octagon", "desc": "Expectoration of blood or blood-tinged sputum from airways.", "cond": "Tuberculosis, Severe Pneumonia, Bronchiectasis"},
        {"key": "runny_nose", "name": "Runny Nose (Rhinorrhea)", "cat": "Respiratory", "icon": "bi-droplet", "desc": "Excessive discharge of mucus from nasal passages.", "cond": "Common Cold, Allergic Rhinitis"},
        {"key": "sneezing", "name": "Frequent Sneezing", "cat": "Respiratory", "icon": "bi-emoji-dizzy", "desc": "Involuntary expulsion of air caused by nasal mucosal irritation.", "cond": "Allergic Rhinitis, Common Cold"},
        {"key": "sore_throat", "name": "Sore or Scratchy Throat", "cat": "Respiratory", "icon": "bi-chat-square-dots", "desc": "Pain, scratchiness, or pharyngeal irritation worsening with swallowing.", "cond": "Common Cold, Acute Bronchitis, GERD Acid Reflux"},
        {"key": "nasal_congestion", "name": "Sinus Pressure & Nasal Congestion", "cat": "Respiratory", "icon": "bi-shield-shaded", "desc": "Blockage of nasal passages accompanied by facial sinus pressure.", "cond": "Sinusitis, Allergic Rhinitis, Common Cold"},
        {"key": "chest_pain", "name": "Chest Pain / Tightness", "cat": "Cardiovascular", "icon": "bi-heart-pulse-fill", "desc": "Retrosternal pressure, squeezing, or discomfort in the chest.", "cond": "Coronary Artery Disease, Myocardial Infarction, Angina"},
        {"key": "high_blood_pressure", "name": "Hypertension Indicators", "cat": "Cardiovascular", "icon": "bi-speedometer2", "desc": "Sustained arterial pressure >= 130/80 mmHg or acute elevations.", "cond": "Essential Hypertension, Chronic Kidney Disease"},
        {"key": "palpitations", "name": "Rapid Heart Palpitations", "cat": "Cardiovascular", "icon": "bi-activity", "desc": "Awareness of pounding, fluttering, or rapid irregular heartbeats.", "cond": "Arrhythmias, Hyperthyroidism, Severe Anemia, Anxiety"},
        {"key": "leg_swelling", "name": "Lower Extremity / Ankle Edema", "cat": "Cardiovascular", "icon": "bi-water", "desc": "Dependent swelling of feet and ankles caused by fluid extravasation.", "cond": "Heart Failure, Chronic Kidney Disease"},
        {"key": "heartburn", "name": "Heartburn & Acid Reflux", "cat": "Digestive", "icon": "bi-fire", "desc": "Retrosternal burning sensation from stomach acid regurgitation.", "cond": "GERD, Gastritis, Peptic Ulcer Disease"},
        {"key": "abdominal_pain", "name": "Abdominal Pain & Cramping", "cat": "Digestive", "icon": "bi-bandaid", "desc": "Visceral or somatic discomfort localized to abdomen.", "cond": "Peptic Ulcer Disease, Gastroenteritis, IBS, Gallstones"},
        {"key": "nausea", "name": "Persistent Nausea", "cat": "Digestive", "icon": "bi-emoji-neutral", "desc": "Wave-like sensation of gastrointestinal distress and urge to vomit.", "cond": "Gastritis, Peptic Ulcer Disease, Gastroenteritis, Migraine"},
        {"key": "vomiting", "name": "Persistent Vomiting", "cat": "Digestive", "icon": "bi-exclamation-triangle", "desc": "Forceful expulsion of gastric contents through the mouth.", "cond": "Gastroenteritis, Peptic Ulcer Disease, Migraine, Gallstones"},
        {"key": "diarrhea", "name": "Frequent Watery Diarrhea", "cat": "Digestive", "icon": "bi-water", "desc": "Passage of loose watery stools three or more times daily.", "cond": "Gastroenteritis, Irritable Bowel Syndrome (IBS), Chronic Diarrhea"},
        {"key": "constipation", "name": "Chronic Constipation", "cat": "Digestive", "icon": "bi-slash-circle", "desc": "Infrequent, hard, dry bowel movements occurring <3 times per week.", "cond": "Chronic Constipation, IBS-C, Hypothyroidism"},
        {"key": "bloating", "name": "Abdominal Bloating & Gas", "cat": "Digestive", "icon": "bi-circle", "desc": "Sensation of tightness and visible distension in the abdomen.", "cond": "IBS, Chronic Constipation, SIBO"},
        {"key": "jaundice", "name": "Jaundice (Yellowing Eyes/Skin)", "cat": "Digestive", "icon": "bi-eye-fill", "desc": "Yellowish skin and scleral discoloration from elevated bilirubin.", "cond": "Hepatitis, Gallstones, Fatty Liver Disease"},
        {"key": "right_upper_quadrant_pain", "name": "Right Upper Quadrant Pain", "cat": "Digestive", "icon": "bi-geo-alt-fill", "desc": "Ache or sharp spasms beneath the right lower ribcage.", "cond": "Gallstones, Fatty Liver Disease, Acute Hepatitis"},
        {"key": "headache", "name": "Severe Throbbing Headache", "cat": "Neurological", "icon": "bi-headset-vr", "desc": "Intense cranial or temporal throbbing or pressure.", "cond": "Migraine, Severe Hypertension, Tension Cephalea"},
        {"key": "dizziness", "name": "Dizziness & Lightheadedness", "cat": "Neurological", "icon": "bi-arrow-repeat", "desc": "Faintness, unsteadiness, or false spinning sensation (vertigo).", "cond": "Anemia, Hypertension, Arrhythmia, Migraine"},
        {"key": "resting_tremor", "name": "Resting Hand / Limb Tremor", "cat": "Neurological", "icon": "bi-hand-index-thumb", "desc": "Rhythmic oscillatory movement of limbs while relaxed and resting.", "cond": "Parkinson's Disease, Essential Tremor"},
        {"key": "seizures", "name": "Involuntary Seizures", "cat": "Neurological", "icon": "bi-lightning-charge", "desc": "Uncontrolled cerebral electrical activity causing convulsions.", "cond": "Epilepsy, Severe Metabolic Disturbance, Stroke"},
        {"key": "memory_loss", "name": "Progressive Memory Decline", "cat": "Neurological", "icon": "bi-journal-medical", "desc": "Progressive short-term memory impairment and spatial disorientation.", "cond": "Alzheimer's Disease, Vascular Dementia, Vitamin B12 Deficiency"},
        {"key": "numbness_tingling", "name": "Numbness & Paresthesia", "cat": "Neurological", "icon": "bi-fingerprint", "desc": "Pins and needles or loss of protective sensation in limbs.", "cond": "Peripheral Neuropathy, Vitamin B12 Deficiency, PAD"},
        {"key": "blurred_vision", "name": "Blurred or Fluctuating Vision", "cat": "Neurological", "icon": "bi-eye-slash", "desc": "Loss of visual acuity or sharpness at standard distances.", "cond": "Diabetic Hyperglycemia, Retinopathy, Hypertension"},
        {"key": "loss_of_smell", "name": "Loss of Smell / Taste (Anosmia)", "cat": "Neurological", "icon": "bi-flower1", "desc": "Partial or total inability to perceive odors or taste.", "cond": "COVID-19, Severe Sinusitis"},
        {"key": "high_blood_sugar", "name": "High Blood Sugar & Polydipsia", "cat": "Endocrine", "icon": "bi-droplet", "desc": "Elevated blood glucose causing extreme thirst and frequent urination.", "cond": "Type 1 & Type 2 Diabetes, Metabolic Syndrome"},
        {"key": "excessive_hunger", "name": "Excessive Hunger (Polyphagia)", "cat": "Endocrine", "icon": "bi-cup-hot", "desc": "Insatiable appetite despite consuming adequate calories.", "cond": "Diabetes Mellitus, Hyperthyroidism"},
        {"key": "weight_gain", "name": "Unintentional Rapid Weight Gain", "cat": "Endocrine", "icon": "bi-graph-up-arrow", "desc": "Rapid unexplained increase in body weight.", "cond": "Hypothyroidism, Obesity, PCOS, Metabolic Syndrome"},
        {"key": "cold_intolerance", "name": "Cold Intolerance", "cat": "Endocrine", "icon": "bi-thermometer-snow", "desc": "Abnormal extreme sensitivity to cool ambient temperatures.", "cond": "Hypothyroidism (Hashimoto's), Severe Anemia"},
        {"key": "heat_intolerance", "name": "Heat Intolerance / Sweating", "cat": "Endocrine", "icon": "bi-thermometer-sun", "desc": "Excessive sweating and distress in moderately warm environments.", "cond": "Hyperthyroidism (Graves' Disease)"},
        {"key": "frequent_urination", "name": "Frequent Urination (Polyuria)", "cat": "Renal", "icon": "bi-clock-history", "desc": "Increased voiding frequency throughout the day and night.", "cond": "Diabetes Mellitus, UTI, Chronic Kidney Disease"},
        {"key": "dysuria", "name": "Dysuria (Painful Urination)", "cat": "Renal", "icon": "bi-shield-exclamation", "desc": "Burning or stinging discomfort in urethra while passing urine.", "cond": "Urinary Tract Infection (UTI), Kidney Stones"},
        {"key": "flank_pain", "name": "Flank / Low Back Pain", "cat": "Renal", "icon": "bi-activity", "desc": "Colicky or dull pain in lateral abdominal wall or lower back.", "cond": "Kidney Stones (Nephrolithiasis), Pyelonephritis"},
        {"key": "blood_in_urine", "name": "Blood in Urine (Hematuria)", "cat": "Renal", "icon": "bi-exclamation-circle-fill", "desc": "Pink, red, or cola-colored discoloration of urine.", "cond": "Kidney Stones, Severe UTI, Pyelonephritis"},
        {"key": "skin_rash", "name": "Visible Skin Rash or Redness", "cat": "Dermatological", "icon": "bi-grid-fill", "desc": "Noticeable eruption or redness altering skin texture and barrier.", "cond": "Eczema, Psoriasis, Contact Dermatitis, Fungal Infection"},
        {"key": "itching", "name": "Intense Pruritus / Itching", "cat": "Dermatological", "icon": "bi-hand-index", "desc": "Irritating sensation of the skin provoking the urge to scratch.", "cond": "Eczema, Contact Dermatitis, Fungal Infection, Hives"},
        {"key": "skin_flaking", "name": "Flaking or Scaly Skin Patches", "cat": "Dermatological", "icon": "bi-layers", "desc": "Excess shedding of dead epidermal keratinocytes.", "cond": "Psoriasis, Eczema, Fungal Skin Infection"},
        {"key": "acne_breakouts", "name": "Acne Papules, Pustules or Cysts", "cat": "Dermatological", "icon": "bi-circle-half", "desc": "Inflammatory or comedonal lesions of pilosebaceous units.", "cond": "Acne Vulgaris, PCOS"},
        {"key": "hives_welts", "name": "Raised Itchy Wheals / Hives", "cat": "Dermatological", "icon": "bi-chat-heart", "desc": "Transient raised, edematous, intensely pruritic wheals.", "cond": "Urticaria (Hives), Acute Allergic Reaction"},
        {"key": "hair_thinning", "name": "Diffuse Hair Thinning / Loss", "cat": "Dermatological", "icon": "bi-scissors", "desc": "Noticeable reduction in scalp hair density or excessive shedding.", "cond": "Hypothyroidism, PCOS, Severe Stress"},
        {"key": "joint_pain", "name": "Severe Joint / Bone Pain", "cat": "Musculoskeletal", "icon": "bi-diagram-3", "desc": "Aching, stiffness, warmth, or swelling within articular joints.", "cond": "Osteoarthritis, Rheumatoid Arthritis, Gout, Dengue"},
        {"key": "joint_stiffness", "name": "Morning Joint Stiffness", "cat": "Musculoskeletal", "icon": "bi-hourglass-split", "desc": "Restricted joint mobility upon waking in the morning.", "cond": "Rheumatoid Arthritis, Osteoarthritis"},
        {"key": "muscle_pain", "name": "Muscle Aches & Myalgia", "cat": "Musculoskeletal", "icon": "bi-person-arms-up", "desc": "Diffuse or localized aching tenderness across muscle groups.", "cond": "Muscle Strain, Tension Headache, PAD, Anxiety"},
        {"key": "back_pain", "name": "Lower Back Ache or Stiffness", "cat": "Musculoskeletal", "icon": "bi-body-text", "desc": "Ache, stiffness, or sharp spasm in lumbosacral region.", "cond": "Muscle Strain, Osteoporosis, Lumbar Disc Disease"},
        {"key": "anxiety_nervousness", "name": "Excessive Worry & Nervousness", "cat": "Psychological", "icon": "bi-exclamation-triangle-fill", "desc": "Persistent, intrusive worry and autonomic hyperarousal.", "cond": "Generalized Anxiety, Chronic Stress & Burnout"},
        {"key": "depressed_mood", "name": "Persistent Depressed Mood", "cat": "Psychological", "icon": "bi-cloud-drizzle-fill", "desc": "Lasting sadness, anhedonia, and unrefreshing fatigue.", "cond": "Depressive Symptoms, Vitamin D Deficiency, Burnout"},
        {"key": "sleep_disturbance", "name": "Insomnia & Sleep Disruption", "cat": "Psychological", "icon": "bi-moon-stars-fill", "desc": "Difficulty initiating, consolidating, or maintaining restorative sleep.", "cond": "Insomnia & Sleep Disorder, Anxiety, Chronic Stress"}
    ]

    cards_html = ""
    for s in symptoms_list:
        cond_str = s.get('cond', '').strip()
        cond_items = [c.strip() for c in cond_str.split(',') if c.strip()]
        if cond_items:
            cond_html = "".join([f'<span class="symptom-condition-tag">{c}</span>' for c in cond_items])
        else:
            cond_html = '<span class="symptom-relation-empty">No associated conditions listed</span>'

        cards_html += f"""
        <div class="col-md-6 col-lg-4 symptom-guide-card" data-name="{s['name'].lower()}" data-category="{s['cat'].lower()}" data-desc="{(s['desc'] + ' ' + cond_str).lower()}">
            <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                <div>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="p-2 bg-info bg-opacity-10 text-info rounded-circle"><i class="bi {s['icon']} fs-4"></i></div>
                        <span class="badge bg-secondary bg-opacity-25 text-info border border-info border-opacity-25">{s['cat']}</span>
                    </div>
                    <h5 class="fw-bold mb-2">{s['name']}</h5>
                    <p class="small text-muted mb-3" style="line-height: 1.6;">{s['desc']}</p>
                    <div class="symptom-relation-box mb-3">
                        <div class="symptom-relation-title">
                            <i class="bi bi-diagram-3-fill text-info"></i> May occur with:
                        </div>
                        <div class="symptom-relation-content d-flex flex-wrap gap-1 mt-2">
                            {cond_html}
                        </div>
                    </div>
                </div>
                <div class="pt-3 border-top mt-2">
                    <a href="/prediction?symptom={s['key']}" class="btn btn-outline-info btn-sm rounded-pill w-100 py-2 fw-semibold">
                        <i class="bi bi-cpu-fill me-1"></i> Use this symptom in AI checker
                    </a>
                </div>
            </div>
        </div>
        """

    content = f"""
    <div class="row py-3 text-center">
        <div class="col-12 mb-4">
            <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">CLINICAL DIRECTORY</span>
            <h1 class="display-5 fw-extrabold mb-2">Interactive Symptoms Guide & Clinical Index</h1>
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
                    <button type="button" class="btn btn-sm symptom-filter-pill active btn-info text-white fw-bold" data-category="all">All</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="general">General</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="respiratory">Respiratory</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="cardiovascular">Cardiovascular</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="digestive">Digestive</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="neurological">Neurological</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="endocrine">Endocrine</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="renal">Renal</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="dermatological">Dermatological</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="musculoskeletal">Musculoskeletal</button>
                    <button type="button" class="btn btn-sm symptom-filter-pill btn-outline-secondary" data-category="psychological">Psychological</button>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4" id="symptomsGuideGrid">{cards_html}</div>

    <!-- Empty Search Fallback -->
    <div id="symptomsEmptySearch" class="card-custom p-5 text-center my-4" style="display: none;">
        <i class="bi bi-search text-muted display-4 mb-3"></i>
        <h4 class="fw-bold">No Matching Symptoms Found</h4>
        <p class="text-muted small mb-3">Try adjusting your search terms or select "All" from the body system filters above.</p>
        <button type="button" class="btn btn-outline-info rounded-pill px-4" onclick="document.getElementById('symptomSearchInput').value=''; document.querySelector('[data-category=all]').click();">
            Reset Search & Filters
        </button>
    </div>
    """
    return render_page(content)

@app.route('/prevention')
@app.route('/prevention.php')
@app.route('/api/prevention')
def prevention():
    lifestyle_cards = [
        ("bi-egg-fried", "Nutritional Balance", "Diet & Fuel", "Prioritize whole grains, colorful vegetables, lean proteins, and unsaturated fats while reducing sodium to <2,300 mg/day."),
        ("bi-lightning-charge-fill", "Physical Activity", "Movement", "Target at least 150 minutes of moderate aerobic exercise or 75 minutes of vigorous activity weekly with strength training."),
        ("bi-moon-stars-fill", "Restorative Sleep", "Recovery", "Aim for 7 to 9 hours of uninterrupted nocturnal sleep in a cool, dark room. Maintain regular circadian rhythms."),
        ("bi-droplet-fill", "Optimal Hydration", "Vital Fluids", "Drink 2 to 3 liters of fresh water daily to support kidney filtration, blood pressure homeostasis, and joint lubrication."),
        ("bi-heart-half", "Stress Management", "Nervous System", "Practice diaphragmatic breathing, mindfulness, and regular outdoor recreation to reduce chronic sympathetic cortisol elevation."),
        ("bi-shield-shaded", "Hygiene & Sanitation", "Infection Control", "Wash hands for at least 20 seconds with soap and water before meals and after transit to block microbial transmission."),
        ("bi-capsule", "Vaccination Awareness", "Immunization", "Keep routine vaccines current, including annual influenza boosters, COVID-19 immunizations, and tetanus toxoid boosters."),
        ("bi-clipboard2-pulse", "Regular Screenings", "Proactive Care", "Schedule annual health checkups to monitor fasting blood glucose, lipid panels, and resting blood pressure.")
    ]

    lifestyle_html = "".join([f"""
    <div class="col-md-6 col-lg-3">
        <div class="card-custom p-4 h-100 border border-secondary border-opacity-25">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <i class="bi {icon} text-info fs-3"></i>
                <span class="badge bg-secondary bg-opacity-40 text-info">{badge}</span>
            </div>
            <h5 class="fw-bold text-white mb-2">{title}</h5>
            <p class="small text-muted mb-0">{tip}</p>
        </div>
    </div>
    """ for icon, title, badge, tip in lifestyle_cards])

    content = f"""
    <div class="row py-3 text-center">
        <div class="col-12 mb-4">
            <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">PREVENTATIVE HEALTH</span>
            <h1 class="display-5 fw-extrabold text-white">Health Awareness & Disease Prevention</h1>
            <p class="lead text-muted mx-auto" style="max-width: 780px;">
                Evidence-based preventative practices, lifestyle foundations, and organ-specific risk reduction strategies.
            </p>
        </div>
    </div>

    <h3 class="fw-bold text-white mb-4"><i class="bi bi-compass text-info me-2"></i> Foundations of Healthy Living</h3>
    <div class="row g-4 mb-5">{lifestyle_html}</div>

    <!-- Emergency Triage Guidance -->
    <div class="card-custom p-4 p-md-5 my-4 border-danger" style="border-width: 2px;">
        <h4 class="fw-bold text-danger mb-3 d-flex align-items-center">
            <i class="bi bi-exclamation-octagon-fill me-2 fs-3"></i> Red-Flag Warning Signs: When to Seek Immediate Emergency Medical Care
        </h4>
        <div class="row g-3 text-muted small">
            <div class="col-md-3">
                <div class="p-3 bg-card-subtle rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Cardiac Symptoms:</strong> Crushing chest pressure, pain radiating to left arm or jaw, sudden cold sweat.
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-card-subtle rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Respiratory Distress:</strong> Inability to speak full sentences, severe shortness of breath, cyanosis (blue lips/fingertips).
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-card-subtle rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Neurological Emergencies:</strong> Sudden facial drooping, arm weakness, slurred speech (FAST stroke signs) or seizure > 5 mins.
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 bg-card-subtle rounded border border-danger border-opacity-25 h-100">
                    <strong class="text-danger d-block mb-1">Systemic Sepsis:</strong> High fever > 103°F with confusion, drenching rigors, and rapid heart rate.
                </div>
            </div>
        </div>
        <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded mt-3 text-center">
            <span class="text-danger fw-bold small"><i class="bi bi-telephone-fill me-1"></i> If you experience severe emergency signs, call 911 / 112 or visit the nearest emergency room immediately.</span>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/dataset-info')
@app.route('/dataset_info.php')
@app.route('/api/dataset-info')
def dataset_info():
    content = """
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-3">Dataset & Large Data Handling Architecture</h2>
        <p class="text-muted small mb-4">Offline data preprocessing, separate dataset storage, lightweight joblib pipelines, and REST API inference microservices.</p>
    </div>
    """
    return render_page(content)

@app.route('/project-info')
@app.route('/project_info.php')
@app.route('/api/project-info')
def project_info():
    content = """
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-3">About College Project</h2>
        <p class="text-muted small">AI Healthcare – Intelligent Disease Prediction & Health Assistance System built with HTML5, CSS3, Bootstrap 5, JavaScript, PHP, MySQL, Python Scikit-Learn.</p>
    </div>
    """
    return render_page(content)

@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact.php', methods=['GET', 'POST'])
@app.route('/api/contact', methods=['GET', 'POST'])
def contact():
    content = """
    <div class="card-custom p-5 max-w-lg mx-auto my-4">
        <h2 class="fw-bold text-white mb-3">Contact & Academic Support</h2>
        <p class="text-muted small">Reach out to our project development team regarding academic submissions.</p>
    </div>
    """
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.php', methods=['GET', 'POST'])
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = {"name": "Academic Student", "email": "student@college.edu"}
        return redirect('/dashboard')
    content = """
    <div class="card-custom p-4 max-w-md mx-auto my-5">
        <h3 class="fw-bold text-white mb-3 text-center">Platform Login</h3>
        <form method="POST" action="/login">
            <div class="mb-3"><label class="form-label text-white">Email</label><input type="email" name="email" class="form-control" value="student@college.edu" required></div>
            <div class="mb-3"><label class="form-label text-white">Password</label><input type="password" name="password" class="form-control" value="password123" required></div>
            <button type="submit" class="btn btn-primary-custom w-100 py-2">Login to Dashboard</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.php', methods=['GET', 'POST'])
@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user'] = {"name": request.form.get('name', 'Student User'), "email": request.form.get('email', 'user@college.edu')}
        return redirect('/dashboard')
    content = """
    <div class="card-custom p-4 max-w-md mx-auto my-5">
        <h3 class="fw-bold text-white mb-3 text-center">User Registration</h3>
        <form method="POST" action="/register">
            <div class="mb-3"><label class="form-label text-white">Full Name</label><input type="text" name="name" class="form-control" required></div>
            <div class="mb-3"><label class="form-label text-white">Email</label><input type="email" name="email" class="form-control" required></div>
            <div class="mb-3"><label class="form-label text-white">Password</label><input type="password" name="password" class="form-control" required></div>
            <button type="submit" class="btn btn-primary-custom w-100 py-2">Create Account</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/logout')
@app.route('/logout.php')
@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
@app.route('/dashboard.php')
@app.route('/api/dashboard')
def dashboard():
    user = session.get('user', {"name": "Academic Student", "email": "student@college.edu"})
    content = f"""
    <div class="card-custom p-5 my-4">
        <h2 class="fw-bold text-white mb-2">Welcome, {user['name']}!</h2>
        <p class="text-muted small mb-4">Access your previous AI disease predictions and explore health information.</p>
        <a href="/prediction" class="btn btn-primary-custom rounded-pill">Run Symptom Prediction</a>
    </div>
    """
    return render_page(content)

@app.route('/predict', methods=['POST', 'GET'])
@app.route('/api/predict', methods=['POST', 'GET'])
def api_predict():
    if request.method == 'GET':
        return jsonify({"message": "Send POST request with JSON payload: {'disease': 'symptoms', 'symptoms': [...]}"})
    try:
        req_data = request.get_json(force=True, silent=True) or request.form.to_dict()
        disease = req_data.get('disease', 'symptoms')
        symptoms = req_data.get('symptoms', [])
        data_dict = req_data.get('data', {})
        
        if disease == 'symptoms' or symptoms:
            if not symptoms and isinstance(data_dict, list):
                symptoms = data_dict
            result_data = predict_symptoms(symptoms)
        else:
            result_data = predict_disease(disease, data_dict)
        return jsonify(result_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scanner')
@app.route('/image_scanner.php')
@app.route('/api/scanner')
def scanner_page():
    content = """
    <!-- Page Header & Hero -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card-custom p-4 p-md-5 mb-3" style="background: linear-gradient(135deg, #0b1120 0%, #151f32 50%, #0f766e 100%);">
                <span class="badge bg-white text-dark fw-bold px-3 py-2 rounded-pill mb-3">
                    <i class="bi bi-camera-fill text-info me-1"></i> Computer Vision Pipeline
                </span>
                <h1 class="display-6 fw-bold text-white mb-2">AI Infection & Injury Scanner</h1>
                <p class="lead mb-0 text-white-50">
                    Upload a clear image of a skin injury, wound, rash, swelling, or redness for an AI-assisted preliminary visual assessment.
                </p>
            </div>

            <!-- Mandatory Educational Disclaimer -->
            <div class="alert alert-warning border-0 p-3 mb-3 shadow-sm" style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #f59e0b !important;">
                <i class="bi bi-exclamation-triangle-fill fs-5 me-2"></i>
                <strong>Important Medical Notice:</strong> This AI scanner provides an <em>educational preliminary visual assessment</em> and is not a medical diagnosis. For concerning, worsening, infected, or serious injuries, consult a qualified healthcare professional.
            </div>

            <!-- Privacy Assurance Banner -->
            <div class="alert alert-secondary py-2 px-3 small border d-flex align-items-center gap-2 mb-4">
                <i class="bi bi-shield-lock-fill text-success fs-5"></i>
                <div>
                    <strong>Privacy Assurance:</strong> Uploaded images are processed ephemerally in memory and permanently deleted immediately after visual metric extraction. Photos are <strong>never stored</strong> in our database. <em>Do not upload identifying personal documents or faces.</em>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Scanner Layout -->
    <div class="row g-4 mb-5">
        <div class="col-lg-6">
            <div class="card-custom h-100 p-4">
                <h4 class="fw-bold mb-1 d-flex align-items-center gap-2">
                    <i class="bi bi-cloud-arrow-up text-info"></i> Scan an Infection or Injury
                </h4>
                <p class="text-muted small mb-3">Upload a clear, well-lit image of the affected skin area for preliminary analysis.</p>

                <div id="scannerErrorAlert" class="alert alert-danger d-none mb-3 py-2 px-3 small">
                    <i class="bi bi-exclamation-circle-fill me-1"></i> <span id="scannerErrorMsg"></span>
                </div>

                <div id="dropZone" class="scanner-dropzone mb-3">
                    <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle d-inline-block mb-3">
                        <i class="bi bi-image fs-1"></i>
                    </div>
                    <h5 class="fw-bold mb-1">Drag & Drop Image Here</h5>
                    <p class="text-muted small mb-3">or choose from your device</p>
                    <div class="d-flex flex-wrap justify-content-center gap-2">
                        <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnBrowseFiles">
                            <i class="bi bi-folder2-open me-1"></i> Upload Image
                        </button>
                        <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnTakePhoto">
                            <i class="bi bi-camera me-1"></i> Take Photo
                        </button>
                    </div>
                    <div class="mt-3 text-muted small">
                        <span class="badge bg-secondary-subtle text-secondary me-1">JPG</span>
                        <span class="badge bg-secondary-subtle text-secondary me-1">PNG</span>
                        <span class="badge bg-secondary-subtle text-secondary">WEBP</span>
                        <span class="ms-2">Max 8 MB</span>
                    </div>
                    <input type="file" id="imageFileInput" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" class="d-none">
                    <input type="file" id="cameraFileInput" accept="image/*" capture="environment" class="d-none">
                </div>

                <div id="previewContainer" class="d-none mt-2">
                    <div class="scanner-preview-wrapper mb-3" id="previewFrame">
                        <img id="previewImage" class="scanner-preview-img" alt="Skin Preview">
                        <div class="scanner-laser-beam"></div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center p-2 px-3 rounded-3 mb-3 border" style="background: var(--bg-secondary);">
                        <span id="previewFilename" class="small fw-semibold text-truncate me-2">image.jpg</span>
                        <span id="previewFilesize" class="badge bg-secondary rounded-pill">0 KB</span>
                    </div>
                    <div class="d-flex gap-2" id="previewActions">
                        <button type="button" class="btn btn-outline-danger flex-fill py-2 rounded-3" id="btnRemoveImage">
                            <i class="bi bi-trash3 me-1"></i> Remove Image
                        </button>
                        <button type="button" class="btn btn-primary-custom flex-fill py-2" id="btnScanImage">
                            <i class="bi bi-cpu me-1"></i> Scan Image
                        </button>
                    </div>
                    <div id="scanningState" class="d-none text-center py-3">
                        <strong class="text-info fs-5 d-block mb-2">Analyzing image...</strong>
                        <p id="scanningStatusText" class="text-muted small mb-2">Evaluating visual characteristics...</p>
                        <div class="progress" style="height: 6px;">
                            <div id="scanProgressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-info" style="width: 50%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-6">
            <div class="card-custom h-100 p-4" id="resultCardContainer">
                <div id="idleState" class="text-center py-5 my-auto">
                    <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                    <h4 class="fw-bold mb-2">Preliminary Assessment Output</h4>
                    <p class="text-muted small mb-0">Select or capture a photo and click <strong>"Scan Image"</strong>. The computer vision analyzer evaluates erythema index, edge gradients, and textural dispersion.</p>
                </div>

                <div id="resultContent" class="d-none">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="text-muted small fw-bold text-uppercase"><i class="bi bi-clipboard2-pulse me-1"></i> Visual Assessment</span>
                        <span class="small text-muted">Just now</span>
                    </div>
                    <div class="mb-3">
                        <span id="resultCategoryBadge" class="badge-category badge-category-injury">
                            <span id="resultCategoryText">Evaluating...</span>
                        </span>
                    </div>
                    <div class="p-3 rounded-3 border mb-3" style="background: var(--bg-secondary);">
                        <h5 class="fw-bold mb-1" id="resultSummaryHeading">Visual indicators may be consistent with...</h5>
                        <p class="text-muted small mb-0" id="resultSummaryDesc">Assessment generated via spectrophotometric color analysis and surface edge gradient measurement.</p>
                    </div>
                    <div class="mb-3 p-3 rounded-3 border" style="background: var(--bg-secondary);">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="small fw-semibold">Visual Feature Correlation Score:</span>
                            <span id="resultScoreText" class="fw-bold text-info">0.0%</span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div id="resultScoreBar" class="progress-bar bg-info" style="width: 0%;"></div>
                        </div>
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valErythema">--</div>
                                <div class="metric-pill-lbl">Erythema</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valRoughness">--</div>
                                <div class="metric-pill-lbl">Roughness</div>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="metric-pill-card">
                                <div class="metric-pill-val" id="valChroma">--</div>
                                <div class="metric-pill-lbl">Variance</div>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <h6 class="fw-bold small text-uppercase text-muted mb-2">Visual Observations</h6>
                        <ul id="resultFindingsList" class="small text-muted ps-3 mb-0"></ul>
                    </div>
                    <div class="mb-3">
                        <h6 class="fw-bold small text-uppercase text-muted mb-2">General Educational Guidance</h6>
                        <ul id="resultRecsList" class="small text-muted ps-3 mb-0"></ul>
                    </div>
                    <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2" id="btnScanAnother">
                        <i class="bi bi-arrow-repeat me-1"></i> Scan Another Image
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Safety Warning Signs -->
    <div class="card-custom p-4 mb-5 border-danger-subtle">
        <div class="d-flex align-items-center gap-2 mb-3">
            <span class="badge bg-danger text-white px-3 py-2 rounded-pill">
                <i class="bi bi-hospital me-1"></i> Patient Safety Notice
            </span>
            <h4 class="fw-bold mb-0">When to Seek Immediate Medical Attention</h4>
        </div>
        <div class="row g-3">
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-droplet-fill me-1"></i> Severe Bleeding</div><div class="small text-muted">Blood that continues to flow after 10 minutes of direct pressure.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-graph-up-arrow me-1"></i> Rapidly Spreading Redness</div><div class="small text-muted">Red streaks radiating from the wound or expanding borders.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-thermometer-high me-1"></i> Fever & Systemic Chills</div><div class="small text-muted">Elevated body temperature (>100.4°F), rigors, or nausea.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-radioactive me-1"></i> Foul Pus or Drainage</div><div class="small text-muted">Thick, yellow/green discharge or wound that feels unusually hot.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-arrows-fullscreen me-1"></i> Rapidly Increasing Swelling</div><div class="small text-muted">Swelling that produces severe throbbing pain or numbs limb.</div></div></div>
            <div class="col-md-4 col-sm-6"><div class="warning-sign-card h-100"><div class="fw-bold text-danger mb-1"><i class="bi bi-bandaid-fill me-1"></i> Deep or Gaping Wounds</div><div class="small text-muted">Cuts exposing yellow fat or muscle requiring sutures.</div></div></div>
        </div>
    </div>

    <!-- Live Camera Modal -->
    <div class="modal fade" id="cameraModal" tabindex="-1" aria-labelledby="cameraModalLabel" aria-hidden="true" data-bs-backdrop="static">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content card-custom border-info">
                <div class="modal-header border-bottom border-subtle">
                    <h5 class="modal-title fw-bold" id="cameraModalLabel">
                        <i class="bi bi-camera-fill text-info me-2"></i>Photograph Affected Area
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="btnCloseCameraX"></button>
                </div>
                <div class="modal-body p-3 text-center">
                    <div id="cameraStreamContainer" class="position-relative overflow-hidden rounded-3 bg-black" style="min-height: 280px; max-height: 420px;">
                        <video id="cameraVideo" autoplay playsinline muted class="w-100 h-100" style="object-fit: cover;"></video>
                        <div class="position-absolute top-50 start-50 translate-middle border border-info border-2 rounded-circle opacity-75 pointer-events-none" style="width: 140px; height: 140px; border-style: dashed !important;"></div>
                    </div>
                    <canvas id="cameraCanvas" class="d-none"></canvas>
                    <div id="cameraAlert" class="alert alert-warning d-none mt-2 py-2 px-3 small text-start"></div>
                </div>
                <div class="modal-footer border-top border-subtle d-flex justify-content-between">
                    <button type="button" class="btn btn-outline-secondary rounded-pill px-3" id="btnFlipCamera">
                        <i class="bi bi-arrow-repeat me-1"></i> Flip Camera
                    </button>
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-outline-danger rounded-pill px-3" data-bs-dismiss="modal" id="btnCancelCamera">Cancel</button>
                        <button type="button" class="btn btn-info rounded-pill px-4 text-white fw-bold" id="btnSnapPhoto">
                            <i class="bi bi-circle-fill me-1"></i> Capture
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var dropZone = document.getElementById('dropZone');
        var imageFileInput = document.getElementById('imageFileInput');
        var cameraFileInput = document.getElementById('cameraFileInput');
        var btnBrowseFiles = document.getElementById('btnBrowseFiles');
        var btnTakePhoto = document.getElementById('btnTakePhoto');
        var previewContainer = document.getElementById('previewContainer');
        var previewImage = document.getElementById('previewImage');
        var previewFilename = document.getElementById('previewFilename');
        var previewFilesize = document.getElementById('previewFilesize');
        var previewActions = document.getElementById('previewActions');
        var btnRemoveImage = document.getElementById('btnRemoveImage');
        var btnScanImage = document.getElementById('btnScanImage');
        var scanningState = document.getElementById('scanningState');
        var scanningStatusText = document.getElementById('scanningStatusText');
        var scanProgressBar = document.getElementById('scanProgressBar');
        var previewFrame = document.getElementById('previewFrame');
        var idleState = document.getElementById('idleState');
        var resultContent = document.getElementById('resultContent');
        var resultCategoryBadge = document.getElementById('resultCategoryBadge');
        var resultCategoryText = document.getElementById('resultCategoryText');
        var resultSummaryHeading = document.getElementById('resultSummaryHeading');
        var resultScoreText = document.getElementById('resultScoreText');
        var resultScoreBar = document.getElementById('resultScoreBar');
        var valErythema = document.getElementById('valErythema');
        var valRoughness = document.getElementById('valRoughness');
        var valChroma = document.getElementById('valChroma');
        var resultFindingsList = document.getElementById('resultFindingsList');
        var resultRecsList = document.getElementById('resultRecsList');
        var btnScanAnother = document.getElementById('btnScanAnother');
        var scannerErrorAlert = document.getElementById('scannerErrorAlert');
        var scannerErrorMsg = document.getElementById('scannerErrorMsg');

        // Camera Modal
        var cameraModalElem = document.getElementById('cameraModal');
        var cameraModalInstance = null;
        var cameraVideo = document.getElementById('cameraVideo');
        var cameraCanvas = document.getElementById('cameraCanvas');
        var btnSnapPhoto = document.getElementById('btnSnapPhoto');
        var btnFlipCamera = document.getElementById('btnFlipCamera');
        var activeCameraStream = null;
        var currentFacingMode = 'environment';

        var currentFile = null;
        var scanAnimationTimer = null;

        function showError(msg) {
            scannerErrorMsg.innerHTML = msg;
            scannerErrorAlert.classList.remove('d-none');
        }
        function clearError() {
            scannerErrorAlert.classList.add('d-none');
            scannerErrorMsg.textContent = '';
        }

        btnBrowseFiles.onclick = function(e) { e.stopPropagation(); imageFileInput.click(); };
        
        btnTakePhoto.onclick = function(e) {
            e.stopPropagation();
            clearError();
            if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
                startLiveCamera(currentFacingMode);
            } else {
                cameraFileInput.click();
            }
        };

        function startLiveCamera(facingMode) {
            if (!cameraModalInstance && typeof bootstrap !== 'undefined') {
                cameraModalInstance = new bootstrap.Modal(cameraModalElem);
            }
            stopActiveCameraStream();
            var constraints = {
                video: { facingMode: { ideal: facingMode }, width: { ideal: 1280 }, height: { ideal: 720 } },
                audio: false
            };
            navigator.mediaDevices.getUserMedia(constraints)
            .then(function(stream) {
                activeCameraStream = stream;
                cameraVideo.srcObject = stream;
                if (cameraModalInstance) cameraModalInstance.show();
            })
            .catch(function(err) {
                console.warn('Camera error:', err);
                if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                    showError('<strong>Camera access denied.</strong> Please allow camera permissions in your browser or use <em>Upload Image</em>.');
                } else {
                    cameraFileInput.click();
                }
            });
        }

        function stopActiveCameraStream() {
            if (activeCameraStream) {
                activeCameraStream.getTracks().forEach(function(t) { t.stop(); });
                activeCameraStream = null;
            }
            if (cameraVideo) cameraVideo.srcObject = null;
        }

        if (cameraModalElem) {
            cameraModalElem.addEventListener('hidden.bs.modal', function() {
                stopActiveCameraStream();
            });
        }

        if (btnFlipCamera) {
            btnFlipCamera.onclick = function() {
                currentFacingMode = (currentFacingMode === 'environment') ? 'user' : 'environment';
                startLiveCamera(currentFacingMode);
            };
        }

        if (btnSnapPhoto) {
            btnSnapPhoto.onclick = function() {
                if (!cameraVideo || !cameraVideo.videoWidth) return;
                cameraCanvas.width = cameraVideo.videoWidth;
                cameraCanvas.height = cameraVideo.videoHeight;
                var ctx = cameraCanvas.getContext('2d');
                ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
                cameraCanvas.toBlob(function(blob) {
                    if (!blob) return;
                    var capturedFile = new File([blob], 'camera_photo_' + Date.now() + '.jpg', { type: 'image/jpeg' });
                    if (cameraModalInstance) cameraModalInstance.hide();
                    stopActiveCameraStream();
                    handleFile(capturedFile);
                }, 'image/jpeg', 0.92);
            };
        }

        dropZone.onclick = function() { imageFileInput.click(); };

        ['dragenter', 'dragover'].forEach(function(ev) {
            dropZone.addEventListener(ev, function(e) { e.preventDefault(); dropZone.classList.add('dragover'); });
        });
        ['dragleave', 'drop'].forEach(function(ev) {
            dropZone.addEventListener(ev, function(e) { e.preventDefault(); dropZone.classList.remove('dragover'); });
        });
        dropZone.addEventListener('drop', function(e) {
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });

        imageFileInput.onchange = function() { if (this.files.length) handleFile(this.files[0]); };
        cameraFileInput.onchange = function() { if (this.files.length) handleFile(this.files[0]); };

        function handleFile(file) {
            clearError();
            if (file.size > 8 * 1024 * 1024) { showError('Image is too large (max 8 MB).'); return; }
            currentFile = file;
            previewFilename.textContent = file.name;
            previewFilesize.textContent = (file.size / 1024).toFixed(1) + ' KB';
            var reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                dropZone.classList.add('d-none');
                previewContainer.classList.remove('d-none');
                previewActions.classList.remove('d-none');
                scanningState.classList.add('d-none');
                resultContent.classList.add('d-none');
                idleState.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }

        btnRemoveImage.onclick = resetScanner;
        btnScanAnother.onclick = resetScanner;

        function resetScanner() {
            currentFile = null;
            imageFileInput.value = '';
            cameraFileInput.value = '';
            previewImage.src = '';
            previewContainer.classList.add('d-none');
            dropZone.classList.remove('d-none');
            previewFrame.classList.remove('scanning-active');
            resultContent.classList.add('d-none');
            idleState.classList.remove('d-none');
            btnScanImage.removeAttribute('disabled');
            btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';
            if (scanAnimationTimer) clearInterval(scanAnimationTimer);
            clearError();
        }

        btnScanImage.onclick = function() {
            if (!currentFile) { showError('Please select an image first.'); return; }
            clearError();
            btnScanImage.setAttribute('disabled', 'disabled');
            btnScanImage.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';
            previewActions.classList.add('d-none');
            scanningState.classList.remove('d-none');
            previewFrame.classList.add('scanning-active');

            var steps = [
                "Preparing image for analysis...",
                "Computing spectrophotometric erythema index...",
                "Analyzing surface texture & edge roughness...",
                "Evaluating chromatic dispersion & color variance...",
                "Generating preliminary assessment..."
            ];
            var stepIdx = 0;
            scanningStatusText.textContent = steps[0];
            scanProgressBar.style.width = '20%';

            scanAnimationTimer = setInterval(function() {
                stepIdx++;
                if (stepIdx < steps.length) {
                    scanningStatusText.textContent = steps[stepIdx];
                    scanProgressBar.style.width = Math.min(90, 20 + stepIdx * 18) + '%';
                }
            }, 320);

            var formData = new FormData();
            formData.append('image', currentFile);

            fetch('/api/scan-image', { method: 'POST', body: formData })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                clearInterval(scanAnimationTimer);
                scanProgressBar.style.width = '100%';
                setTimeout(function() {
                    previewFrame.classList.remove('scanning-active');
                    scanningState.classList.add('d-none');
                    previewActions.classList.remove('d-none');
                    btnScanImage.removeAttribute('disabled');
                    btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';

                    if (!data || data.success === false) {
                        showError('<strong>Image analysis could not be completed.</strong><br>Reason: ' + (data.error || 'Image processing service unavailable.'));
                        resultContent.classList.add('d-none');
                        idleState.classList.remove('d-none');
                    } else {
                        renderResult(data);
                    }
                }, 300);
            })
            .catch(function(err) {
                clearInterval(scanAnimationTimer);
                previewFrame.classList.remove('scanning-active');
                scanningState.classList.add('d-none');
                previewActions.classList.remove('d-none');
                btnScanImage.removeAttribute('disabled');
                btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';
                showError('<strong>Analysis unavailable:</strong> ' + err.message);
                resultContent.classList.add('d-none');
                idleState.classList.remove('d-none');
            });
        };

        function renderResult(res) {
            idleState.classList.add('d-none');
            resultContent.classList.remove('d-none');
            var cat = res.category || 'Unable to Assess';
            resultCategoryText.textContent = cat;
            resultCategoryBadge.className = 'badge-category';
            if (cat.includes('Infection')) resultCategoryBadge.classList.add('badge-category-infection');
            else if (cat.includes('Inflammation')) resultCategoryBadge.classList.add('badge-category-inflammation');
            else if (cat.includes('Minor Injury')) resultCategoryBadge.classList.add('badge-category-injury');
            else if (cat.includes('Rash')) resultCategoryBadge.classList.add('badge-category-rash');
            else if (cat.includes('Swelling')) resultCategoryBadge.classList.add('badge-category-swelling');
            else resultCategoryBadge.classList.add('badge-category-unable');

            resultSummaryHeading.textContent = 'Visual indicators may be consistent with ' + cat.toLowerCase();
            var score = (typeof res.confidence_score === 'number') ? res.confidence_score : 0;
            resultScoreText.textContent = score.toFixed(1) + '%';
            resultScoreBar.style.width = Math.min(100, Math.max(0, score)) + '%';

            var metrics = res.metrics || {};
            valErythema.textContent = (metrics.erythema_index !== undefined) ? metrics.erythema_index : 'Not available';
            var rVal = (metrics.surface_roughness !== undefined) ? metrics.surface_roughness : ((metrics.roughness_score !== undefined) ? metrics.roughness_score : 'Not available');
            valRoughness.textContent = rVal;
            var cVal = (metrics.chromatic_variance !== undefined) ? metrics.chromatic_variance : ((metrics.color_variance !== undefined) ? metrics.color_variance : 'Not available');
            valChroma.textContent = cVal;

            resultFindingsList.innerHTML = '';
            (res.findings || []).forEach(function(f) {
                var li = document.createElement('li');
                li.className = 'mb-1';
                li.textContent = f;
                resultFindingsList.appendChild(li);
            });

            resultRecsList.innerHTML = '';
            (res.recommendations || []).forEach(function(r) {
                var li = document.createElement('li');
                li.className = 'mb-1';
                li.textContent = r;
                resultRecsList.appendChild(li);
            });
        }
    });
    </script>
    """
    return render_page(content)

@app.route('/api/scan-image', methods=['POST'])
def api_scan_image():
    temp_path = None
    try:
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"success": False, "category": "Unable to Assess", "error": "No file selected"}), 400
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            file.save(temp_path)
            res = compute_vision_metrics(temp_path)
            return jsonify(res)

        req_data = request.get_json(silent=True) or {}
        if 'image_base64' in req_data:
            b64_val = req_data['image_base64']
            if ',' in b64_val:
                b64_val = b64_val.split(',', 1)[1]
            img_bytes = base64.b64decode(b64_val)
            fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            with open(temp_path, 'wb') as f:
                f.write(img_bytes)
            res = compute_vision_metrics(temp_path)
            return jsonify(res)

        return jsonify({"success": False, "category": "Unable to Assess", "error": "No image data provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "category": "Unable to Assess", "error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


handler = app
app_handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
