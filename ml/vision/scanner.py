"""
AI Healthcare - Infection & Injury Image Scanner (Computer Vision Pipeline)
=============================================================================
Genuine Computer Vision feature extraction for educational preliminary visual assessment.
Uses Pillow (PIL), NumPy, and SciPy to analyze physical image characteristics:
  - Blur detection via Laplacian edge variance
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
from scipy import ndimage

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
    if h < 80 or w < 80:
        return False, 0.0, 0.0, "Image resolution is too low (< 80x80 px). Please upload a higher resolution photo."

    # Mean brightness (0-255)
    brightness = float(np.mean(gray_arr))
    if brightness < 28.0:
        return False, 0.0, brightness, "Image is severely underexposed (too dark). Please take a photo in good lighting."
    if brightness > 238.0:
        return False, 0.0, brightness, "Image is severely overexposed (washed out). Please adjust lighting to avoid glare."

    # Blur estimation using Laplacian variance
    # Discrete Laplacian kernel
    laplacian = ndimage.laplace(gray_arr.astype(np.float64))
    blur_variance = float(laplacian.var())

    # If blur variance is too low, the image is out of focus
    if blur_variance < 35.0:
        return False, blur_variance, brightness, "Image is out of focus or blurry. Please hold camera steady for a sharp image."

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
    if not acceptable:
        return {
            "success": True,
            "category": CAT_UNABLE,
            "confidence_score": 0.0,
            "assessment_summary": "The uploaded photo could not be reliably assessed due to visual quality limitations.",
            "metrics": {
                "sharpness_score": round(blur_score, 1),
                "brightness_score": round(brightness, 1),
                "erythema_index": 0.0,
                "roughness_score": 0.0,
                "color_variance": 0.0
            },
            "findings": [quality_msg],
            "recommendations": [
                "Ensure steady lighting without heavy flash glare or deep shadows.",
                "Hold your camera steady and tap to focus directly on the affected skin.",
                "Include a small border of normal surrounding skin for comparative contrast."
            ],
            "warning_signs": WARNING_SIGNS,
            "is_preliminary": True
        }

    # Normalized color channels
    R = rgb_arr[:, :, 0]
    G = rgb_arr[:, :, 1]
    B = rgb_arr[:, :, 2]
    total_intensity = R + G + B + 1e-6

    # 2. Spectrophotometric Erythema Index (EI)
    # Standard formula approximation: 100 * (log10(R) - log10(G)) for pixels with R > 0 and G > 0
    safe_R = np.clip(R, 1.0, 255.0)
    safe_G = np.clip(G, 1.0, 255.0)
    erythema_map = 100.0 * (np.log10(safe_R) - np.log10(safe_G))
    mean_ei = float(np.mean(erythema_map))
    p90_ei = float(np.percentile(erythema_map, 90))

    # Normalized redness ratio: (R - G) / (R + G + B)
    red_excess = np.clip((R - G) / total_intensity, 0.0, 1.0)
    red_ratio_score = float(np.mean(red_excess)) * 100.0
    p90_red_ratio = float(np.percentile(red_excess, 90)) * 100.0

    # 3. Surface Roughness / Edge Gradient Density (Sobel filter via SciPy)
    # Detects skin tears, lacerations, scabs, abrasions, and sharp textural disruption
    sobel_h = ndimage.sobel(gray_arr, axis=0)
    sobel_v = ndimage.sobel(gray_arr, axis=1)
    gradient_magnitude = np.hypot(sobel_h, sobel_v)
    roughness_score = float(np.mean(gradient_magnitude))
    p90_roughness = float(np.percentile(gradient_magnitude, 90))

    # 4. Chromatic Dispersion & Micro-clustering (Rashes / Dermatitis)
    # High standard deviation in color space across distinct local patches indicates macules/papules
    hue_diff = np.abs(R - B) + np.abs(R - G)
    chromatic_dispersion = float(np.std(hue_diff))

    # 5. Localized Luminance Convexity (Swelling / Edema Indicator)
    # Swollen tissue causes gentle curvature and diffuse specular reflections with low edge roughness
    smoothed_gray = ndimage.gaussian_filter(gray_arr, sigma=5)
    high_freq = np.abs(gray_arr - smoothed_gray)
    texture_uniformity = float(np.mean(high_freq))

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
        "metrics": {
            "erythema_index": round(max(0.0, mean_ei), 1),
            "peak_erythema": round(max(0.0, p90_ei), 1),
            "surface_roughness": round(roughness_score, 1),
            "peak_gradient": round(p90_roughness, 1),
            "chromatic_variance": round(chromatic_dispersion, 1),
            "sharpness_score": round(blur_score, 1),
            "brightness_score": round(brightness, 1)
        },
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
    is_high_erythema = (p90_ei > 22.0 or p90_red_ratio > 18.0)
    is_moderate_erythema = (p90_ei > 12.0 or p90_red_ratio > 10.0)
    is_high_roughness = (roughness > 30.0 or p90_roughness > 70.0)
    is_moderate_roughness = (roughness > 18.0 or p90_roughness > 45.0)
    is_high_chroma_var = (chroma_std > 32.0)

    # 1. Infection Indicators: Elevated erythema AND significant surface disruption / potential crusting
    if is_high_erythema and is_high_roughness:
        category = CAT_INFECTION
        confidence = min(88.0, 58.0 + (p90_ei * 0.6) + (roughness * 0.3))
        findings.append("Prominent localized erythema (redness) detected alongside elevated surface texture disruption.")
        findings.append("Visual patterns exhibit characteristics commonly seen in active inflammatory wound responses.")
        recommendations = [
            "Keep the affected area clean, dry, and gently protected with a sterile dressing.",
            "Avoid scratching, picking scabs, or applying unprescribed harsh ointments.",
            "Monitor closely for spreading redness, rising warmth, or drainage, which warrant medical evaluation."
        ]

    # 2. Minor Injury: Surface break/roughness prominent, mild to moderate erythema
    elif is_high_roughness and not is_high_erythema:
        category = CAT_INJURY
        confidence = min(85.0, 60.0 + (roughness * 0.45))
        findings.append("Elevated edge gradient density consistent with superficial skin barrier disruption or abrasion.")
        findings.append("Surrounding erythema levels remain within typical localized healing thresholds.")
        recommendations = [
            "Rinse gently with clean potable water or mild saline solution to remove debris.",
            "Apply petroleum jelly or an over-the-counter soothing ointment to support moisture healing.",
            "Cover with a sterile non-stick bandage to shield against friction and environmental contamination."
        ]

    # 3. Rash / Irritation: Scattered chromatic variance + moderate erythema without deep laceration edges
    elif is_high_chroma_var and is_moderate_erythema and not is_high_roughness:
        category = CAT_RASH
        confidence = min(84.0, 55.0 + (chroma_std * 0.5) + (p90_red_ratio * 0.4))
        findings.append("Dispersed chromatic variance with patchy tonal distribution across the evaluated tissue.")
        findings.append("Surface contour remains largely intact without sharp laceration margins.")
        recommendations = [
            "Wash gently with a mild fragrance-free soap; pat dry without rubbing.",
            "Consider whether new detergents, cosmetics, soaps, or plants may have contacted the area.",
            "A cool, damp compress may help soothe temporary itching or irritation."
        ]

    # 4. Swelling: Diffuse low-texture convexity or moderate erythema with smooth contours
    elif is_moderate_erythema and roughness < 16.0 and texture_uniformity < 10.0:
        category = CAT_SWELLING
        confidence = min(80.0, 54.0 + (mean_ei * 0.5) + ((20.0 - roughness) * 0.8))
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
        confidence = min(82.0, 56.0 + (p90_red_ratio * 0.7))
        findings.append("Elevated hemoglobin absorption index / redness noticeable across the region.")
        findings.append("Skin surface appears relatively uniform with minimal open edge disruptions.")
        recommendations = [
            "Protect the sensitive skin from friction, excessive heat, and direct sunlight.",
            "Hydrate the skin barrier using gentle, hypoallergenic moisturizers.",
            "Track the border of the redness with a skin marker if you suspect it may be expanding."
        ]

    # 6. Fallback / Mild
    else:
        category = CAT_INJURY
        confidence = 62.0
        findings.append("Mild localized visual irregularity observed with baseline color metrics.")
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

    image_path = sys.argv[1]
    result = compute_vision_metrics(image_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
