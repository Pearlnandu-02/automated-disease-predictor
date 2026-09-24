import pymysql

new_diseases = [
    {
        'name': 'Fever',
        'category': 'General Health',
        'short_description': 'A temporary elevation in body temperature above normal (typically > 38°C or 100.4°F), often serving as an adaptive physiological defense against infection.',
        'causes': 'Viral infections (influenza, common cold, COVID-19), bacterial pathogens (strep, urinary infections), inflammatory conditions, or immunization responses.',
        'risk_factors': 'Exposure to infectious agents, weakened immune defenses, close contact with sick individuals, extreme physical exertion in hot environments.',
        'prevention': 'Frequent hand hygiene, routine vaccinations, avoiding close contact with sick persons, preparing food safely, and maintaining hydration.',
        'management': 'Adequate fluid replenishment, rest, antipyretics (acetaminophen or ibuprofen if clinically suitable), light clothing, and room temperature control.',
        'when_to_seek_care': 'Seek emergency care for temperature > 39.4°C (103°F), fever lasting > 3 days, stiff neck, confusion, breathing difficulty, or persistent vomiting.'
    },
    {
        'name': 'Dehydration',
        'category': 'General Health',
        'short_description': 'A deficit in total body water resulting from fluid loss exceeding intake, disrupting vital cellular and metabolic electrolyte homeostasis.',
        'causes': 'Inadequate fluid intake, profuse perspiration from heat or exertion, prolonged vomiting, diarrhea, high fever, or untreated diabetes mellitus.',
        'risk_factors': 'Extreme age (infants and elderly), intense physical labor, hot humid weather, chronic illnesses, diuretic medications, febrile illnesses.',
        'prevention': 'Drink clean fluids regularly throughout the day, increase intake during exercise or hot weather, consume electrolyte solutions during illness.',
        'management': 'Oral rehydration therapy with balanced oral electrolyte solutions; severe cases require intravenous isotonic crystalloid hydration.',
        'when_to_seek_care': 'Seek emergency medical evaluation for severe dizziness, confusion, inability to keep liquids down, absence of urination > 8 hours, or fainting.'
    },
    {
        'name': 'Fatigue',
        'category': 'General Health',
        'short_description': 'A persistent, overwhelming feeling of physical or mental exhaustion that is not relieved by normal sleep and impairs daily functional capacity.',
        'causes': 'Chronic sleep deficiency, anemia, hypothyroidism, major depression, fibromyalgia, chronic infections, poor nutrition, or underlying systemic disease.',
        'risk_factors': 'High chronic stress, sleep apnea, sedentary lifestyle, poor diet, shift work, chronic medical conditions, nutritional deficiencies.',
        'prevention': 'Establish consistent 7-9 hour sleep routines, engage in daily moderate physical exercise, consume nutrient-dense foods, manage psychological stress.',
        'management': 'Investigate and address underlying systemic causes, cognitive behavioral sleep therapy, balanced nutrition, graded physical exercise.',
        'when_to_seek_care': 'Seek prompt medical evaluation if fatigue is accompanied by unexplained weight loss, shortness of breath, chest pain, or swollen lymph nodes.'
    },
    {
        'name': 'Coronary Artery Disease',
        'category': 'Cardiovascular',
        'short_description': 'Impairment of blood flow through coronary arteries caused by progressive atherosclerotic plaque buildup, restricting myocardial oxygenation.',
        'causes': 'Atherosclerosis initiated by endothelial injury, lipid accumulation, and chronic vascular inflammation.',
        'risk_factors': 'Elevated LDL cholesterol, hypertension, cigarette smoking, diabetes mellitus, obesity, sedentary lifestyle, family history of early heart disease.',
        'prevention': 'Adopt heart-healthy Mediterranean diet, engage in 150 mins/week aerobic activity, maintain healthy blood pressure and lipid levels, quit smoking.',
        'management': 'Statins, antiplatelet therapy (aspirin), beta-blockers, ACE inhibitors, cardiac rehabilitation, and percutaneous coronary intervention when indicated.',
        'when_to_seek_care': 'Seek emergency care immediately for crushing chest pain, pain radiating to jaw or left arm, cold sweats, or sudden shortness of breath.'
    },
    {
        'name': 'Stroke',
        'category': 'Neurological',
        'short_description': 'Acute neurological deficit caused by disrupted cerebral perfusion (ischemic stroke, 87%) or intracranial vascular rupture (hemorrhagic stroke).',
        'causes': 'Thromboembolism from large-artery atherosclerosis, cardiac emboli (atrial fibrillation), or cerebral aneurysm/arteriovenous malformation rupture.',
        'risk_factors': 'Chronic hypertension, atrial fibrillation, smoking, diabetes, carotid stenosis, dyslipidemia, advanced age, previous transient ischemic attack (TIA).',
        'prevention': 'Strict blood pressure control, anticoagulation for atrial fibrillation, smoking cessation, cholesterol management, healthy body weight.',
        'management': 'Immediate emergency thrombolysis (IV rtPA) within 4.5 hours, mechanical endovascular thrombectomy, neurointensive monitoring, rehabilitation.',
        'when_to_seek_care': 'CALL EMERGENCY IMMEDIATELY upon any FAST sign: Face drooping, Arm weakness, Speech difficulty, Time to call emergency.'
    },
    {
        'name': 'Melanoma',
        'category': 'Skin',
        'short_description': 'The most aggressive form of skin cancer arising from malignant transformation of melanocytes, capable of rapid metastatic dissemination if untreated.',
        'causes': 'DNA damage primarily induced by solar ultraviolet (UV) radiation (especially intermittent sunburns) and genetic mutations (BRAF, CDKN2A).',
        'risk_factors': 'Fair skin that burns easily, history of blistering sunburns, high mole count (>50), atypical dysplastic nevi, family history of melanoma, tanning bed use.',
        'prevention': 'Broad-spectrum SPF 30+ sunscreen daily, seeking shade during peak UV hours (10 AM - 4 PM), protective clothing, avoiding artificial tanning beds.',
        'management': 'Wide local surgical excision, sentinel lymph node biopsy, targeted molecular therapies (BRAF/MEK inhibitors), immune checkpoint inhibitors (PD-1).',
        'when_to_seek_care': 'Consult a dermatologist promptly for any mole exhibiting ABCDE warning signs (Asymmetry, Border irregularity, Color variegation, Diameter >6mm, Evolving).'
    },
    {
        'name': 'Basal Cell Carcinoma',
        'category': 'Skin',
        'short_description': 'The most prevalent cutaneous malignancy worldwide, arising from basal keratinocytes, characterized by slow growth and rare distant metastasis.',
        'causes': 'Cumulative chronic ultraviolet (UVB/UVA) radiation exposure damaging PTCH1 and p53 tumor suppressor genes.',
        'risk_factors': 'Light skin phototypes (Fitzpatrick I-II), cumulative lifetime sun exposure, age over 50, immune suppression, prior radiation exposure.',
        'prevention': 'Daily application of broad-spectrum sunscreen, wearing wide-brimmed hats and UV-blocking sunglasses, routine annual skin screenings.',
        'management': 'Surgical excision, Mohs micrographic surgery for facial lesions, curettage and electrodesiccation, topical imiquimod, or targeted Hedgehog inhibitors.',
        'when_to_seek_care': 'Seek dermatological evaluation for pearly pink bumps with rolled edges, non-healing sores that bleed easily, or persistent scaly patches.'
    },
    {
        'name': 'Actinic Keratosis',
        'category': 'Skin',
        'short_description': 'A pre-malignant cutaneous lesion caused by chronic ultraviolet damage, presenting as rough, scaly or gritty patches that may progress to squamous cell carcinoma.',
        'causes': 'Cumulative lifetime ultraviolet radiation inducing TP53 mutations in epidermal keratinocytes.',
        'risk_factors': 'Older age, fair skin, bald scalp, outdoor occupations, extensive solar exposure, immunosuppressed status.',
        'prevention': 'Rigorous sun protection (SPF 50+), wearing UV protective hats and clothing, avoiding peak mid-day sun, routine dermatological exams.',
        'management': 'Cryotherapy with liquid nitrogen, topical 5-fluorouracil (5-FU), imiquimod cream, photodynamic therapy (PDT), field directed therapies.',
        'when_to_seek_care': 'Consult a dermatologist for rough, sandpaper-like or crusty skin spots that persist, enlarge, become tender, or develop indurated bases.'
    }
]

def run():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='ai_healthcare')
    with conn.cursor() as cursor:
        for d in new_diseases:
            cursor.execute('SELECT id FROM diseases WHERE name = %s', (d['name'],))
            row = cursor.fetchone()
            if not row:
                cursor.execute('''
                    INSERT INTO diseases (name, category, short_description, causes, risk_factors, prevention, management, when_to_seek_care)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (d['name'], d['category'], d['short_description'], d['causes'], d['risk_factors'], d['prevention'], d['management'], d['when_to_seek_care']))
                print('Inserted:', d['name'])
            else:
                print('Already exists:', d['name'])
        conn.commit()

        cursor.execute('SELECT COUNT(*) FROM diseases')
        print('Total diseases now in DB:', cursor.fetchone()[0])

if __name__ == '__main__':
    run()
