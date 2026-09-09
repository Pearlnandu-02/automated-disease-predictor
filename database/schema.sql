-- AI Healthcare - Intelligent Disease Prediction & Health Assistance System Database Schema

SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `ai_healthcare` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ai_healthcare`;

DROP TABLE IF EXISTS `prediction_history`;
DROP TABLE IF EXISTS `disease_symptoms`;
DROP TABLE IF EXISTS `health_articles`;
DROP TABLE IF EXISTS `symptoms`;
DROP TABLE IF EXISTS `diseases`;
DROP TABLE IF EXISTS `users`;

-- 1. Users Table
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Diseases Table (25 Diseases)
CREATE TABLE `diseases` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `category` VARCHAR(100) NOT NULL,
  `short_description` TEXT NOT NULL,
  `causes` TEXT NOT NULL,
  `risk_factors` TEXT NOT NULL,
  `prevention` TEXT NOT NULL,
  `management` TEXT NOT NULL,
  `when_to_seek_care` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Symptoms Table
CREATE TABLE `symptoms` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `symptom_key` VARCHAR(100) NOT NULL UNIQUE,
  `body_system` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(20) DEFAULT 'Moderate'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Disease-Symptoms Junction Table
CREATE TABLE `disease_symptoms` (
  `disease_id` INT NOT NULL,
  `symptom_id` INT NOT NULL,
  PRIMARY KEY (`disease_id`, `symptom_id`),
  CONSTRAINT `fk_ds_disease` FOREIGN KEY (`disease_id`) REFERENCES `diseases`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ds_symptom` FOREIGN KEY (`symptom_id`) REFERENCES `symptoms`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Prediction History Table
CREATE TABLE `prediction_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `symptoms_selected` TEXT NOT NULL,
  `predicted_disease` VARCHAR(100) NOT NULL,
  `confidence` FLOAT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_ph_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Health Articles Table
CREATE TABLE `health_articles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(200) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `summary` TEXT NOT NULL,
  `content` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------
-- SEED DATA: 25 DISEASES
-- ----------------------------------------------------

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

-- ----------------------------------------------------
-- SEED DATA: SYMPTOMS
-- ----------------------------------------------------

INSERT INTO `symptoms` (`id`, `name`, `symptom_key`, `body_system`, `severity`) VALUES
(1, 'High Blood Sugar / Thirst', 'glucose_high', 'Endocrine', 'Moderate'),
(2, 'Frequent Urination', 'polyuria', 'Renal', 'Moderate'),
(3, 'High Blood Pressure', 'hypertension', 'Cardiovascular', 'Severe'),
(4, 'Chest Pain / Angina', 'chest_pain', 'Cardiovascular', 'Emergency'),
(5, 'Shortness of Breath', 'dyspnea', 'Respiratory', 'Severe'),
(6, 'Persistent Cough', 'cough', 'Respiratory', 'Moderate'),
(7, 'High Fever', 'fever_high', 'Systemic', 'Severe'),
(8, 'Chills and Sweating', 'chills', 'Systemic', 'Moderate'),
(9, 'Severe Headache', 'headache', 'Neurological', 'Moderate'),
(10, 'Throbbing Unilateral Pain', 'migraine_pain', 'Neurological', 'Moderate'),
(11, 'Seizures / Tremors', 'seizures', 'Neurological', 'Emergency'),
(12, 'Memory Loss / Confusion', 'cognitive_decline', 'Neurological', 'Severe'),
(13, 'Resting Tremors', 'resting_tremor', 'Neurological', 'Moderate'),
(14, 'Fatigue and Weakness', 'fatigue', 'Systemic', 'Mild'),
(15, 'Yellowing Skin / Eyes (Jaundice)', 'jaundice', 'Hepatic', 'Severe'),
(16, 'Abdominal Pain / Gastritis', 'abdominal_pain', 'Gastrointestinal', 'Moderate'),
(17, 'Nausea and Vomiting', 'nausea', 'Gastrointestinal', 'Moderate'),
(18, 'Painful Urination (Dysuria)', 'dysuria', 'Renal', 'Moderate'),
(19, 'Swelling in Legs / Ankles', 'edema', 'Renal', 'Moderate'),
(20, 'Pale Skin / Anemia', 'pallor', 'Hematological', 'Moderate'),
(21, 'Weight Gain / Cold Intolerance', 'hypo_weight', 'Endocrine', 'Moderate'),
(22, 'Weight Loss / Palpitations', 'hyper_weight', 'Endocrine', 'Moderate'),
(23, 'Wheezing / Bronchospasm', 'wheezing', 'Respiratory', 'Severe'),
(24, 'Coughing Blood (Hemoptysis)', 'cough_blood', 'Respiratory', 'Emergency'),
(25, 'Night Sweats', 'night_sweats', 'Systemic', 'Moderate'),
(26, 'Joint / Bone Pain', 'joint_pain', 'Musculoskeletal', 'Moderate'),
(27, 'Loss of Taste or Smell', 'anosmia', 'Neurological', 'Moderate'),
(28, 'Diarrhea / Loose Stools', 'diarrhea', 'Gastrointestinal', 'Moderate'),
(29, 'Dark Brown Urine', 'dark_urine', 'Hepatic', 'Severe'),
(30, 'Skin Rash / Rose Spots', 'skin_rash', 'Dermatological', 'Moderate');

-- ----------------------------------------------------
-- SEED DATA: DISEASE_SYMPTOMS MAPPING
-- ----------------------------------------------------

INSERT INTO `disease_symptoms` (`disease_id`, `symptom_id`) VALUES
(1, 1), (1, 2), (1, 14), (1, 21),
(2, 3), (2, 9), (2, 14),
(3, 4), (3, 5), (3, 3), (3, 14),
(4, 5), (4, 6), (4, 23),
(5, 7), (5, 6), (5, 5), (5, 4),
(6, 6), (6, 24), (6, 25), (6, 14),
(7, 7), (7, 6), (7, 5), (7, 27),
(8, 7), (8, 6), (8, 8), (8, 14),
(9, 7), (9, 9), (9, 26), (9, 14),
(10, 7), (10, 8), (10, 9), (10, 14),
(11, 7), (11, 16), (11, 30), (11, 28),
(12, 9), (12, 10), (12, 17),
(13, 11), (13, 12),
(14, 13), (14, 14),
(15, 12), (15, 14),
(16, 5), (16, 6), (16, 23), (16, 14),
(17, 6), (17, 5), (17, 14),
(18, 16), (18, 17),
(19, 15), (19, 29), (19, 14), (19, 17),
(20, 16), (20, 14), (20, 15),
(21, 19), (21, 14), (21, 17), (21, 3),
(22, 18), (22, 2), (22, 16),
(23, 14), (23, 20), (23, 5),
(24, 21), (24, 14),
(25, 22), (25, 14);

SET FOREIGN_KEY_CHECKS = 1;
