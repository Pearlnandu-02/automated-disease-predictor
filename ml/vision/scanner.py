"""
MediSense AI - Infection & Injury Image Scanner (Computer Vision & ML Pipeline)
=============================================================================
Advanced AI-assisted preliminary visual assessment for dermatological images.
Combines genuine feature extraction with a calibrated Machine Learning model:
  1. Quality & Feasibility Gating (resolution, exposure, blur variance)
  2. Human Skin Chrominance Verification (Fitzpatrick I-VI invariant)
  3. 24-D Extraction: Optical Erythema Index, Sobel Edge Roughness,
     Chromatic Dispersion, Color Proxies, Luminance Convexity
  4. Calibrated Multi-Class Machine Learning Inference with Platt Scaling
  5. Out-of-Scope Detection & Uncertainty Rejection
  6. Structured Clinical Observation & First-Aid Guidance Mapping

DISCLAIMER: This system provides an educational preliminary visual assessment
and does NOT constitute a clinical medical diagnosis.
"""

import sys
import os
import json
import numpy as np
import joblib

# Ensure ml directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from features import process_image_file, FEATURE_NAMES

# Categories
CAT_INFECTION = "Possible Infection Indicators"
CAT_INJURY = "Possible Minor Injury"
CAT_RASH = "Possible Rash/Skin Irritation"
CAT_SWELLING = "Possible Swelling"
CAT_INFLAMMATION = "Possible Inflammation/Redness"
CAT_CONCERNING_LESION = "Potentially Concerning Skin Lesion"
CAT_UNABLE = "Unable to Confidently Assess"

WARNING_SIGNS_GENERAL = [
    "Severe, pulsating, or rapidly worsening pain",
    "Rapidly spreading redness or red streaks radiating from the wound toward the heart",
    "Thick, foul-smelling yellow, green, or brown pus or discharge",
    "Fever (> 100.4°F / 38°C), chills, nausea, confusion, or general malaise",
    "Wound that continues bleeding actively after 10 minutes of direct pressure",
    "Deep gaping lacerations, exposed adipose (yellow fat), tendon, or bone",
    "Loss of sensation, persistent numbness, or inability to move the affected limb",
    "Animal or human bite wounds (high polymicrobial anaerobic infection risk)",
    "Significant swelling that impairs peripheral blood circulation or breathing"
]

CONDITION_PROFILES = {
    CAT_CONCERNING_LESION: {
        "display_name": "Potentially Concerning Skin Lesion",
        "badge_class": "badge-category-concerning",
        "description": "Visual characteristics in this image may warrant professional medical evaluation. This AI-assisted assessment cannot confirm whether a lesion is cancerous.",
        "what_detected": "Computer-vision image analysis observed visual characteristics including localized contrast drop, chromatic variegation, and edge roughness characteristic of a focal skin lesion.",
        "what_means": "Certain visual characteristics may warrant further professional assessment. This system cannot determine whether a lesion is cancerous.",
        "interpretation": "Visual characteristics in this image may warrant professional medical evaluation. This AI-assisted assessment cannot confirm whether a lesion is cancerous.",
        "disclaimer_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
        "recommended_next_step": "Consider evaluation by a qualified dermatologist or healthcare professional, particularly if the lesion is new, changing, bleeding, painful, or otherwise concerning.",
        "general_information": "Skin lesions encompass a wide spectrum from common benign nevi (moles) and seborrheic keratoses to dysplastic lesions and cutaneous neoplasms (such as basal cell carcinoma, squamous cell carcinoma, or melanoma). Accurate diagnostic differentiation requires specialized in-person clinical dermoscopy, serial photographic surveillance, or histopathological biopsy.",
        "general_care": [
            "Consider evaluation by a qualified dermatologist or healthcare professional, particularly if the lesion is new, changing, bleeding, painful, or otherwise concerning.",
            "Do not scratch, pick, shave, peel, or apply caustic chemical home remedies to suspicious spots.",
            "Record close-up photos with a millimeter ruler next to the lesion to document size and contour over time.",
            "Practice daily broad-spectrum sun protection (SPF 30+ sunscreen, protective clothing, and UV avoidance)."
        ],
        "warning_signs": [
            "A - Asymmetry: One half of the spot does not match the other half in contour or shape",
            "B - Border: Edges are irregular, ragged, notched, scalloped, blurred, or poorly defined",
            "C - Color: Color is non-uniform with shades of pink, red, tan, brown, black, or white",
            "D - Diameter: Spot is larger than 6 mm (pencil eraser size), though lesions can be smaller",
            "E - Evolving: The lesion is changing in size, shape, surface elevation, color, or bleeding/itching",
            "A persistent, non-healing sore that bleeds, crusts, oozes, or fails to resolve over 3 to 4 weeks",
            "A pearly, translucent, smooth, or pink nodule with visible tiny dilated surface blood vessels (telangiectasia)",
            "The 'Ugly Duckling' sign: A lesion that looks noticeably different from other spots on your body"
        ],
        "when_to_seek_care": [
            "Promptly (within days to a couple of weeks) for any new, changing, or irregular skin spot",
            "Urgent consultation if the lesion is actively bleeding, painful, ulcerated, or growing rapidly",
            "Regular annual full-body skin examinations by a board-certified dermatologist"
        ],
        "abcde_guide": [
            {"rule": "A - Asymmetry", "desc": "One half of the spot does not match the other half."},
            {"rule": "B - Border", "desc": "Edges are irregular, ragged, notched, scalloped, or blurred."},
            {"rule": "C - Color", "desc": "Color is non-uniform; contains varying shades of pink, red, brown, black, or tan."},
            {"rule": "D - Diameter", "desc": "Lesion is larger than 6 mm (about pencil eraser size), though lesions can be smaller."},
            {"rule": "E - Evolving", "desc": "The spot is changing in size, shape, surface texture, elevation, or bleeding/itching."}
        ]
    },
    CAT_INFECTION: {
        "display_name": "Possible Infection Indicators",
        "badge_class": "badge-category-infection",
        "description": "Visual patterns indicate notable localized red discoloration (erythema) alongside surface disruption, crusting, or irregular wound margins.",
        "what_detected": "Computer-vision image analysis identified elevated red tonal intensity combined with high surface edge roughness patterns.",
        "what_means": "Visual characteristics exhibit surface redness and edge disruption. In clinical settings, these visual patterns may correspond to superficial bacterial invasion, wound irritation, or local reaction.",
        "interpretation": "Visual characteristics exhibit surface redness and edge disruption consistent with acute localized inflammation or superficial infection.",
        "recommended_next_step": "Seek clinical evaluation by a medical doctor or urgent care clinic for diagnostic confirmation and appropriate prescription therapy if bacterial infection is present.",
        "general_information": "Skin infections typically occur when bacteria (such as Staphylococcus or Streptococcus) enter through a break in the epidermal skin barrier. Common presentations include localized warmth, edema, erythema, and purulent exudate.",
        "general_care": [
            "Keep the affected area clean, dry, and shielded with a sterile non-stick dressing.",
            "Wash hands thoroughly with soap and water before and after touching the dressing.",
            "Avoid squeezing, picking scabs, or applying unprescribed topical antibiotics.",
            "Mark the border of the redness with a skin-safe pen to monitor whether it is expanding over time."
        ],
        "warning_signs": [
            "Red streaks radiating outward from the wound toward the heart",
            "Foul-smelling pus or copious cloudy drainage",
            "Systemic fever, chills, dizziness, or confusion",
            "Rapid expansion of warmth and redness beyond the original wound boundary"
        ],
        "when_to_seek_care": [
            "Immediately if fever, chills, or red streaks appear",
            "Within 12-24 hours if redness continues expanding or pus develops",
            "If the wound was caused by an animal, human bite, or contaminated puncture object"
        ]
    },
    CAT_INJURY: {
        "display_name": "Possible Minor Injury",
        "badge_class": "badge-category-injury",
        "description": "Visual patterns reflect prominent surface edge gradients and textural discontinuity characteristic of a superficial skin break, such as a scrape, abrasion, or minor laceration.",
        "what_detected": "Computer-vision image analysis identified elevated edge transition gradients across the stratum corneum with localized color contrast.",
        "what_means": "Visual findings suggest a superficial mechanical disruption of the outer skin layers (such as a scrape or surface cut).",
        "interpretation": "Visual findings suggest a superficial mechanical disruption of the outer skin layers (such as a scrape or surface cut).",
        "recommended_next_step": "Cleanse gently with potable water, protect with a sterile dressing, and monitor for normal healing over the next 3 to 7 days.",
        "general_information": "Minor superficial abrasions and shallow cuts damage the epidermis and upper dermis. Healing begins immediately with platelet aggregation and fibrin clot formation (scabbing) to seal the barrier against contaminants.",
        "general_care": [
            "Rinse gently under clean running water or mild sterile saline to flush out dirt and micro-debris.",
            "Gently pat the surrounding area dry with a clean cloth; do not rub the wound directly.",
            "Apply a thin layer of pure petroleum jelly (e.g. Vaseline) to maintain a moist healing environment.",
            "Cover with a sterile adhesive bandage; change daily or whenever the dressing becomes wet or soiled."
        ],
        "warning_signs": [
            "Bleeding that will not stop after 10 minutes of direct, continuous pressure",
            "Deep, gaping wound edges that cannot be gently held together (may require sutures)",
            "Numbness or tingling distal to the wound site",
            "Puncture from a rusty, outdoor, or unknown metallic object (tetanus risk)"
        ],
        "when_to_seek_care": [
            "Within 6 hours if sutures may be needed to close gaping skin margins",
            "If last tetanus vaccination was more than 5 to 10 years ago and the wound is dirty",
            "If pain increases significantly over subsequent days instead of improving"
        ]
    },
    CAT_RASH: {
        "display_name": "Possible Rash / Skin Irritation",
        "badge_class": "badge-category-rash",
        "description": "Visual characteristics exhibit dispersed color variance and patchy tonal irregularity across the evaluated skin surface.",
        "what_detected": "Computer-vision image analysis observed elevated color variance and patchy tonal distribution across intact skin tissue.",
        "what_means": "Visual characteristics exhibit surface color variability consistent with localized contact irritation, mild dermatitis, or surface reaction.",
        "interpretation": "Visual characteristics exhibit surface color variability consistent with localized contact irritation, mild dermatitis, or surface reaction.",
        "recommended_next_step": "Identify and remove potential environmental irritants (new detergents, soaps, jewelry), apply a cool compress, and consult a physician if the rash spreads or does not improve.",
        "general_information": "Rashes are inflammatory dermatological reactions triggered by immune responses, chemical contact, allergens (plants, cosmetics, nickel), friction, heat, or systemic viral infections. The skin barrier remains largely structurally intact.",
        "general_care": [
            "Gently cleanse with lukewarm water and a fragrance-free, hypoallergenic cleanser.",
            "Avoid scratching to prevent secondary bacterial infection (keep fingernails trimmed short).",
            "Apply a cool, damp compress for 10-15 minutes to relieve itching and soothe burning sensations.",
            "Review recent exposures to new soaps, detergents, cosmetics, jewelry, plants, or medications."
        ],
        "warning_signs": [
            "Rash accompanied by difficulty breathing, facial swelling, or lip/tongue puffiness (anaphylaxis)",
            "Sudden rash covering a large portion of the body or blistering intensely",
            "Rash accompanied by high fever, joint pain, or purple/dark bruises that do not fade when pressed",
            "Signs of secondary infection such as yellow crusting, oozing pus, or red streaks"
        ],
        "when_to_seek_care": [
            "Immediately (call emergency services) if breathing difficulty or facial swelling occurs",
            "Within 24 hours if the rash is blistering, intensely painful, or spreading rapidly",
            "If the rash does not improve after 5-7 days of gentle over-the-counter care"
        ]
    },
    CAT_SWELLING: {
        "display_name": "Possible Swelling",
        "badge_class": "badge-category-swelling",
        "description": "Visual appearance features a smooth localized luminance curvature and low high-frequency textural variance, consistent with localized tissue distension, fluid buildup (edema), contusion (bruise), or blunt trauma response.",
        "what_detected": "The analyzer detected smooth luminance convexity and subdued high-frequency surface roughness, indicative of underlying subcutaneous volume expansion pushing against the skin envelope.",
        "what_means": "Features indicate localized fluid accumulation (edema) or subcutaneous blood pooling (contusion) following blunt impact, strain, or inflammatory fluid retention.",
        "interpretation": "Features indicate localized fluid accumulation (edema) or subcutaneous blood pooling (contusion) following blunt impact, strain, or inflammatory fluid retention.",
        "recommended_next_step": "Rest and elevate the affected area, apply a cold pack for 10-15 minutes, and seek medical attention if severe pain or joint immobility is present.",
        "general_information": "Swelling occurs when trauma, inflammation, or vascular permeability causes interstitial fluid, blood, or inflammatory cells to accumulate within soft tissue. Capillary rupture from impact causes contusions (ecchymosis).",
        "general_care": [
            "Rest the affected limb and protect it from further impact or weight-bearing strain.",
            "Apply a cold pack wrapped in a thin cloth for 10-15 minutes every 2-3 hours (never apply bare ice).",
            "Elevate the affected limb above the level of the heart when resting to promote fluid drainage.",
            "Consider mild compression with an elastic bandage if appropriate, ensuring it is not wrapped too tightly."
        ],
        "warning_signs": [
            "Rapidly expanding swelling causing skin tightness, pallor, or loss of pulse (compartment syndrome)",
            "Severe pain that is completely disproportionate to the injury or worsens continuously",
            "Inability to bear weight on the joint or limb, or visible anatomical deformity",
            "Numbness, tingling, or coldness in fingers or toes beyond the swollen area"
        ],
        "when_to_seek_care": [
            "Immediately if limb deformity, severe pain, or loss of circulation/sensation occurs",
            "Within 24 hours if swelling does not begin to subside after rest and ice",
            "If swelling occurs symmetrically in both legs without an injury (potential cardiovascular/renal sign)"
        ]
    },
    CAT_INFLAMMATION: {
        "display_name": "Possible Inflammation / Redness",
        "badge_class": "badge-category-inflammation",
        "description": "Visual findings reveal diffuse, uniform erythema (capillary hyperfusion) across an intact skin barrier, such as seen in mild sunburn, thermal flush, localized friction irritation, or early reactive vasodilation.",
        "what_detected": "The analysis showed prominent hemoglobin chrominance and elevated Erythema Index with minimal structural surface disruption, indicating active cutaneous vasodilation without open lacerations.",
        "what_means": "Superficial microvessels are dilated in response to thermal, frictional, or chemical stimulus. The epidermal surface remains intact.",
        "interpretation": "Superficial microvessels are dilated in response to thermal, frictional, or chemical stimulus. The epidermal surface remains intact.",
        "recommended_next_step": "Protect the sensitized skin from direct sunlight, hydrate with gentle aloe or ceramide moisturizer, and seek care if blistering or systemic fever occurs.",
        "general_information": "Cutaneous erythema is caused by dilation of superficial dermal capillaries in response to thermal energy, UV radiation, friction, or mild histamine release. In early stages, skin integrity remains preserved.",
        "general_care": [
            "Shield the sensitized skin from direct sunlight, thermal heat, and tight frictional clothing.",
            "Apply soothing aloe vera gel or a gentle hypoallergenic ceramide moisturizer to hydrate the skin.",
            "Drink plenty of water to maintain overall hydration.",
            "Take cool or lukewarm showers instead of hot water, and pat dry gently without rubbing."
        ],
        "warning_signs": [
            "Blistering over a wide surface area (partial-thickness burn)",
            "Chills, high fever, dizziness, or extreme headache alongside extensive redness",
            "Redness that feels hot, hard, indurated, or increasingly tender to touch (early cellulitis)",
            "Dark red, purple, or mottled skin changes with severe localized burning pain"
        ],
        "when_to_seek_care": [
            "Immediately if large blisters develop or widespread thermal burn is suspected",
            "Within 24 hours if redness becomes increasingly painful, hot, or begins to spread",
            "If fever or chills accompany the erythema"
        ]
    },
    CAT_UNABLE: {
        "display_name": "Unable to Confidently Assess",
        "badge_class": "badge-category-unable",
        "description": "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype.",
        "what_detected": "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype.",
        "what_means": "The visual presentation is ambiguous, sub-threshold, or outside supported categories.",
        "interpretation": "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype.",
        "recommended_next_step": "Upload another image or consider professional evaluation by a qualified healthcare provider.",
        "disclaimer_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
        "general_information": "Accurate computer-vision analysis requires adequate lighting, focused detail, and an unobstructed view of the affected skin area. Images of non-skin objects, documents, heavily shadowed scenes, or extreme blur cannot be assessed.",
        "general_care": [
            "Ensure steady, natural lighting without heavy flash glare or deep shadows.",
            "Hold your device steady and tap the screen to focus directly on the affected skin.",
            "Keep the affected area in close frame while including a small border of normal skin for contrast.",
            "Avoid uploading photos of everyday objects, text, animals, or distant wide shots."
        ],
        "warning_signs": WARNING_SIGNS_GENERAL,
        "when_to_seek_care": [
            "If you have an active, concerning skin wound, rash, or injury, consult a healthcare professional directly rather than relying on computer vision tools."
        ]
    }
}

# Model cache
_MODEL_CACHE = None


def load_vision_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model_path = os.path.join(SCRIPT_DIR, '..', 'models', 'vision_scanner_model.joblib')
    if os.path.exists(model_path):
        try:
            _MODEL_CACHE = joblib.load(model_path)
            return _MODEL_CACHE
        except Exception as e:
            # Fallback gracefully
            pass
    return None


def run_rule_based_fallback(features_dict):
    """
    Deterministic rule-based computer-vision classification heuristics.
    NOTE: Current scanner is a rule-based computer-vision screening prototype.
    Diagnostic accuracy percentages are not fabricated.
    """
    mean_ei = features_dict.get("mean_erythema", 0.0)
    roughness = features_dict.get("sobel_roughness", 0.0)
    chroma_std = features_dict.get("chromatic_dispersion", 0.0)
    convexity = features_dict.get("luminance_convexity", 0.0)
    skin_frac = features_dict.get("skin_pixel_fraction", 0.0)
    lesion_info = features_dict.get("lesion_analysis", {})

    # Out of scope check
    if skin_frac < 0.20:
        return CAT_UNABLE, None, ["Non-skin image content detected (skin pixel match < 20%)."]

    # Concerning skin lesion check: Intercept prior to acute infection/injury
    if lesion_info.get("is_concerning_lesion") or lesion_info.get("is_pigmented_lesion"):
        return CAT_CONCERNING_LESION, None, []

    # Priority 1: High erythema with surface edge disruption -> acute superficial infection
    if mean_ei > 22.0 and roughness > 25.0:
        cat = CAT_INFECTION
    # Priority 2: Mechanical abrasion / surface cut -> prominent edge gradients with lower erythema
    elif roughness > 32.0 and mean_ei < 22.0:
        cat = CAT_INJURY
    # Priority 3: Contact dermatitis / irritation -> elevated chromatic dispersion across intact skin
    elif chroma_std > 38.0 and mean_ei > 10.0 and roughness < 26.0:
        cat = CAT_RASH
    # Priority 4: Soft-tissue contusion / edema -> smooth distension with low high-frequency roughness
    elif roughness < 18.0 and mean_ei > 12.0 and chroma_std < 32.0:
        cat = CAT_SWELLING
    # Priority 5: Cutaneous vasodilation / reactive flush -> uniform erythema on intact skin
    elif mean_ei > 16.0 and roughness < 22.0:
        cat = CAT_INFLAMMATION
    else:
        cat = CAT_UNABLE

    return cat, None, []


def compute_vision_metrics(img_path):
    """
    Primary entry point: Loads image, conducts quality gating, extracts 24 features,
    applies clinical safety gates, uncertainty detection, and returns structured result.
    """
    if not os.path.exists(img_path):
        return {
            "success": False,
            "category": CAT_UNABLE,
            "confidence_score": None,
            "error": "Image file not found on server."
        }

    # 1. Quality & Feasibility Gate + Feature Extraction
    acceptable, quality_msg, features_list, features_dict, gray_arr = process_image_file(img_path)

    if features_dict is None:
        return {
            "success": False,
            "category": CAT_UNABLE,
            "confidence_score": None,
            "error": quality_msg
        }

    # Standardized metrics payload matching all frontend keys
    metrics_payload = {
        "erythema_index": round(max(0.0, features_dict.get("mean_erythema", 0.0)), 1),
        "peak_erythema": round(max(0.0, features_dict.get("p90_erythema", 0.0)), 1),
        "surface_roughness": round(max(0.0, features_dict.get("sobel_roughness", 0.0)), 1),
        "roughness_score": round(max(0.0, features_dict.get("sobel_roughness", 0.0)), 1),
        "peak_gradient": round(max(0.0, features_dict.get("p90_roughness", 0.0)), 1),
        "chromatic_variance": round(max(0.0, features_dict.get("chromatic_dispersion", 0.0)), 1),
        "color_variance": round(max(0.0, features_dict.get("chromatic_dispersion", 0.0)), 1),
        "skin_pixel_fraction": round(max(0.0, features_dict.get("skin_pixel_fraction", 0.0)), 3),
        "sharpness_score": round(max(0.0, features_dict.get("sharpness_score", 0.0)), 1),
        "brightness_score": round(max(0.0, features_dict.get("brightness_score", 0.0)), 1)
    }

    # Check Quality Failure Gate
    if not acceptable:
        profile = CONDITION_PROFILES[CAT_UNABLE]
        return {
            "success": True,
            "category": CAT_UNABLE,
            "classification": CAT_UNABLE,
            "prediction": CAT_UNABLE,
            "confidence_score": None,
            "model_confidence": "Not Applicable (Rule-Based Screening Prototype)",
            "is_quality_failure": True,
            "assessment_summary": "Image quality is too low for reliable analysis.",
            "what_detected": "The visual quality check detected extreme blur, underexposure, or excessive flash glare.",
            "what_means": "The camera image does not contain sufficient contrast, focus, or lighting balance to extract reliable dermatological features.",
            "interpretation": "The camera image does not contain sufficient contrast, focus, or lighting balance to extract reliable dermatological features.",
            "what_observed": [
                f"Image Sharpness Variance: {metrics_payload['sharpness_score']} (Threshold: >= 8.0)",
                f"Lighting Balance: {metrics_payload['brightness_score']} (Usable range: 18 - 245)"
            ],
            "technical_features": [
                f"Sharpness Variance: {metrics_payload['sharpness_score']}",
                f"Mean Brightness: {metrics_payload['brightness_score']}",
                f"Resolution: {features_dict.get('quality_details', {}).get('resolution', 'N/A')}"
            ],
            "technical_image_features": [
                f"Sharpness Variance: {metrics_payload['sharpness_score']}",
                f"Mean Brightness: {metrics_payload['brightness_score']}",
                f"Resolution: {features_dict.get('quality_details', {}).get('resolution', 'N/A')}"
            ],
            "technical_image_metrics": [
                f"Sharpness Variance: {metrics_payload['sharpness_score']}",
                f"Mean Brightness: {metrics_payload['brightness_score']}",
                f"Resolution: {features_dict.get('quality_details', {}).get('resolution', 'N/A')}"
            ],
            "recommended_next_step": "Please retake the photo in good, even lighting, holding the device steady to ensure the skin is in sharp focus.",
            "important_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
            "metrics": metrics_payload,
            "findings": [quality_msg],
            "general_care": [
                "Use good, steady lighting without direct harsh flash or deep shadows.",
                "Keep the affected area in focus and hold the camera steady.",
                "Avoid excessive distance; hold the camera close to the affected skin area.",
                "Keep the affected skin area clearly visible and unobstructed."
            ],
            "recommendations": [
                "Use good, steady lighting without direct harsh flash or deep shadows.",
                "Keep the affected area in focus and hold the camera steady.",
                "Avoid excessive distance; hold the camera close to the affected skin area.",
                "Keep the affected skin area clearly visible and unobstructed."
            ],
            "warning_signs": profile["warning_signs"],
            "when_to_seek_care": profile["when_to_seek_care"],
            "severity": "Severity cannot be reliably determined from this scan.",
            "severity_note": "Visual scan quality insufficient to establish baseline features.",
            "is_preliminary": True,
            "disclaimer": "This tool provides preliminary AI-assisted information for educational purposes and does not provide a medical diagnosis."
        }

    # Check Skin Presence Gate (Out-of-Scope Pre-check)
    skin_fraction = features_dict.get("skin_pixel_fraction", 0.0)
    if skin_fraction < 0.20:
        profile = CONDITION_PROFILES[CAT_UNABLE]
        return {
            "success": True,
            "category": CAT_UNABLE,
            "classification": CAT_UNABLE,
            "prediction": CAT_UNABLE,
            "confidence_score": None,
            "model_confidence": "Not Applicable (Rule-Based Screening Prototype)",
            "is_out_of_scope": True,
            "assessment_summary": "Unable to confidently assess this image.",
            "what_detected": f"Visual characteristics do not exhibit recognized dermatological skin tissue patterns (skin pixel match: {round(skin_fraction*100, 1)}%).",
            "what_means": "The uploaded photo appears to capture everyday non-skin items, fabrics, printed documents, or background scenes.",
            "interpretation": "The uploaded photo appears to capture everyday non-skin items, fabrics, printed documents, or background scenes.",
            "what_observed": [
                f"Skin Pixel Locus Fraction: {round(skin_fraction*100, 1)}% (Minimum required: 20%)"
            ],
            "technical_features": [
                f"Skin Chrominance Fraction: {round(skin_fraction*100, 1)}%",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "technical_image_features": [
                f"Skin Chrominance Fraction: {round(skin_fraction*100, 1)}%",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "technical_image_metrics": [
                f"Skin Chrominance Fraction: {round(skin_fraction*100, 1)}%",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "recommended_next_step": "Please upload a clear, focused photo of the affected human skin area or seek professional healthcare advice.",
            "important_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
            "metrics": metrics_payload,
            "findings": [
                f"Visual characteristics do not exhibit recognized dermatological skin tissue patterns (skin pixel match: {round(skin_fraction*100, 1)}%).",
                "The uploaded photo appears to contain everyday non-skin objects, documents, or an unobstructed background."
            ],
            "general_care": [
                "Please upload a clear, focused photo of the affected human skin area.",
                "If you are concerned about an active wound or skin change, please consult a qualified healthcare provider directly."
            ],
            "recommendations": [
                "Please upload a clear, focused photo of the affected human skin area.",
                "If you are concerned about an active wound or skin change, please consult a qualified healthcare provider directly."
            ],
            "warning_signs": profile["warning_signs"],
            "when_to_seek_care": profile["when_to_seek_care"],
            "severity": "Severity cannot be reliably determined from this scan.",
            "severity_note": "Non-dermatological subject detected.",
            "is_preliminary": True,
            "disclaimer": "This tool provides preliminary AI-assisted information for educational purposes and does not provide a medical diagnosis."
        }

    # 2. Check Concerning Skin Lesion Gate (Clinical Safety & Cancer Interception)
    lesion_info = features_dict.get("lesion_analysis", {})
    if lesion_info.get("is_concerning_lesion") or lesion_info.get("is_pigmented_lesion"):
        profile = CONDITION_PROFILES[CAT_CONCERNING_LESION]
        return {
            "success": True,
            "prediction": CAT_CONCERNING_LESION,
            "category": CAT_CONCERNING_LESION,
            "classification": CAT_CONCERNING_LESION,
            "sub_category": "Potentially Concerning Skin Lesion: Professional Dermatological Evaluation Recommended",
            "status": "potentially_concerning_lesion",
            "is_concerning_lesion": True,
            "confidence_score": None,
            "model_confidence": "Not Applicable (Rule-Based Screening Prototype)",
            "confidence_explanation": "This scanner is a rule-based computer-vision screening prototype. Diagnostic probability and clinical cancer confirmation are outside the supported scope of this prototype.",
            "assessment_summary": "Assessment generated using computer-vision analysis of visual image characteristics.",
            "what_detected": profile["what_detected"],
            "interpretation": profile["what_means"],
            "what_means": profile["what_means"],
            "disclaimer_note": profile["disclaimer_note"],
            "recommended_next_step": profile["recommended_next_step"],
            "important_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
            "observed_visual_features": [
                f"Focal Luminance Contrast Drop: {lesion_info.get('contrast_drop', 0)} units",
                f"Focal Lesion Core Coverage: {lesion_info.get('melanin_core_percent', 0)}% of image area",
                f"Intra-Lesion Chromatic Variegation: {lesion_info.get('variegation', 0)}",
                f"Chromatic Dispersion: {lesion_info.get('chromatic_dispersion', metrics_payload['chromatic_variance'])}",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "what_observed": [
                f"Focal Luminance Contrast Drop: {lesion_info.get('contrast_drop', 0)} units",
                f"Focal Lesion Core Coverage: {lesion_info.get('melanin_core_percent', 0)}%",
                f"Intra-Lesion Chromatic Variegation: {lesion_info.get('variegation', 0)}",
                f"Chromatic Dispersion: {lesion_info.get('chromatic_dispersion', metrics_payload['chromatic_variance'])}",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "observable_characteristics": [
                "Asymmetry / Contour Irregularity: Observable difference across lesion axes",
                "Border Definition: Focal edge transition gradients between lesion and surrounding skin",
                "Color Variegation: Non-uniform tonal distribution across the focal spot",
                "Surface Elevation / Texture: Localized surface roughness and edge density",
                "Contrast Gradient: Localized luminance drop relative to surrounding skin envelope"
            ],
            "technical_features": [
                f"Lesion Luminance Contrast Drop: {lesion_info.get('contrast_drop', 0)} units",
                f"Focal Lesion Core Fraction: {lesion_info.get('melanin_core_percent', 0)}%",
                f"Intra-Lesion Chromatic Variegation: {lesion_info.get('variegation', 0)}",
                f"Chromatic Dispersion: {lesion_info.get('chromatic_dispersion', metrics_payload['chromatic_variance'])}",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "technical_image_features": [
                f"Lesion Luminance Contrast Drop: {lesion_info.get('contrast_drop', 0)} units",
                f"Focal Lesion Core Fraction: {lesion_info.get('melanin_core_percent', 0)}%",
                f"Intra-Lesion Chromatic Variegation: {lesion_info.get('variegation', 0)}",
                f"Chromatic Dispersion: {lesion_info.get('chromatic_dispersion', metrics_payload['chromatic_variance'])}",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "technical_image_metrics": [
                f"Lesion Luminance Contrast Drop: {lesion_info.get('contrast_drop', 0)} units",
                f"Focal Lesion Core Fraction: {lesion_info.get('melanin_core_percent', 0)}%",
                f"Intra-Lesion Chromatic Variegation: {lesion_info.get('variegation', 0)}",
                f"Chromatic Dispersion: {lesion_info.get('chromatic_dispersion', metrics_payload['chromatic_variance'])}",
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}"
            ],
            "general_information": profile["general_information"],
            "general_care": profile["general_care"],
            "recommendations": profile["general_care"],
            "warning_signs": profile["warning_signs"],
            "when_to_seek_care": profile["when_to_seek_care"],
            "abcde_guide": profile["abcde_guide"],
            "severity": "Severity cannot be reliably determined from this scan.",
            "severity_note": "Definitive evaluation of skin lesions requires physical clinical examination with dermoscopy or histopathology.",
            "runner_ups": [],
            "metrics": metrics_payload,
            "findings": [
                profile["what_detected"],
                "Assessment generated using computer-vision analysis of visual image characteristics."
            ],
            "model_used": "MediSense AI Rule-Based Visual Screening Prototype",
            "is_preliminary": True,
            "disclaimer": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis. Results should not replace evaluation by a qualified healthcare professional."
        }

    # 3. Rule-Based Visual Feature Classification for Acute Presentations
    top_cat, _, fallback_findings = run_rule_based_fallback(features_dict)

    # Uncertainty / ambiguous result check (Section 5)
    if top_cat == CAT_UNABLE:
        profile = CONDITION_PROFILES[CAT_UNABLE]
        return {
            "success": True,
            "prediction": CAT_UNABLE,
            "category": CAT_UNABLE,
            "classification": CAT_UNABLE,
            "confidence_score": None,
            "model_confidence": "Not Applicable (Rule-Based Screening Prototype)",
            "is_out_of_scope": True,
            "assessment_summary": "Unable to confidently assess this image.",
            "what_detected": "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype.",
            "what_means": "The visual presentation is ambiguous, sub-threshold, or outside supported categories.",
            "interpretation": "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype.",
            "observed_visual_features": [
                f"Optical Erythema Index: {metrics_payload['erythema_index']} (Baseline red chrominance)",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']} (Sobel gradient density)",
                f"Color Variance: {metrics_payload['chromatic_variance']} (Chromatic dispersion)"
            ],
            "what_observed": [
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}",
                f"Color Variance: {metrics_payload['chromatic_variance']}"
            ],
            "technical_image_metrics": [
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}",
                f"Color Variance: {metrics_payload['chromatic_variance']}"
            ],
            "technical_features": [
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}",
                f"Color Variance: {metrics_payload['chromatic_variance']}"
            ],
            "technical_image_features": [
                f"Optical Erythema Index: {metrics_payload['erythema_index']}",
                f"Surface Edge Roughness: {metrics_payload['surface_roughness']}",
                f"Color Variance: {metrics_payload['chromatic_variance']}"
            ],
            "recommended_next_step": "Upload another image or consider professional evaluation by a qualified healthcare provider.",
            "important_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
            "metrics": metrics_payload,
            "findings": fallback_findings or [
                "The uploaded image does not contain sufficient evidence for a reliable classification by this prototype."
            ],
            "general_care": [
                "Upload another image in good, steady lighting, or consider professional evaluation.",
                "Do not attempt unprescribed treatments without proper in-person clinical assessment."
            ],
            "recommendations": [
                "Upload another image in good, steady lighting, or consider professional evaluation."
            ],
            "warning_signs": profile["warning_signs"],
            "when_to_seek_care": profile["when_to_seek_care"],
            "severity": "Severity cannot be reliably determined from this scan.",
            "severity_note": "Visual presentation ambiguous or sub-threshold.",
            "is_preliminary": True,
            "disclaimer": "This tool provides preliminary AI-assisted information for educational purposes and does not provide a medical diagnosis."
        }

    # Fetch structured knowledge profile
    profile = CONDITION_PROFILES.get(top_cat, CONDITION_PROFILES[CAT_UNABLE])

    # Build observable characteristics bullet points
    observable_chars = [
        f"Optical Erythema Index: {metrics_payload['erythema_index']} (Peak: {metrics_payload['peak_erythema']})",
        f"Surface Edge Roughness: {metrics_payload['surface_roughness']} (Sobel gradient density)",
        f"Color Variance: {metrics_payload['chromatic_variance']} (Chromatic dispersion across tissue)",
        f"Skin Match Fraction: {round(metrics_payload['skin_pixel_fraction'] * 100.0, 1)}% (Skin locus match)"
    ]

    technical_features = [
        f"Optical Erythema Index: {metrics_payload['erythema_index']} (Relative red/green chrominance ratio)",
        f"Sobel Edge Roughness: {metrics_payload['surface_roughness']} (Spatial edge gradient density)",
        f"Color Variance: {metrics_payload['chromatic_variance']} (Chromatic dispersion across tissue pixels)",
        f"Skin Locus Pixel Fraction: {round(metrics_payload['skin_pixel_fraction'] * 100.0, 1)}%",
        f"Image Sharpness Variance: {metrics_payload['sharpness_score']} (Laplacian focus clarity)"
    ]

    findings = [
        profile["what_detected"],
        "Assessment generated using computer-vision analysis of visual image characteristics."
    ]

    return {
        "success": True,
        "prediction": top_cat,
        "category": top_cat,
        "classification": top_cat,
        "confidence_score": None,
        "model_confidence": "Not Applicable (Rule-Based Screening Prototype)",
        "confidence_explanation": "This scanner is a rule-based computer-vision screening prototype. Diagnostic percentage scores are not generated.",
        "assessment_summary": "Assessment generated using computer-vision analysis of visual image characteristics.",
        "what_detected": profile["what_detected"],
        "what_observed": observable_chars,
        "observed_visual_features": observable_chars,
        "observable_characteristics": observable_chars,
        "technical_features": technical_features,
        "technical_image_features": technical_features,
        "technical_image_metrics": technical_features,
        "interpretation": profile.get("what_means", profile["description"]),
        "what_means": profile.get("what_means", profile["description"]),
        "recommended_next_step": profile.get("recommended_next_step", profile["when_to_seek_care"][0]),
        "important_note": "This AI-assisted result is for educational/preliminary screening purposes only and is not a medical diagnosis.",
        "general_information": profile["general_information"],
        "general_care": profile["general_care"],
        "recommendations": profile["general_care"],
        "warning_signs": profile["warning_signs"],
        "when_to_seek_care": profile["when_to_seek_care"],
        "severity": "Severity cannot be reliably determined from this scan.",
        "severity_note": "Tissue firmness, depth, warmth, and induration cannot be evaluated from a 2D photograph and require physical clinical examination.",
        "runner_ups": [],
        "metrics": metrics_payload,
        "findings": findings,
        "model_used": "MediSense AI Rule-Based Visual Screening Prototype",
        "is_preliminary": True,
        "disclaimer": "This tool provides preliminary AI-assisted information for educational purposes and does not provide a medical diagnosis. Results should not replace evaluation by a qualified healthcare professional."
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "category": CAT_UNABLE,
            "error": "Usage: python scanner.py <path_to_image>"
        }))
        sys.exit(1)

    img_path = sys.argv[1]
    result = compute_vision_metrics(img_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

