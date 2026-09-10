-- ==============================================================================
-- AI Healthcare - Intelligent Disease Prediction & Health Assistance System
-- Database Schema for MySQL / MariaDB (XAMPP Compatible)
-- Database Name: ai_healthcare
-- Character Set: utf8mb4 / utf8mb4_unicode_ci
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `ai_healthcare` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ai_healthcare`;

-- Drop existing tables to allow clean re-import
DROP TABLE IF EXISTS `contact_messages`;
DROP TABLE IF EXISTS `health_articles`;
DROP TABLE IF EXISTS `health_assessments`;
DROP TABLE IF EXISTS `prediction_history`;
DROP TABLE IF EXISTS `disease_symptoms`;
DROP TABLE IF EXISTS `symptoms`;
DROP TABLE IF EXISTS `diseases`;
DROP TABLE IF EXISTS `users`;

-- ------------------------------------------------------------------------------
-- 1. Users Table
-- ------------------------------------------------------------------------------
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. Diseases Table (25 Verified Diseases)
-- ------------------------------------------------------------------------------
CREATE TABLE `diseases` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `category` VARCHAR(100) NOT NULL,
  `short_description` TEXT NOT NULL,
  `causes` TEXT NOT NULL,
  `risk_factors` TEXT NOT NULL,
  `prevention` TEXT NOT NULL,
  `management` TEXT NOT NULL,
  `when_to_seek_care` TEXT NOT NULL,
  INDEX `idx_diseases_category` (`category`),
  INDEX `idx_diseases_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. Symptoms Table (30 Verified Symptoms)
-- ------------------------------------------------------------------------------
CREATE TABLE `symptoms` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `symptom_key` VARCHAR(100) NOT NULL UNIQUE,
  `body_system` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(20) DEFAULT 'Moderate',
  INDEX `idx_symptoms_key` (`symptom_key`),
  INDEX `idx_symptoms_system` (`body_system`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. Disease-Symptoms Junction Table
-- ------------------------------------------------------------------------------
CREATE TABLE `disease_symptoms` (
  `disease_id` INT NOT NULL,
  `symptom_id` INT NOT NULL,
  PRIMARY KEY (`disease_id`, `symptom_id`),
  CONSTRAINT `fk_ds_disease` FOREIGN KEY (`disease_id`) REFERENCES `diseases`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ds_symptom` FOREIGN KEY (`symptom_id`) REFERENCES `symptoms`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 5. Prediction History Table (Symptom-Based Predictions)
-- ------------------------------------------------------------------------------
CREATE TABLE `prediction_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `symptoms_selected` TEXT NOT NULL,
  `predicted_disease` VARCHAR(100) NOT NULL,
  `confidence` FLOAT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_pred_user` (`user_id`),
  CONSTRAINT `fk_ph_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 6. Health Assessments Table (Clinical Parameter Assessments)
-- ------------------------------------------------------------------------------
CREATE TABLE `health_assessments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `disease` VARCHAR(100) NOT NULL,
  `input_data` TEXT NOT NULL,
  `risk_level` VARCHAR(20) NOT NULL,
  `probability` FLOAT NOT NULL,
  `feature_importance` TEXT NOT NULL,
  `recommendations` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_assessments_user` (`user_id`),
  CONSTRAINT `fk_ha_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 7. Health Articles Table
-- ------------------------------------------------------------------------------
CREATE TABLE `health_articles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(200) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `summary` TEXT NOT NULL,
  `content` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 8. Contact Messages Table
-- ------------------------------------------------------------------------------
CREATE TABLE `contact_messages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `message` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- SEED DATA: 65 DISEASES
-- ==============================================================================

INSERT INTO `diseases` (`id`, `name`, `category`, `short_description`, `causes`, `risk_factors`, `prevention`, `management`, `when_to_seek_care`) VALUES
(1, 'Diabetes', 'Endocrine', 'A chronic metabolic disease characterized by elevated blood glucose levels leading to vascular and organ complications.', 'Insulin resistance or insufficient insulin production by pancreatic beta cells.', 'Obesity, physical inactivity, genetic predisposition, high-refined sugar diets.', 'Maintain healthy body weight, engage in 150 mins/week exercise, consume fiber-rich foods.', 'Blood glucose monitoring, dietary management, insulin therapy under physician guidance.', 'Seek immediate care for severe confusion, rapid breathing, or blood glucose > 300 mg/dL.'),
(2, 'Hypertension', 'Cardiovascular', 'Long-term high blood pressure against arterial walls causing increased cardiac workload.', 'Arterial stiffening, genetic factors, excessive sodium intake, renal dysfunction.', 'High sodium diet, chronic stress, smoking, excessive alcohol, family history.', 'Reduce salt intake, exercise regularly, manage stress, avoid tobacco.', 'Periodic blood pressure tracking, DASH diet, anti-hypertensive medications.', 'Seek urgent care for blood pressure > 180/120 mm Hg or sudden severe headache/chest pain.'),
(3, 'Heart Disease', 'Cardiovascular', 'Range of cardiac conditions including coronary artery disease and heart muscle dysfunction.', 'Atherosclerotic plaque accumulation narrowing coronary arteries.', 'High cholesterol, smoking, diabetes, hypertension, sedentary lifestyle.', 'Cardio-healthy diet, smoking cessation, lipid monitoring, regular physical activity.', 'Cardiac rehabilitation, lipid-lowering medication, lifestyle modification.', 'Seek emergency care immediately for crushing chest pain, arm radiation, or severe shortness of breath.'),
(4, 'Asthma', 'Respiratory', 'Chronic inflammatory disease of airway passages causing episodic wheezing and bronchospasm.', 'Environmental allergens, airway hyper-responsiveness, respiratory viral infections.', 'Family history, allergen exposure, air pollution, secondhand smoke.', 'Identify and avoid allergen triggers, use prophylactic inhalers as directed.', 'Inhaled corticosteroids, quick-relief bronchodilators, asthma action plan.', 'Seek emergency care for severe chest tightness, inability to speak full sentences, or blue lips.'),
(5, 'Pneumonia', 'Respiratory', 'Inflammatory infection of pulmonary alveoli filled with fluid or purulent exudate.', 'Bacterial (Streptococcus pneumoniae), viral (Influenza, RSV), or fungal pathogens.', 'Advanced age, immunocompromised status, chronic lung disease, smoking.', 'Pneumococcal vaccination, annual flu vaccine, hand hygiene.', 'Targeted antibiotic or antiviral therapy, adequate hydration, fever management.', 'Seek urgent medical attention for high fever, chest pain during breathing, or severe oxygen drop.'),
(6, 'Tuberculosis', 'Respiratory / Infectious', 'Contagious bacterial infection affecting pulmonary tissue caused by Mycobacterium tuberculosis.', 'Inhalation of airborne droplet nuclei containing M. tuberculosis.', 'Immunosuppression (HIV), close contact with active TB cases, malnutrition.', 'BCG vaccination where indicated, infection control in crowded environments.', 'Strict 6-month anti-tubercular drug regimen (DOTS protocol).', 'Seek immediate evaluation for coughing up blood, persistent night sweats, or unexplained weight loss.'),
(7, 'COVID-19', 'Respiratory / Infectious', 'Acute infectious disease caused by the SARS-CoV-2 coronavirus variant.', 'Respiratory transmission of SARS-CoV-2 viral particles.', 'Unvaccinated status, older age, underlying pulmonary/cardiac comorbidities.', 'Vaccination, indoor ventilation, mask usage during outbreaks, hand hygiene.', 'Symptomatic control, hydration, antiviral drugs for high-risk patients.', 'Seek emergency care for persistent chest pressure, oxygen saturation < 94%, or confusion.'),
(8, 'Influenza', 'Respiratory / Infectious', 'Acute viral infection of upper and lower respiratory tracts caused by influenza viruses.', 'Infection by Influenza A or B viral strains.', 'Seasonal outbreaks, immunocompromised health, extreme ages.', 'Annual influenza vaccination, hand washing, avoiding close contact with sick persons.', 'Rest, fluid intake, antiviral treatment (Oseltamivir) within 48 hours of onset.', 'Seek medical attention if fever persists over 4 days or severe breathing difficulty develops.'),
(9, 'Dengue', 'Infectious / Tropical', 'Mosquito-borne viral infection causing severe flu-like illness and low blood platelets.', 'Transmission of Dengue virus (DENV-1-4) by infected Aedes aegypti mosquitoes.', 'Living in tropical endemic areas, standing water reservoirs.', 'Mosquito repellent usage, eliminating standing water containers, wearing long clothing.', 'Supportive care, continuous hydration, monitoring blood platelet count.', 'Seek emergency care for severe abdominal pain, persistent vomiting, or mucosal bleeding.'),
(10, 'Malaria', 'Infectious / Tropical', 'Life-threatening parasitic infection transmitted by female Anopheles mosquitoes.', 'Plasmodium parasite infection (P. falciparum, P. vivax).', 'Travel to endemic tropical regions, lack of bednet protection.', 'Prophylactic antimalarial medication, insecticide-treated mosquito nets.', 'Artemisinin-based combination therapies (ACT) prescribed by physicians.', 'Seek immediate medical attention for high cyclical fever, severe chills, or jaundice.'),
(11, 'Typhoid', 'Infectious / Gastrointestinal', 'Systemic bacterial fever caused by Salmonella enterica serovar Typhi.', 'Ingestion of food or water contaminated with S. Typhi bacteria.', 'Poor sanitation, unhygienic street food, lack of clean drinking water.', 'Typhoid vaccination, drinking boiled/filtered water, hygienic food preparation.', 'Targeted oral/intravenous antibiotics and fever control.', 'Seek medical care for continuous high fever, Rose spots on abdomen, or severe lethargy.'),
(12, 'Migraine', 'Neurological', 'Recurrent neurological headache disorder characterized by moderate-to-severe throbbing pain.', 'Neurovascular reactivity, trigeminal nerve activation, serotonin level fluctuations.', 'Stress, hormonal changes, sleep disruption, dietary triggers (caffeine, monosodium glutamate).', 'Maintain consistent sleep schedules, stress reduction, trigger diary tracking.', 'Acute triptan therapy, preventive medications, dark room rest.', 'Seek urgent evaluation for a sudden "thunderclap" headache or accompanied facial numbness/weakness.'),
(13, 'Epilepsy', 'Neurological', 'Central nervous system disorder characterized by recurrent unprovoked electrical seizures.', 'Abnormal brain electrical activity due to genetics, head trauma, stroke, or structural brain lesions.', 'Family history, prior head injury, central nervous system infections.', 'Head injury prevention (helmets), consistent medication adherence.', 'Antiepileptic drugs (AEDs), regular neurological monitoring.', 'Seek emergency services if a seizure lasts longer than 5 minutes or consecutive seizures occur.'),
(14, 'Parkinson''s Disease', 'Neurological', 'Progressive neurodegenerative disorder characterized by loss of dopamine-producing brain cells.', 'Degeneration of substantia nigra dopaminergic neurons, alpha-synuclein accumulation.', 'Advanced age, male sex, pesticide/environmental toxin exposure.', 'Regular aerobic exercise, neuroprotective lifestyle habits.', 'Levodopa/Carbidopa medication, physical therapy, occupational assistance.', 'Seek medical advice upon noticing resting hand tremors, muscle rigidity, or gait disturbance.'),
(15, 'Alzheimer''s Disease', 'Neurological', 'Progressive neurodegenerative disease causing memory impairment and cognitive decline.', 'Accumulation of extracellular amyloid-beta plaques and intracellular tau tangles.', 'Age over 65, APOE-e4 gene variant, cardiovascular comorbidities, low cognitive reserve.', 'Cardiovascular health management, lifelong mental stimulation, Mediterranean diet.', 'Cholinesterase inhibitors, supportive cognitive care, safety modifications.', 'Seek neurological assessment for progressive short-term memory loss interfering with daily living.'),
(16, 'COPD', 'Respiratory', 'Progressive airflow limitation caused by emphysema and chronic bronchitis.', 'Long-term exposure to irritating gases, primarily cigarette smoke or biomass fuel.', 'Cigarette smoking, occupational dust exposure, alpha-1 antitrypsin deficiency.', 'Complete smoking cessation, avoiding workplace respiratory irritants.', 'Inhaled bronchodilators, pulmonary rehabilitation, supplemental oxygen therapy.', 'Seek immediate emergency care for acute exacerbation with severe breathlessness and cyanosis.'),
(17, 'Bronchitis', 'Respiratory', 'Inflammation of bronchial mucosal lining leading to productive cough.', 'Viral respiratory infections (rhinovirus, influenza) or acute chemical irritants.', 'Smoking exposure, air pollution, weakened immune defense.', 'Avoid smoking exposure, practice hand hygiene, get vaccinated.', 'Expectorants, hydration, rest, avoiding respiratory irritants.', 'Seek medical consultation if cough persists over 3 weeks or sputum contains blood.'),
(18, 'Gastritis', 'Gastrointestinal', 'Inflammation or erosion of the protective gastric mucosal lining.', 'Helicobacter pylori bacterial infection, chronic NSAID use, excessive alcohol.', 'Frequent painkiller use, severe physiological stress, H. pylori exposure.', 'Limit NSAID usage, avoid excessive alcohol and spicy trigger foods.', 'Proton pump inhibitors (PPIs), antacids, H. pylori antibiotic eradication.', 'Seek immediate medical care for vomiting blood, dark tarry stools, or severe stomach pain.'),
(19, 'Hepatitis', 'Gastrointestinal / Hepatic', 'Inflammation of liver tissue caused primarily by viral pathogens or toxins.', 'Hepatitis viruses (A, B, C, D, E), heavy alcohol consumption, autoimmune reactions.', 'Unprotected exposure to bodily fluids, contaminated water, heavy alcohol intake.', 'Hepatitis A & B vaccination, safe needle protocols, clean water consumption.', 'Antiviral medications, supportive liver care, complete alcohol abstinence.', 'Seek urgent medical attention for yellowing skin/eyes (jaundice) or dark brown urine.'),
(20, 'Fatty Liver Disease', 'Gastrointestinal / Hepatic', 'Excessive accumulation of triglycerides within hepatic cells (steatosis).', 'Metabolic dysfunction, insulin resistance, high fructose intake, heavy alcohol consumption.', 'Obesity, type 2 diabetes, high cholesterol, metabolic syndrome.', 'Weight reduction (7-10%), low-carb diet, regular aerobic exercise.', 'Dietary modification, lifestyle intervention, managing blood glucose.', 'Seek medical evaluation if experiencing persistent right upper quadrant abdominal discomfort.'),
(21, 'Chronic Kidney Disease', 'Renal', 'Gradual loss of renal filtration function over months to years.', 'Uncontrolled diabetes mellitus, long-standing hypertension, glomerulonephritis.', 'Diabetes, hypertension, family history of renal disease, prolonged NSAID use.', 'Strict blood sugar and blood pressure control, avoiding nephrotoxic drugs.', 'Renoprotective medications (ACE inhibitors), renal diet, dialysis in advanced stages.', 'Seek medical evaluation for swelling in legs/ankles, decreased urine output, or persistent nausea.'),
(22, 'Urinary Tract Infection (UTI)', 'Renal / Urological', 'Infection of urinary structures, most commonly the urinary bladder (cystitis).', 'Bacterial colonization (Escherichia coli) ascending through urethra into urinary bladder.', 'Female anatomy, sexual activity, urinary catheterization, inadequate hydration.', 'Adequate fluid intake, voiding after intercourse, maintaining personal hygiene.', 'Targeted antibiotic therapy, increased water intake.', 'Seek urgent medical attention if experiencing high fever, flank/back pain, or severe chills.'),
(23, 'Anemia', 'Hematological', 'Deficiency in healthy red blood cells or hemoglobin concentration impaired oxygen delivery.', 'Iron deficiency, vitamin B12/folate deficiency, chronic blood loss, bone marrow failure.', 'Inadequate iron diet, heavy menstrual bleeding, gastrointestinal bleeding.', 'Iron-rich balanced diet (leafy greens, meat), vitamin C intake.', 'Iron/vitamin supplementation, addressing underlying blood loss cause.', 'Seek immediate care for severe shortness of breath, dizziness upon standing, or chest tightness.'),
(24, 'Hypothyroidism', 'Endocrine', 'Underactive thyroid gland producing insufficient thyroid hormones (T3/T4).', 'Hashimoto autoimmune thyroiditis, thyroidectomy, iodine deficiency.', 'Female sex, middle age, autoimmune conditions, personal history of radiation.', 'Adequate dietary iodine intake, periodic TSH screening.', 'Daily levothyroxine hormone replacement therapy.', 'Seek medical review for progressive unexplained weight gain, extreme fatigue, or cold intolerance.'),
(25, 'Hyperthyroidism', 'Endocrine', 'Overactive thyroid gland producing excessive thyroid hormones.', 'Graves autoimmune disease, toxic multinodular goiter, thyroiditis.', 'Female sex, family history of Graves disease, high iodine exposure.', 'Regular thyroid monitoring, stress management.', 'Anti-thyroid medications (Methimazole), beta-blockers, radioactive iodine.', 'Seek immediate medical attention for rapid irregular heart rate (palpitations) or severe tremors.'),
(26, 'Common Cold', 'Respiratory', 'A mild viral infectious disease of the upper respiratory tract primarily affecting the nasal mucosa and throat.', 'Rhinoviruses, coronaviruses, adenoviruses, or enteroviruses.', 'Exposure to infected individuals, seasonal winter changes, psychological stress, sleep deprivation.', 'Frequent hand hygiene, avoiding touching facial mucous membranes, maintaining adequate hydration and rest.', 'Rest, oral hydration, warm saline gargles, over-the-counter decongestants or analgesics as appropriate.', 'Seek medical care if symptoms persist beyond 10-14 days, high fever develops, or wheezing occurs.'),
(27, 'Allergic Rhinitis', 'Respiratory', 'Inflammation of the interior nasal passages caused by an IgE-mediated allergic response to inhaled environmental allergens.', 'Inhaled allergens including tree/grass pollen, house dust mites, animal dander, and fungal spores.', 'Atopic genetic predisposition, family history of asthma or eczema, high environmental allergen exposure.', 'Minimize exposure to identified allergens, use HEPA filtration, keep windows closed during high pollen counts.', 'Nasal corticosteroid sprays, oral second-generation antihistamines, saline nasal rinses, allergen immunotherapy.', 'Seek evaluation if chronic nasal obstruction causes secondary sinusitis or impairs quality of sleep.'),
(28, 'Sinusitis', 'Respiratory', 'Inflammation or infection of the mucosal lining of the paranasal sinuses, causing facial pressure and nasal congestion.', 'Secondary bacterial infection following viral upper respiratory infection, allergic swelling, or anatomical nasal polyps.', 'Recent viral cold, allergic rhinitis, structural deviated septum, environmental smoke exposure.', 'Prompt management of colds and allergies, indoor humidification, nasal saline irrigation.', 'Nasal saline irrigation, decongestants, intranasal steroids, oral antibiotics if bacterial infection confirmed.', 'Seek urgent medical care if experiencing severe headache, periorbital swelling, vision changes, or high fever.'),
(29, 'Heart Failure', 'Cardiovascular', 'A chronic, progressive condition in which the cardiac muscle is unable to pump sufficient blood volume to meet systemic metabolic demands.', 'Long-standing hypertension, prior myocardial infarction, coronary artery disease, cardiomyopathy, or valvular heart disease.', 'Hypertension, history of heart attack, diabetes, obesity, smoking, excessive alcohol consumption.', 'Strict blood pressure control, coronary disease prevention, smoking cessation, low-sodium dietary habits.', 'ACE inhibitors/ARNs, beta-blockers, aldosterone antagonists, SGLT2 inhibitors, diuretics, fluid restriction, daily weight tracking.', 'Seek immediate emergency care for sudden severe breathlessness, inability to lie flat, or rapid unexplained weight gain (>3 lbs in 24h).'),
(30, 'Arrhythmia', 'Cardiovascular', 'Disruptions or irregularities in the electrical conduction system of the heart, resulting in bradycardia, tachycardia, or fibrillatory rhythm.', 'Ischemic heart disease, electrolyte imbalances, structural cardiac remodeling, caffeine, thyroid disease, or electrical channelopathies.', 'Underlying coronary disease, hypertension, electrolyte disturbances (potassium/magnesium), sleep apnea, stimulant use.', 'Limit caffeine and alcohol, avoid illicit stimulants, manage stress, monitor electrolyte balance.', 'Anti-arrhythmic medications, rate-control agents (beta-blockers), catheter ablation, cardioversion, pacemakers or ICDs.', 'Seek immediate emergency medical care for palpitations accompanied by syncope, chest pain, or severe dizziness.'),
(31, 'Angina Pectoris', 'Cardiovascular', 'Reversible chest pain or pressure resulting from transient myocardial ischemia due to inadequate coronary blood flow.', 'Atherosclerotic coronary artery stenosis restricting oxygen delivery during times of increased myocardial workload.', 'Coronary artery disease, hypertension, dyslipidemia, smoking, diabetes, sedentary lifestyle.', 'Manage cardiovascular risk factors, adhere to Mediterranean-style diet, smoking cessation, regular moderate exercise.', 'Sublingual nitroglycerin for acute episodes, beta-blockers, calcium channel blockers, statins, antiplatelet therapy.', 'Seek emergency medical services immediately if chest pain lasts longer than 10 minutes or does not resolve with rest and nitroglycerin.'),
(32, 'Peripheral Artery Disease', 'Cardiovascular', 'A circulatory condition in which atherosclerotic plaque narrows peripheral arteries, severely reducing blood flow to the limbs.', 'Systemic atherosclerosis affecting the abdominal aorta, iliac, femoral, and popliteal arterial branches.', 'Cigarette smoking, type 2 diabetes, chronic hypertension, advanced age, hypercholesterolemia.', 'Smoking cessation, routine walking exercise programs, glycemic and lipid control, blood pressure optimization.', 'Supervised exercise therapy, antiplatelet medications (aspirin/clopidogrel), statin therapy, cilostazol, endovascular revascularization.', 'Seek urgent care for resting foot pain, cold/pale extremities, or non-healing ulcers on the lower extremities.'),
(33, 'Prediabetes', 'Endocrine', 'A metabolic state where blood glucose levels are above normal ranges (HbA1c 5.7-6.4%) but not yet meeting the threshold for type 2 diabetes.', 'Progressive peripheral insulin resistance coupled with relative pancreatic beta-cell secretory compensation.', 'Overweight/obesity (BMI > 25), physical inactivity, age > 45, family history of type 2 diabetes, gestational diabetes history.', 'Structured lifestyle interventions: 7% sustained weight reduction, 150 minutes/week moderate physical exercise, whole-food diet.', 'Intensive dietary modification, aerobic and resistance training, routine HbA1c monitoring every 6-12 months, metformin where indicated.', 'Consult a physician for routine screening if persistent fatigue, increased thirst, or unexplained weight shifts occur.'),
(34, 'Obesity', 'Endocrine', 'A complex, chronic multifactorial disease characterized by excessive adiposity that impairs physical and metabolic health.', 'Energy imbalance between caloric consumption and metabolic expenditure, neuroendocrine appetite regulation dysregulation, genetics.', 'Sedentary lifestyle, high-density refined food availability, endocrine disruptors, chronic sleep disruption, genetic susceptibility.', 'Whole-food dietary patterns, regular daily physical activity, stress mitigation, adequate sleep, behavioral health support.', 'Comprehensive lifestyle therapy, medical nutritional therapy, pharmacotherapy (GLP-1 receptor agonists), bariatric metabolic surgery.', 'Seek healthcare consultation when excess weight contributes to joint pain, obstructive sleep apnea, or metabolic dysregulation.'),
(35, 'Polycystic Ovary Syndrome (PCOS)', 'Endocrine', 'A prevalent endocrine disorder in reproductive-aged females characterized by ovulatory dysfunction, hyperandrogenism, and polycystic ovarian morphology.', 'Complex genetic, neuroendocrine, and metabolic factors with underlying hyperinsulinemia and ovarian theca-cell androgen overproduction.', 'Family history of PCOS, insulin resistance, metabolic syndrome, obesity, sedentary lifestyle.', 'Weight management, low-glycemic dietary habits, regular physical activity to enhance peripheral insulin sensitivity.', 'Combined oral contraceptives, metformin for insulin resistance, lifestyle modification, anti-androgens (spironolactone), ovulation induction.', 'Consult a gynecologist or endocrinologist for irregular menstrual cycles, severe cystic acne, or difficulty conceiving.'),
(36, 'GERD (Acid Reflux)', 'Gastrointestinal', 'A chronic gastrointestinal disorder where stomach acid persistently refluxes backward into the esophagus, irritating the mucosal lining.', 'Transient lower esophageal sphincter (LES) relaxations, hiatal hernia, delayed gastric emptying, increased intra-abdominal pressure.', 'Obesity, pregnancy, hiatal hernia, smoking, late-night heavy meals, consumption of fatty, spicy, citrus, or caffeinated foods.', 'Elevate head of bed, avoid recumbency within 3 hours of meals, lose excess weight, avoid trigger foods, stop smoking.', 'Proton pump inhibitors (PPIs), H2-receptor antagonists, antacids, lifestyle modifications, endoscopic or surgical fundoplication.', 'Seek prompt evaluation for progressive dysphagia (trouble swallowing), unintentional weight loss, hematemesis, or anemia.'),
(37, 'Peptic Ulcer Disease', 'Gastrointestinal', 'Erosive mucosal lesions occurring in the protective inner lining of the stomach (gastric ulcer) or proximal small intestine (duodenal ulcer).', 'Helicobacter pylori bacterial colonization, chronic usage of nonsteroidal anti-inflammatory drugs (NSAIDs), hyperacidity.', 'H. pylori infection, regular NSAID or aspirin use, smoking, heavy alcohol consumption, severe physiological stress.', 'Eradicate H. pylori, minimize unprescribed NSAID use, co-prescribe gastroprotection (PPIs) when chronic NSAIDs are required, avoid smoking.', 'Antibiotic eradication therapy for H. pylori, proton pump inhibitors, mucosal protective agents, avoiding mucosal irritants.', 'Seek immediate emergency evaluation for vomiting frank blood or coffee-ground emesis, black tarry stools, or sudden acute abdominal pain.'),
(38, 'Gastroenteritis', 'Gastrointestinal', 'An acute inflammation of the gastrointestinal tract mucous membranes, involving both stomach and small intestine.', 'Viral pathogens (Norovirus, Rotavirus), bacterial toxins (Salmonella, Campylobacter, E. coli), or parasitic protozoa.', 'Consumption of contaminated water or unpasteurized food, poor hand hygiene, crowded living conditions, international travel.', 'Meticulous hand washing with soap and water, hygienic food storage and preparation, drinking clean treated water, rotavirus vaccination.', 'Oral rehydration therapy with balanced electrolyte solutions, gradual reintroduction of bland diet, zinc supplementation, antiemetics if needed.', 'Seek urgent care if signs of dehydration emerge (sunken eyes, dizziness, absence of urination), bloody stool, or inability to tolerate liquids.'),
(39, 'Irritable Bowel Syndrome (IBS)', 'Gastrointestinal', 'A common disorder of the brain-gut interaction characterized by recurrent abdominal pain related to defecation or changes in bowel habits.', 'Visceral hypersensitivity, altered gut-brain communication, gastrointestinal dysmotility, post-infectious inflammation, altered gut microbiome.', 'Female sex, severe preceding bacterial gastroenteritis, chronic psychological stress, early adverse life events.', 'Stress reduction, identifying individual food triggers, regular meal patterns, adequate dietary fiber and hydration.', 'Low-FODMAP dietary trial, soluble fiber (psyllium), antispasmodics, neuromodulators, gut-directed cognitive behavioral therapy.', 'Seek medical assessment for "red flag" symptoms: nocturnal symptoms, unintended weight loss, rectal bleeding, or onset after age 50.'),
(40, 'Chronic Constipation', 'Gastrointestinal', 'A functional gastrointestinal condition marked by infrequent, difficult, or incomplete evacuation of dry, hardened stool.', 'Inadequate dietary fiber, insufficient hydration, pelvic floor dyssynergia, slow transit colonic motility, side effect of medications.', 'Low-fiber diet, sedentary lifestyle, suppressing the urge to defecate, medications (opioids, calcium channel blockers, iron supplements).', 'High-fiber diet (25-35 grams/day), plentiful fluid intake, regular physical activity, establishing consistent toilet routines.', 'Bulk-forming laxatives (psyllium), osmotic laxatives (polyethylene glycol), pelvic floor physical therapy, biofeedback.', 'Consult a physician if constipation is accompanied by severe abdominal distension, vomiting, rectal bleeding, or sudden onset in older adults.'),
(41, 'Chronic Diarrhea', 'Gastrointestinal', 'Frequent loose, watery stools persisting continuously or intermittently for greater than four weeks in duration.', 'Inflammatory bowel disease (Crohn''s/Colitis), celiac disease, malabsorption syndromes, chronic parasitic infection, microscopic colitis.', 'Autoimmune history, family history of IBD or celiac disease, prior gastrointestinal surgeries, chronic antibiotic or metformin use.', 'Prompt investigation of dietary intolerances (gluten, lactose), hygienic water sources during travel, cautious antibiotic usage.', 'Etiology-specific treatment (gluten-free diet for celiac, anti-inflammatory therapy for IBD), electrolyte replenishment, anti-diarrheal agents.', 'Seek thorough clinical evaluation for chronic diarrhea accompanied by unintended weight loss, fever, anemia, or visible blood in stool.'),
(42, 'Gallstones', 'Gastrointestinal', 'Hardened mineral deposits formed inside the gallbladder, predominantly composed of crystallized cholesterol or bilirubin pigments.', 'Supersaturation of bile with cholesterol, gallbladder hypomotility, excessive biliary bilirubin secretion.', 'Female sex, age > 40, multiparity, rapid weight loss, obesity, high-fat diet, hemolytic blood disorders.', 'Maintain a healthy body weight gradually (avoid crash starvation diets), eat a balanced fiber-rich diet with healthy unsaturated fats.', 'Observation for asymptomatic stones; laparoscopic cholecystectomy for symptomatic recurrent biliary colic or acute cholecystitis.', 'Seek emergency medical evaluation for severe right upper quadrant pain radiating to shoulder, fever, persistent vomiting, or jaundice.'),
(43, 'Tension Headache', 'Neurological', 'The most prevalent type of primary headache, presenting as mild-to-moderate dull, band-like tightening pressure across the head and neck.', 'Myofascial trigger points, pericranial muscle tenderness, central pain sensitization, prolonged emotional stress.', 'Chronic emotional or occupational stress, poor ergonomic posture, ocular strain, clenching jaw/teeth, sleep deprivation.', 'Regular ergonomic breaks, adequate nocturnal sleep, stress management, hydration, stretching of cervical and shoulder muscles.', 'Over-the-counter analgesics (acetaminophen, NSAIDs), physical therapy, stress management techniques, tricyclic antidepressants for chronic cases.', 'Seek evaluation for sudden severe "thunderclap" headache, new headaches after age 50, or associated focal neurological deficits.'),
(44, 'Peripheral Neuropathy', 'Neurological', 'Damage to the peripheral nervous system leading to weakness, numbness, tingling, or burning sensations primarily in hands and feet.', 'Diabetic microvascular axonal damage, chronic alcoholism, vitamin B12 deficiency, chemotherapy toxicity, autoimmune disorders.', 'Poorly controlled diabetes mellitus, heavy alcohol consumption, chemotherapy treatments, nutritional deficiencies, renal disease.', 'Strict blood glucose control in diabetes, moderation of alcohol, adequate nutritional vitamin B12 intake, foot protective care.', 'Optimization of underlying cause, neuropathic pain agents (gabapentin, pregabalin, duloxetine), physical therapy, daily foot inspections.', 'Seek medical attention for progressive numbness spreading upward, unhealed foot ulcers, or difficulty with balance and walking.'),
(45, 'Kidney Stones', 'Renal / Urological', 'Solid mineral and acid salt crystalline aggregations that form within renal calyces and pass into the urinary tract.', 'Supersaturation of urine with calcium, oxalate, phosphate, or uric acid coupled with inadequate urinary fluid volume.', 'Low fluid intake, high dietary sodium/animal protein, family history of nephrolithiasis, hyperparathyroidism, gout.', 'Drink 2.5 to 3 liters of water daily to maintain clear dilute urine, limit sodium and excess animal protein, ensure normal calcium intake.', 'Adequate hydration, alpha-blockers (tamsulosin) to aid stone passage, oral analgesia, shock-wave lithotripsy or ureteroscopy for large stones.', 'Seek immediate emergency care for intractable flank pain, persistent vomiting, inability to urinate, or high fever with chills.'),
(46, 'Kidney Infection (Pyelonephritis)', 'Renal / Urological', 'An acute bacterial infection of the renal parenchyma and renal pelvis, usually ascending from the lower urinary tract.', 'Ascending spread of uropathogenic bacteria (primarily Escherichia coli) from cystitis through ureters into the kidney.', 'Untreated or recurrent lower urinary tract infections, female anatomy, urinary catheterization, kidney stones, pregnancy, diabetes.', 'Prompt, complete treatment of bladder infections, generous hydration, post-coital urination, proper perineal hygiene.', 'Empirical and culture-directed oral or intravenous antibiotics for 7-14 days, antipyretics, adequate oral or IV fluid hydration.', 'Seek emergency medical care immediately for high fever, severe flank pain, shaking chills, nausea, or confusion.'),
(47, 'Acne Vulgaris', 'Dermatological', 'A chronic inflammatory dermatological disorder of the pilosebaceous units characterized by comedones, papules, pustules, or cysts.', 'Excess sebum production, follicular hyperkeratinization, Cutibacterium acnes bacterial proliferation, and inflammatory mediator release.', 'Adolescent hormonal surges, androgen excess, family history, high-glycemic index diets, comedogenic cosmetic products.', 'Gentle non-abrasive facial cleansing twice daily, avoiding picking or squeezing lesions, non-comedogenic oil-free skincare.', 'Topical retinoids, benzoyl peroxide, topical/oral antibiotics, salicylic acid, hormonal therapies (oral contraceptives, spironolactone), oral isotretinoin.', 'Seek dermatological consultation for painful deep cysts, scarring acne lesions, or lack of response to non-prescription remedies.'),
(48, 'Eczema (Atopic Dermatitis)', 'Dermatological', 'A chronic, pruritic inflammatory skin condition characterized by defective epidermal barrier function and immune dysregulation.', 'Genetic mutations in the filaggrin (FLG) gene, epidermal skin barrier disruption, Th2-skewed immune hyperreactivity.', 'Personal or family history of atopy (asthma, allergic rhinitis), dry climates, frequent bathing with harsh soaps, environmental irritants.', 'Frequent skin moisturization with bland thick emollient ointments, lukewarm brief baths, fragrance-free detergents, avoiding wool clothing.', 'Liberal emollient moisturizers, topical corticosteroids, topical calcineurin inhibitors, phototherapy, biologic therapies (dupilumab).', 'Seek prompt medical attention if eczema lesions exhibit signs of bacterial superinfection (honey-colored crusting, pustules, severe pain).'),
(49, 'Psoriasis', 'Dermatological', 'A chronic autoimmune inflammatory dermatosis characterized by well-demarcated erythematous plaques covered with silvery micaceous scales.', 'Immune-mediated acceleration of epidermal keratinocyte turnover driven by the IL-23/IL-17 cytokine signaling pathway.', 'Genetic susceptibility (HLA-Cw6), physiological or psychological stress, streptococcal pharyngeal infection, smoking, obesity, alcohol.', 'Stress reduction, avoiding skin trauma/friction (Koebner phenomenon), maintaining healthy body weight, avoiding smoking and heavy drinking.', 'Topical corticosteroids, topical vitamin D analogs, phototherapy (narrowband UVB), systemic methotrexate, biologic targeted agents.', 'Consult a dermatologist for extensive cutaneous involvement, severe discomfort, or associated joint pain (psoriatic arthritis).'),
(50, 'Contact Dermatitis', 'Dermatological', 'An acute or chronic cutaneous inflammatory reaction elicited by direct contact with an external chemical, allergen, or physical irritant.', 'Either direct cytotoxic irritant injury (Irritant Contact Dermatitis) or delayed Type IV cell-mediated allergy (Allergic Contact Dermatitis).', 'Occupational chemical exposure (hairdressers, healthcare, cleaners), nickel jewelry, poison ivy/oak, fragrance ingredients, topical neomycin.', 'Identify and rigorously avoid contact with causative allergens or irritants, wear protective barrier gloves, wash skin immediately after accidental exposure.', 'Cool wet compresses, topical corticosteroid creams, oral antihistamines for pruritus, barrier repair creams.', 'Seek care if dermatitis affects eyes, face, or genitalia, spreads rapidly, or develops secondary bacterial pustules or cellulitis.'),
(51, 'Fungal Skin Infection', 'Dermatological', 'Superficial fungal colonization of the keratinized layer of skin, hair, or nails caused by dermatophytes or yeasts.', 'Dermatophyte fungi (Trichophyton, Microsporum, Epidermophyton) or Candida albicans yeast proliferating in warm, humid skin folds.', 'Warm humid environments, excessive perspiration, occlusive footwear, communal showers/gyms, diabetes mellitus, compromised immunity.', 'Keep skin clean and dry, wear breathable cotton clothing, dry thoroughly after bathing, wear sandals in public locker rooms and showers.', 'Topical antifungal creams (clotrimazole, terbinafine, miconazole) applied for 2-4 weeks, oral antifungals for widespread or nail infections.', 'Seek medical consultation if fungal rash does not improve after 2 weeks of over-the-counter treatment or spreads extensively.'),
(52, 'Urticaria (Hives)', 'Dermatological', 'A transient vascular reaction of the dermis characterized by intensely pruritic, raised, erythematous wheals with surrounding flare.', 'Mast cell and basophil degranulation with rapid release of histamine and vasodilatory mediators triggered by allergens, infections, or physical stimuli.', 'Viral infections, food allergies (nuts, shellfish), medications (NSAIDs, antibiotics), insect stings, physical stimuli (heat, cold, pressure).', 'Identify and avoid known specific triggering allergens, minimize physical skin friction, avoid unneeded NSAIDs during acute flares.', 'Second-generation H1-antihistamines (cetirizine, fexofenadine, loratadine), H2-blockers, cool compresses, oral corticosteroids for severe flares.', 'Seek immediate emergency care if hives occur with facial/lip/tongue swelling (angioedema), difficulty breathing, or dizziness (anaphylaxis).'),
(53, 'Osteoarthritis', 'Musculoskeletal', 'A progressive degenerative joint disease characterized by breakdown of articular cartilage, subchondral bone remodeling, and osteophyte formation.', 'Biomechanical joint stress, age-related chondrocyte senescence, repetitive mechanical microtrauma, low-grade joint inflammation.', 'Advanced age, female sex, obesity (excess load on weight-bearing joints), prior traumatic joint injury, repetitive occupational joint stress.', 'Maintain healthy body weight to reduce knee/hip mechanical loading, engage in low-impact aerobic exercise (swimming, cycling), avoid joint trauma.', 'Physical therapy, quadriceps muscle strengthening, weight loss, acetaminophen or topical NSAIDs, intra-articular injections, joint replacement surgery.', 'Consult an orthopedic specialist for progressive joint pain limiting ambulation or daily self-care activities.'),
(54, 'Rheumatoid Arthritis', 'Musculoskeletal', 'A chronic, systemic autoimmune disease characterized by symmetric inflammatory polyarthritis, synovial proliferation, and progressive joint destruction.', 'Autoimmune targeting of synovial tissue by autoantibodies (Rheumatoid Factor, anti-CCP), leading to chronic pannus formation and cartilage erosion.', 'Female sex, genetic predisposition (HLA-DRB1 alleles), cigarette smoking, family history of autoimmune disease.', 'Smoking cessation, maintaining optimal dental hygiene, early diagnostic assessment upon onset of symmetric joint swelling.', 'Disease-modifying antirheumatic drugs (DMARDs, e.g. methotrexate), biologic TNF/IL-6 inhibitors, short-term corticosteroids, physical therapy.', 'Seek urgent rheumatology evaluation within weeks of developing persistent symmetric joint swelling, morning stiffness > 1 hour, or hand deformities.'),
(55, 'Osteoporosis', 'Musculoskeletal', 'A systemic skeletal disease characterized by low bone mineral density and microarchitectural deterioration, resulting in heightened bone fragility.', 'Imbalance between osteoclastic bone resorption and osteoblastic bone formation, accelerated by postmenopausal estrogen decline or aging.', 'Postmenopausal female status, advanced age, low body weight, calcium/vitamin D deficiency, glucocorticoid therapy, sedentary lifestyle, smoking.', 'Adequate dietary calcium and vitamin D, regular weight-bearing and resistance training exercises, fall prevention strategies, smoking cessation.', 'Antiresorptive medications (bisphosphonates, denosumab), anabolic agents (teriparatide), calcium and vitamin D supplementation, DEXA scans.', 'Seek medical care following any low-trauma fall resulting in severe bone/hip pain, or progressive height loss and dorsal kyphosis.'),
(56, 'Gout', 'Musculoskeletal', 'A painful form of inflammatory crystal arthritis caused by the deposition of monosodium urate monohydrate crystals within articular and periarticular tissues.', 'Persistent hyperuricemia exceeding the saturation threshold due to renal urate underexcretion or excessive purine metabolism.', 'Male sex, high-purine diet (red meat, seafood, beer, distilled spirits), high-fructose corn syrup, obesity, hypertension, diuretics.', 'Limit high-purine foods, eliminate beer and sweetened beverages, maintain high daily hydration, manage weight, avoid crash dieting.', 'Acute flare: NSAIDs, colchicine, or corticosteroids. Long-term management: urate-lowering therapy (allopurinol, febuxostat) targeting uric acid < 6 mg/dL.', 'Seek prompt care for acute, excruciating monoarticular joint swelling (commonly the first metatarsophalangeal big toe joint).'),
(57, 'Muscle Strain', 'Musculoskeletal', 'An acute or repetitive stretch injury causing tearing of muscle fibers or their associated myotendinous junctions.', 'Overstretching, excessive eccentric muscular load, sudden violent contraction, or repetitive ergonomic fatigue without adequate warm-up.', 'Poor muscle flexibility, muscular fatigue, inadequate pre-exercise warm-up, prior muscle injury, sudden resumption of vigorous exertion.', 'Thorough dynamic warm-up before athletic activity, gradual progression of workout intensity, core muscle strengthening, ergonomic lifting form.', 'R.I.C.E. protocol (Rest, Ice, Compression, Elevation) initially, brief course of oral NSAIDs, gentle progressive stretching, physical therapy.', 'Seek medical evaluation for an audible muscle "pop", severe inability to bear weight, visible muscular defect, or significant hematoma.'),
(58, 'Vitamin B12 Deficiency', 'Hematological', 'A nutritional hematological and neurological disorder caused by insufficient cobalamin levels, leading to megaloblastic anemia and neuropathy.', 'Pernicious anemia (autoimmune destruction of gastric parietal cells / lack of intrinsic factor), strict vegan diet without supplementation, malabsorption.', 'Strict vegetarian/vegan diets, age > 65, chronic proton pump inhibitor or metformin use, prior gastric bypass or ileal resection, celiac disease.', 'Incorporate B12-rich foods (eggs, dairy, fortified cereals) or take regular oral cobalamin supplements if adhering to plant-based diets.', 'Oral high-dose vitamin B12 (1000 mcg daily) or intramuscular cyanocobalamin/hydroxocobalamin injections until stores are replenished.', 'Seek medical evaluation for persistent numbness in extremities, unsteady gait, cognitive changes, or unexplained fatigue and pale skin.'),
(59, 'Vitamin D Deficiency', 'Hematological', 'A systemic nutritional insufficiency resulting from inadequate synthesis or dietary intake of calciferol, impairing calcium and bone homeostasis.', 'Limited cutaneous synthesis from sunlight exposure, low dietary intake, malabsorption, renal/hepatic conversion impairments, pigmented skin.', 'Living in northern latitudes, limited outdoor sun exposure, extensive sunscreen use, darker skin pigmentation, obesity, malabsorptive bowel disease.', 'Sensible sun exposure, consuming vitamin D-fortified milk/cereals and fatty fish, routine daily supplementation of 800-2000 IU/day.', 'High-dose oral ergocalciferol (D2) or cholecalciferol (D3) therapy, followed by long-term maintenance supplementation and serum 25(OH)D monitoring.', 'Seek healthcare consultation for persistent diffuse musculoskeletal aching, proximal muscle weakness, or recurrent bone stress fractures.'),
(60, 'Sickle Cell Disease', 'Hematological', 'An inherited genetic hemoglobinopathy caused by a point mutation in the beta-globin gene, resulting in abnormal sickle-shaped red blood cells.', 'Homozygous inheritance of the HbS allele (glutamic acid substituted by valine at position 6 of the beta-globin chain).', 'African, Mediterranean, Middle Eastern, or South Asian ancestral descent; positive parental sickle cell carrier status.', 'Genetic counseling and carrier screening, avoiding cold exposure, preventing dehydration, avoiding high-altitude hypoxic triggers.', 'Hydroxyurea to boost fetal hemoglobin, routine vaccinations, prophylactic penicillin in children, hydration, multimodal pain crisis protocols.', 'Seek immediate emergency medical care for acute vaso-occlusive pain crises, acute chest syndrome (chest pain/fever/cough), or stroke symptoms.'),
(61, 'Generalized Anxiety', 'Psychological', 'An educational screening category for persistent, excessive, and uncontrollable worry regarding various everyday life events and activities.', 'Dysregulation of amygdala-prefrontal neurocircuitry, neurotransmitter imbalances (GABA, serotonin, norepinephrine), chronic psychosocial stress.', 'Family history of anxiety, major chronic life stress, personality traits (neuroticism), chronic physical illnesses, substance use.', 'Cognitive reframing, regular aerobic physical activity, consistent sleep hygiene, minimizing caffeine and stimulant consumption, mindfulness.', 'Evidence-based cognitive behavioral therapy (CBT), mindfulness-based stress reduction, SSRI or SNRI medications under psychiatric guidance.', 'Seek urgent mental health evaluation if anxiety causes panic attacks, severe functional impairment, or suicidal thoughts.'),
(62, 'Depressive Symptoms', 'Psychological', 'An educational screening category for persistent depressed mood, loss of interest or pleasure, low energy, and feelings of worthlessness.', 'Interactions between genetic vulnerability, neurochemical alterations, neuroendocrine dysregulation (HPA axis), and adverse life events.', 'Family history of mood disorders, chronic illness, severe interpersonal losses or trauma, chronic lack of social support, sleep disruption.', 'Regular cardiovascular physical activity, maintaining social connection, structured daily routines, balanced nutrition, exposure to morning daylight.', 'Psychotherapy (CBT, interpersonal therapy), structured exercise programs, antidepressant pharmacotherapy (SSRIs) supervised by clinicians.', 'Seek immediate emergency support or call a crisis lifeline (988 in the US) if experiencing thoughts of self-harm or suicide.'),
(63, 'Chronic Stress & Burnout', 'Psychological', 'A state of chronic physical and psychological exhaustion coupled with emotional depletion caused by prolonged unmanaged stress.', 'Sustained activation of the sympathetic-adreno-medullary and hypothalamic-pituitary-adrenal (HPA) axes without adequate recovery phases.', 'High workload environments, lack of perceived autonomy, caregiver demands, perfectionism, chronic financial strain, insufficient sleep.', 'Clear personal and professional boundaries, scheduled restorative downtime, peer support systems, regular physical movement, mindfulness.', 'Workplace/lifestyle restructuring, stress reduction coaching, sleep optimization, mindfulness-based stress reduction (MBSR), clinical counseling.', 'Seek professional psychological consultation if burnout leads to chronic depressive feelings, severe insomnia, or panic attacks.'),
(64, 'Insomnia & Sleep Disorder', 'Psychological', 'A condition characterized by persistent difficulty initiating, consolidating, or maintaining restorative sleep despite adequate opportunity.', 'Hyperarousal states of the central nervous system, circadian rhythm misalignment, poor sleep ergonomics, psychological distress.', 'Irregular sleep schedules, shift work, blue light screen use in bed, excessive caffeine/alcohol, chronic anxiety, sleep apnea.', 'Strict sleep hygiene: consistent sleep-wake schedule, dark/cool/quiet bedroom, avoiding screens 1 hour before bed, limiting caffeine after midday.', 'Cognitive Behavioral Therapy for Insomnia (CBT-I) as first-line gold standard, stimulus control, sleep restriction therapy, short-term sleep aids.', 'Consult a sleep specialist or physician if sleep disruption persists over 3 months, causes daytime sleepiness, or is accompanied by loud snoring/gasping.'),
(65, 'Metabolic Syndrome', 'Endocrine', 'A clustering of at least three concurrent cardiometabolic risk factors including central obesity, hypertension, hypertriglyceridemia, low HDL, and impaired fasting glucose.', 'Visceral adiposity-induced chronic low-grade inflammation, adipokine dysregulation, and systemic peripheral insulin resistance.', 'Sedentary lifestyle, high-carbohydrate refined diet, visceral abdominal obesity, advancing age, genetic predisposition.', 'Structured Mediterranean-style nutrition, 150 minutes/week moderate aerobic exercise plus resistance training, maintaining waist circumference < 40 in (men) or < 35 in (women).', 'Intensive therapeutic lifestyle intervention, targeted pharmacological management of individual risk factors (statins, antihypertensives, metformin).', 'Consult your primary healthcare provider for comprehensive cardiometabolic blood panel screening and personalized prevention planning.');

-- ==============================================================================
-- SEED DATA: 58 SYMPTOMS (Aligned with ML Features)
-- ==============================================================================

INSERT INTO `symptoms` (`id`, `name`, `symptom_key`, `body_system`, `severity`) VALUES
(1, 'High Blood Sugar / Thirst', 'high_blood_sugar', 'Endocrine', 'Moderate'),
(2, 'Frequent Urination (Polyuria)', 'frequent_urination', 'Renal', 'Moderate'),
(3, 'High Blood Pressure', 'high_blood_pressure', 'Cardiovascular', 'Severe'),
(4, 'Chest Pain / Angina', 'chest_pain', 'Cardiovascular', 'Emergency'),
(5, 'Shortness of Breath (Dyspnea)', 'shortness_of_breath', 'Respiratory', 'Severe'),
(6, 'Persistent Cough with Sputum', 'cough_with_sputum', 'Respiratory', 'Moderate'),
(7, 'Coughing Blood (Hemoptysis)', 'hemoptysis', 'Respiratory', 'Emergency'),
(8, 'High Fever (>100.4 F)', 'fever', 'Systemic', 'Severe'),
(9, 'Severe Chills / Rigors', 'chills', 'Systemic', 'Moderate'),
(10, 'Severe Joint / Bone Pain', 'joint_pain', 'Musculoskeletal', 'Moderate'),
(11, 'Severe Throbbing Headache', 'headache', 'Neurological', 'Moderate'),
(12, 'Involuntary Seizures / Convulsions', 'seizures', 'Neurological', 'Emergency'),
(13, 'Resting Hand Tremors', 'resting_tremor', 'Neurological', 'Moderate'),
(14, 'Progressive Memory Loss / Confusion', 'memory_loss', 'Neurological', 'Severe'),
(15, 'Respiratory Wheezing', 'wheezing', 'Respiratory', 'Severe'),
(16, 'Gastric Heartburn / Acid Reflux', 'heartburn', 'Gastrointestinal', 'Moderate'),
(17, 'Yellowing of Skin / Eyes (Jaundice)', 'jaundice', 'Hepatic', 'Severe'),
(18, 'Right Upper Quadrant Abdominal Pain', 'right_upper_quadrant_pain', 'Hepatic', 'Moderate'),
(19, 'Flank / Lower Back Pain', 'flank_pain', 'Renal', 'Moderate'),
(20, 'Painful Urination (Dysuria)', 'dysuria', 'Renal', 'Moderate'),
(21, 'Chronic Fatigue & Weakness', 'fatigue', 'Systemic', 'Mild'),
(22, 'Cold Intolerance / Hypothermia Sensitivity', 'cold_intolerance', 'Endocrine', 'Moderate'),
(23, 'Heat Intolerance & Excessive Sweating', 'heat_intolerance', 'Endocrine', 'Moderate'),
(24, 'Rapid Heart Palpitations / Tachycardia', 'palpitations', 'Cardiovascular', 'Moderate'),
(25, 'Unexplained Rapid Weight Loss', 'weight_loss', 'Systemic', 'Moderate'),
(26, 'Drenching Night Sweats', 'sweats', 'Systemic', 'Moderate'),
(27, 'Nausea & Loss of Appetite', 'nausea', 'Gastrointestinal', 'Moderate'),
(28, 'Persistent Vomiting', 'vomiting', 'Gastrointestinal', 'Moderate'),
(29, 'Dizziness & Lightheadedness', 'dizziness', 'Neurological', 'Moderate'),
(30, 'Generalized Abdominal Pain / Cramping', 'abdominal_pain', 'Gastrointestinal', 'Moderate'),
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
(58, 'Hematuria / Discolored Urine', 'blood_in_urine', 'Renal', 'Severe');

-- ==============================================================================
-- SEED DATA: DISEASE_SYMPTOMS MAPPING (250 Relationships)
-- ==============================================================================

INSERT INTO `disease_symptoms` (`disease_id`, `symptom_id`) VALUES
(1, 1),
(1, 2),
(1, 21),
(1, 25),
(1, 50),
(1, 51),
(2, 3),
(2, 11),
(2, 29),
(3, 4),
(3, 5),
(3, 21),
(3, 24),
(4, 5),
(4, 6),
(4, 15),
(4, 34),
(5, 4),
(5, 5),
(5, 6),
(5, 8),
(5, 9),
(6, 6),
(6, 7),
(6, 8),
(6, 25),
(6, 26),
(7, 5),
(7, 6),
(7, 8),
(7, 21),
(7, 36),
(8, 8),
(8, 9),
(8, 10),
(8, 11),
(8, 21),
(8, 46),
(9, 8),
(9, 10),
(9, 11),
(9, 21),
(9, 27),
(9, 40),
(10, 8),
(10, 9),
(10, 11),
(10, 26),
(10, 27),
(11, 8),
(11, 11),
(11, 21),
(11, 27),
(11, 30),
(11, 37),
(12, 11),
(12, 27),
(12, 28),
(12, 29),
(13, 11),
(13, 12),
(13, 29),
(14, 13),
(14, 21),
(14, 29),
(15, 14),
(15, 21),
(16, 5),
(16, 6),
(16, 15),
(16, 21),
(17, 5),
(17, 6),
(17, 8),
(17, 21),
(17, 33),
(18, 16),
(18, 27),
(18, 28),
(18, 30),
(19, 17),
(19, 21),
(19, 27),
(19, 30),
(20, 18),
(20, 21),
(20, 30),
(21, 2),
(21, 19),
(21, 21),
(21, 57),
(22, 2),
(22, 8),
(22, 19),
(22, 20),
(22, 58),
(23, 5),
(23, 21),
(23, 24),
(23, 29),
(24, 21),
(24, 22),
(24, 25),
(24, 52),
(24, 53),
(25, 23),
(25, 24),
(25, 25),
(25, 26),
(26, 31),
(26, 32),
(26, 33),
(26, 34),
(27, 31),
(27, 32),
(27, 35),
(27, 41),
(28, 6),
(28, 8),
(28, 11),
(28, 35),
(29, 5),
(29, 21),
(29, 24),
(29, 57),
(30, 4),
(30, 5),
(30, 24),
(30, 29),
(31, 4),
(31, 5),
(31, 21),
(32, 21),
(32, 46),
(32, 49),
(33, 1),
(33, 2),
(33, 21),
(34, 5),
(34, 10),
(34, 21),
(34, 52),
(35, 21),
(35, 43),
(35, 52),
(35, 53),
(36, 16),
(36, 27),
(36, 30),
(36, 33),
(37, 16),
(37, 27),
(37, 28),
(37, 30),
(38, 8),
(38, 27),
(38, 28),
(38, 30),
(38, 37),
(39, 30),
(39, 37),
(39, 38),
(39, 39),
(40, 30),
(40, 38),
(40, 39),
(41, 21),
(41, 27),
(41, 30),
(41, 37),
(42, 18),
(42, 27),
(42, 28),
(42, 30),
(43, 11),
(43, 21),
(43, 46),
(44, 21),
(44, 46),
(44, 49),
(45, 19),
(45, 20),
(45, 27),
(45, 58),
(46, 8),
(46, 9),
(46, 19),
(46, 20),
(47, 40),
(47, 43),
(48, 40),
(48, 41),
(48, 42),
(49, 10),
(49, 40),
(49, 42),
(50, 40),
(50, 41),
(50, 45),
(51, 40),
(51, 41),
(51, 42),
(52, 41),
(52, 44),
(52, 45),
(53, 10),
(53, 48),
(54, 10),
(54, 21),
(54, 45),
(54, 48),
(55, 10),
(55, 47),
(56, 10),
(56, 40),
(56, 45),
(57, 45),
(57, 46),
(57, 47),
(58, 14),
(58, 21),
(58, 29),
(58, 49),
(59, 10),
(59, 21),
(59, 46),
(59, 55),
(60, 5),
(60, 8),
(60, 10),
(60, 21),
(61, 24),
(61, 46),
(61, 54),
(61, 56),
(62, 21),
(62, 25),
(62, 55),
(62, 56),
(63, 11),
(63, 21),
(63, 54),
(63, 56),
(64, 11),
(64, 21),
(64, 56),
(65, 1),
(65, 3),
(65, 21),
(65, 52);

-- ==============================================================================
-- SEED DATA: SAMPLE USER FOR IMMEDIATE ACADEMIC DEMONSTRATION
-- Email: student@college.edu | Password: password123 (bcrypt hashed)
-- ==============================================================================

INSERT INTO `users` (`id`, `name`, `email`, `password`) VALUES
(1, 'Academic Student', 'student@college.edu', '$2y$10$7K6zxLVo/wkHjtr9VOavbOJLgNWI4ZqSLSHP6SS.9uneNwX.QddC.');

-- ==============================================================================
-- SEED DATA: HEALTH ARTICLES
-- ==============================================================================

INSERT INTO `health_articles` (`id`, `title`, `category`, `summary`, `content`) VALUES
(1, 'Understanding Type 2 Diabetes Prevention', 'Endocrine', 'Key lifestyle changes and dietary guidelines to maintain healthy blood glucose levels.', 'Type 2 Diabetes mellitus is characterized by peripheral insulin resistance and progressive pancreatic beta-cell dysfunction. Evidence-based preventative measures emphasize regular aerobic physical activity (at least 150 minutes per week), structured weight reduction for overweight individuals, and adherence to fiber-rich whole-food diets minimizing refined sugars and sweetened beverages.'),
(2, 'Hypertension Management and Cardiovascular Health', 'Cardiovascular', 'Practical sodium management and blood pressure screening protocols.', 'Hypertension increases risk for coronary artery disease, stroke, and chronic kidney disease. Standard clinical guidelines recommend periodic ambulatory blood pressure monitoring, dietary sodium restriction below 2,300 mg per day (DASH dietary protocol), regular aerobic exercise, and smoking cessation.'),
(3, 'Respiratory Health: Early Symptoms of Chronic Lung Disease', 'Respiratory', 'Recognizing chronic cough, wheezing, and dyspnea before severe lung function decline.', 'Chronic obstructive pulmonary disease (COPD) and asthma represent major causes of chronic respiratory impairment. Early detection relies on identifying persistent symptoms including exertional dyspnea, wheezing, and morning cough with sputum. Tobacco cessation is the single most effective intervention to halt COPD disease progression.'),
(4, 'AI and Machine Learning in Modern Healthcare Diagnostics', 'Technology', 'An overview of machine learning algorithms supporting healthcare triage and clinical decision making.', 'Machine learning classification models, including Logistic Regression, Random Forests, and Neural Networks, process complex multi-symptom clinical data to provide statistical decision assistance. In academic and decision-support systems, these models assist triage by identifying probabilistic condition likelihoods, while clinical validation remains the domain of qualified medical professionals.');

SET FOREIGN_KEY_CHECKS = 1;
