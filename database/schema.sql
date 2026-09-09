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
-- SEED DATA: 25 DISEASES
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
(25, 'Hyperthyroidism', 'Endocrine', 'Overactive thyroid gland producing excessive thyroid hormones.', 'Graves autoimmune disease, toxic multinodular goiter, thyroiditis.', 'Female sex, family history of Graves disease, high iodine exposure.', 'Regular thyroid monitoring, stress management.', 'Anti-thyroid medications (Methimazole), beta-blockers, radioactive iodine.', 'Seek immediate medical attention for rapid irregular heart rate (palpitations) or severe tremors.');

-- ==============================================================================
-- SEED DATA: 30 SYMPTOMS (Aligned with ML Features)
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
(30, 'Generalized Abdominal Pain / Cramping', 'abdominal_pain', 'Gastrointestinal', 'Moderate');

-- ==============================================================================
-- SEED DATA: DISEASE_SYMPTOMS MAPPING (93 Relationships)
-- ==============================================================================

INSERT INTO `disease_symptoms` (`disease_id`, `symptom_id`) VALUES
(1, 1), (1, 2), (1, 21), (1, 25),
(2, 3), (2, 11), (2, 29),
(3, 4), (3, 5), (3, 21), (3, 24),
(4, 5), (4, 15), (4, 6),
(5, 8), (5, 6), (5, 4), (5, 5),
(6, 6), (6, 7), (6, 8), (6, 26), (6, 25),
(7, 8), (7, 5), (7, 6), (7, 21),
(8, 8), (8, 9), (8, 11), (8, 10), (8, 21),
(9, 8), (9, 10), (9, 11), (9, 21), (9, 27),
(10, 8), (10, 9), (10, 26), (10, 11), (10, 27),
(11, 8), (11, 30), (11, 11), (11, 21), (11, 27),
(12, 11), (12, 27), (12, 28), (12, 29),
(13, 12), (13, 29), (13, 11),
(14, 13), (14, 21), (14, 29),
(15, 14), (15, 21),
(16, 5), (16, 6), (16, 15), (16, 21),
(17, 6), (17, 5), (17, 8), (17, 21),
(18, 16), (18, 27), (18, 28), (18, 30),
(19, 17), (19, 21), (19, 27), (19, 30),
(20, 18), (20, 21), (20, 30),
(21, 21), (21, 19), (21, 2),
(22, 20), (22, 2), (22, 19), (22, 8),
(23, 21), (23, 29), (23, 5), (23, 24),
(24, 21), (24, 22), (24, 25),
(25, 24), (25, 23), (25, 25), (25, 26);

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
