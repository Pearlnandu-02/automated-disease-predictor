"""
AI Healthcare - Infection & Injury Image Scanner (Computer Vision Pipeline)
=============================================================================
Genuine Computer Vision feature extraction for educational preliminary visual assessment.
Uses pure Pillow (PIL) and NumPy to analyze physical image characteristics:
  - Blur detection via discrete Laplacian edge variance
  - Exposure & lighting feasibility check
  - Dermatological Erythema Index (EI = 100 * [log10(R) - log10(G)])
  - Surface gradient roughness (Sobel filter for cuts, abrasions, scabbing)
  - Chromatic dispersion & micro-cluster variance (rashes, irritation)
  - Swelling contour luminance distribution

DISCLAIMER: This system provides an educational preliminary visual assessment
and does NOT constitute a medical diagnosis.
"""

import sys
import os
import json
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter

# Educational assessment categories
CAT_INFECTION = "Possible Infection Indicators"
CAT_INFLAMMATION = "Possible Inflammation/Redness"
CAT_INJURY = "Possible Minor Injury"
CAT_RASH = "Possible Rash/Skin Irritation"
CAT_SWELLING = "Possible Swelling"
CAT_UNABLE = "Unable to Assess"

WARNING_SIGNS = [
    "Severe, pulsating, or worsening pain",
    "Rapidly spreading redness or red streaks radiating from the wound",
    "Thick, foul-smelling yellow or green pus/discharge",
    "Fever, chills, nausea, or general feeling of illness",
    "Wound that won't stop bleeding after 10 minutes of direct pressure",
    "Deep gaping lacerations, exposed fat, muscle, or bone",
    "Loss of sensation, numbness, or inability to move the affected limb",
    "Animal or human bite wounds (high infection risk)",
    "Significant swelling that impairs circulation or breathing"
]


def assess_image_quality(gray_arr):
    """
    Evaluates image sharpness, focus, and illumination.
    Returns (is_acceptable: bool, blur_score: float, brightness: float, reason: str)
    """
    h, w = gray_arr.shape
    if h < 40 or w < 40:
        return False, 0.0, 0.0, "Image resolution is too low (< 40x40 px). Please upload a higher resolution photo."

    # Mean brightness (0-255)
    brightness = float(np.mean(gray_arr))
    if brightness < 12.0:
        return False, 0.0, brightness, "Image is severely underexposed (too dark). Please take a photo in good lighting."
    if brightness > 248.0:
        return False, 0.0, brightness, "Image is severely overexposed (washed out). Please adjust lighting to avoid glare."

    # Discrete Laplacian kernel [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    padded = np.pad(gray_arr, 1, mode='edge')
    laplacian = (
        padded[:-2, 1:-1] +
        padded[2:, 1:-1] +
        padded[1:-1, :-2] +
        padded[1:-1, 2:] -
        4.0 * padded[1:-1, 1:-1]
    )
    blur_variance = float(np.var(laplacian))

    # Only reject if virtually zero detail (pure blur or featureless solid)
    if blur_variance < 4.0:
        return False, blur_variance, brightness, "Image appears out of focus or blurry. Please hold camera steady for a sharp image."

    return True, blur_variance, brightness, "Quality check passed"


def compute_vision_metrics(img_path):
    """
    Loads an image file, conducts quality gating, and computes dermatological
    and textural computer vision metrics.
    """
    if not os.path.exists(img_path):
        return {
            "success": False,
            "category": CAT_UNABLE,
            "error": "Image file not found on server."
        }

    try:
        # Open with PIL and convert to RGB
        with Image.open(img_path) as pil_img:
            # Handle EXIF orientation if needed
            pil_img = ImageOps.exif_transpose(pil_img)
            # Resize image to reasonable working resolution for consistent metrics
            max_dim = 600
            pil_img.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)
            rgb_img = pil_img.convert("RGB")
            rgb_arr = np.array(rgb_img, dtype=np.float64)

    except Exception as e:
        return {
            "success": False,
            "category": CAT_UNABLE,
            "error": f"Invalid or corrupt image format: {str(e)}"
        }

    # Extract Grayscale representation
    gray_img = ImageOps.grayscale(rgb_img)
    gray_arr = np.array(gray_img, dtype=np.float64)

    # 1. Quality & Feasibility Gate
    acceptable, blur_score, brightness, quality_msg = assess_image_quality(gray_arr)

    # Normalized color channels
    R = rgb_arr[:, :, 0]
    G = rgb_arr[:, :, 1]
    B = rgb_arr[:, :, 2]
    total_intensity = R + G + B + 1e-6

    # 2. Spectrophotometric Erythema Index (EI)
    # Standard formula: 100 * (log10(R) - log10(G)) for pixels with R > 0 and G > 0
    safe_R = np.clip(R, 1.0, 255.0)
    safe_G = np.clip(G, 1.0, 255.0)
    erythema_map = 100.0 * (np.log10(safe_R) - np.log10(safe_G))
    mean_ei = float(np.mean(erythema_map))
    p90_ei = float(np.percentile(erythema_map, 90))

    # Normalized redness ratio: (R - G) / (R + G + B)
    red_excess = np.clip((R - G) / total_intensity, 0.0, 1.0)
    red_ratio_score = float(np.mean(red_excess)) * 100.0
    p90_red_ratio = float(np.percentile(red_excess, 90)) * 100.0

    # 3. Surface Roughness / Edge Gradient Density (3x3 Sobel filter via pure NumPy)
    pad = np.pad(gray_arr, 1, mode='edge')
    sobel_h = (
        -1.0 * pad[:-2, :-2] + 1.0 * pad[:-2, 2:] +
        -2.0 * pad[1:-1, :-2] + 2.0 * pad[1:-1, 2:] +
        -1.0 * pad[2:, :-2] + 1.0 * pad[2:, 2:]
    )
    sobel_v = (
        -1.0 * pad[:-2, :-2] - 2.0 * pad[:-2, 1:-1] - 1.0 * pad[:-2, 2:] +
        1.0 * pad[2:, :-2] + 2.0 * pad[2:, 1:-1] + 1.0 * pad[2:, 2:]
    )
    gradient_magnitude = np.hypot(sobel_h, sobel_v)
    roughness_score = float(np.mean(gradient_magnitude))
    p90_roughness = float(np.percentile(gradient_magnitude, 90))

    # 4. Chromatic Dispersion & Micro-clustering (Rashes / Dermatitis)
    hue_diff = np.abs(R - B) + np.abs(R - G)
    chromatic_dispersion = float(np.std(hue_diff))

    # 5. Localized Luminance Convexity (Swelling / Edema Indicator)
    # Swollen tissue causes smooth curvature with low high-frequency textural variance
    smoothed_gray = np.array(gray_img.filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float64)
    high_freq = np.abs(gray_arr - smoothed_gray)
    texture_uniformity = float(np.mean(high_freq))

    # Standardized metrics payload supporting all frontend key conventions
    metrics_dict = {
        "erythema_index": round(max(0.0, mean_ei), 1),
        "peak_erythema": round(max(0.0, p90_ei), 1),
        "surface_roughness": round(max(0.0, roughness_score), 1),
        "roughness_score": round(max(0.0, roughness_score), 1),
        "peak_gradient": round(max(0.0, p90_roughness), 1),
        "chromatic_variance": round(max(0.0, chromatic_dispersion), 1),
        "color_variance": round(max(0.0, chromatic_dispersion), 1),
        "sharpness_score": round(max(0.0, blur_score), 1),
        "brightness_score": round(max(0.0, brightness), 1)
    }

    if not acceptable:
        return {
            "success": True,
            "category": CAT_UNABLE,
            "confidence_score": 0.0,
            "assessment_summary": "The uploaded photo could not be reliably assessed due to visual quality limitations.",
            "metrics": metrics_dict,
            "findings": [quality_msg],
            "recommendations": [
                "Ensure steady lighting without heavy flash glare or deep shadows.",
                "Hold your camera steady and tap to focus directly on the affected skin.",
                "Include a small border of normal surrounding skin for comparative contrast."
            ],
            "warning_signs": WARNING_SIGNS,
            "is_preliminary": True
        }

    # Determine educational assessment category and confidence score
    category, confidence, findings, recommendations = classify_visual_patterns(
        mean_ei=mean_ei,
        p90_ei=p90_ei,
        red_ratio=red_ratio_score,
        p90_red_ratio=p90_red_ratio,
        roughness=roughness_score,
        p90_roughness=p90_roughness,
        chroma_std=chromatic_dispersion,
        texture_uniformity=texture_uniformity
    )

    return {
        "success": True,
        "category": category,
        "confidence_score": round(confidence, 1),
        "assessment_summary": f"Visual indicators may be consistent with {category.lower()}.",
        "metrics": metrics_dict,
        "findings": findings,
        "recommendations": recommendations,
        "warning_signs": WARNING_SIGNS,
        "is_preliminary": True
    }


def classify_visual_patterns(mean_ei, p90_ei, red_ratio, p90_red_ratio,
                             roughness, p90_roughness, chroma_std, texture_uniformity):
    """
    Deterministic rule-based medical computer-vision pattern analysis.
    Classifies visual characteristics into educational observation categories.
    """
    findings = []
    recommendations = []

    # Indicators
    is_high_erythema = (p90_ei > 16.0 or p90_red_ratio > 14.0 or mean_ei > 8.0)
    is_moderate_erythema = (p90_ei > 8.0 or p90_red_ratio > 7.0 or mean_ei > 3.0)
    is_high_roughness = (roughness > 24.0 or p90_roughness > 55.0)
    is_moderate_roughness = (roughness > 14.0 or p90_roughness > 35.0)
    is_high_chroma_var = (chroma_std > 25.0)

    # 1. Infection Indicators: Elevated erythema AND significant surface disruption / potential crusting
    if is_high_erythema and is_high_roughness:
        category = CAT_INFECTION
        confidence = min(89.0, 58.0 + (p90_ei * 0.5) + (roughness * 0.25))
        findings.append(f"Prominent localized erythema (Erythema Index: {round(mean_ei, 1)}) detected alongside elevated surface texture disruption (Roughness: {round(roughness, 1)}).")
        findings.append("Visual patterns exhibit characteristics commonly seen in active inflammatory wound responses.")
        recommendations = [
            "Keep the affected area clean, dry, and gently protected with a sterile dressing.",
            "Avoid scratching, picking scabs, or applying unprescribed harsh ointments.",
            "Monitor closely for spreading redness, rising warmth, or drainage, which warrant immediate medical evaluation."
        ]

    # 2. Minor Injury: Surface break/roughness prominent, mild to moderate erythema
    elif is_high_roughness and not is_high_erythema:
        category = CAT_INJURY
        confidence = min(85.0, 60.0 + (roughness * 0.35))
        findings.append(f"Elevated edge gradient density (Roughness: {round(roughness, 1)}) consistent with superficial skin barrier disruption or abrasion.")
        findings.append("Surrounding erythema levels remain within typical localized healing thresholds.")
        recommendations = [
            "Rinse gently with clean potable water or mild saline solution to remove debris.",
            "Apply petroleum jelly or an over-the-counter soothing ointment to support moisture healing.",
            "Cover with a sterile non-stick bandage to shield against friction and environmental contamination."
        ]

    # 3. Rash / Irritation: Scattered chromatic variance + moderate erythema without deep laceration edges
    elif is_high_chroma_var and is_moderate_erythema and not is_high_roughness:
        category = CAT_RASH
        confidence = min(84.0, 55.0 + (chroma_std * 0.4) + (p90_red_ratio * 0.35))
        findings.append(f"Dispersed chromatic variance (Variance: {round(chroma_std, 1)}) with patchy tonal distribution across evaluated skin.")
        findings.append("Surface contour remains largely intact without sharp laceration margins.")
        recommendations = [
            "Wash gently with a mild fragrance-free cleanser; pat dry without rubbing.",
            "Consider whether new detergents, cosmetics, soaps, or plants may have contacted the area.",
            "A cool, damp compress may help soothe temporary itching or irritation."
        ]

    # 4. Swelling: Diffuse low-texture convexity or moderate erythema with smooth contours
    elif is_moderate_erythema and roughness < 15.0 and texture_uniformity < 12.0:
        category = CAT_SWELLING
        confidence = min(82.0, 54.0 + (mean_ei * 0.5) + ((18.0 - roughness) * 0.8))
        findings.append("Smooth localized luminance profile with low high-frequency textural variance.")
        findings.append("Visual appearance may reflect localized fluid buildup, contusion, or tissue puffiness.")
        recommendations = [
            "Elevate the affected limb or area above heart level where practical to encourage drainage.",
            "Apply a cold pack wrapped in a soft towel for 10-15 minutes at a time (avoid direct ice contact).",
            "Rest the injured area and refrain from strenuous pressure or impact."
        ]

    # 5. Inflammation / Redness: Erythema dominant without structural cuts
    elif is_moderate_erythema or is_high_erythema:
        category = CAT_INFLAMMATION
        confidence = min(83.0, 56.0 + (p90_red_ratio * 0.6))
        findings.append(f"Elevated hemoglobin absorption index (Erythema Index: {round(mean_ei, 1)}) noticeable across the tissue.")
        findings.append("Skin surface appears relatively uniform with minimal open edge disruptions.")
        recommendations = [
            "Protect the sensitive skin from friction, excessive heat, and direct sunlight.",
            "Hydrate the skin barrier using gentle, hypoallergenic moisturizers.",
            "Track the border of the redness with a skin marker if you suspect it may be expanding."
        ]

    # 6. Baseline / Minor Irregularity
    else:
        category = CAT_INJURY
        confidence = min(72.0, 50.0 + roughness * 0.4)
        findings.append(f"Mild localized visual irregularity observed (Roughness: {round(roughness, 1)}, Erythema: {round(mean_ei, 1)}).")
        recommendations = [
            "Maintain basic wound hygiene and monitor for any changes in color, sensation, or swelling.",
            "Consult a healthcare professional if discomfort persists or worsens."
        ]

    return category, confidence, findings, recommendations


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
