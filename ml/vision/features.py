"""
MediSense AI - Computer Vision Feature Extraction Engine
=============================================================================
Computes dermatological, spectrophotometric, and textural image features:
  - Exposure, focus, and illumination quality gating
  - Human skin chrominance locus detection (Fitzpatrick I-VI skin tone invariant)
  - Spectrophotometric Erythema Index (EI = 100 * [log10(R) - log10(G)])
  - Hemoglobin & melanin proxy chrominance (YCbCr Cr & Cb channels, HSV color space)
  - Surface gradient roughness (Sobel horizontal & vertical filter)
  - Micro-cluster chromatic dispersion (rashes, irritation patchiness)
  - Localized luminance convexity (swelling / tissue distension)
  - Edge density & local texture homogeneity
"""

import os
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter

FEATURE_NAMES = [
    "mean_erythema",
    "p90_erythema",
    "red_excess_ratio",
    "p90_red_excess",
    "rg_ratio",
    "rb_ratio",
    "mean_hue",
    "std_hue",
    "mean_saturation",
    "std_saturation",
    "mean_value",
    "std_value",
    "ycbcr_cr_mean",
    "ycbcr_cr_std",
    "skin_pixel_fraction",
    "sobel_roughness",
    "p90_roughness",
    "sobel_direction_entropy",
    "laplacian_sharpness",
    "chromatic_dispersion",
    "luminance_convexity",
    "texture_contrast",
    "texture_homogeneity",
    "edge_density"
]


def assess_image_quality(gray_arr, rgb_arr):
    """
    Evaluates image sharpness, focus, illumination, and usable content.
    Returns:
        is_acceptable: bool
        blur_score: float
        brightness: float
        reason: str
        quality_details: dict
    """
    h, w = gray_arr.shape
    if h < 60 or w < 60:
        return False, 0.0, 0.0, "Image resolution is too low (< 60x60 px). Please upload a higher resolution photo.", {
            "resolution": f"{w}x{h}",
            "sharpness": 0.0,
            "brightness": 0.0
        }

    # Mean brightness (0-255 scale)
    brightness = float(np.mean(gray_arr))
    if brightness < 18.0:
        return False, 0.0, brightness, "Image is severely underexposed (too dark). Please take a photo in good, even lighting.", {
            "resolution": f"{w}x{h}",
            "sharpness": 0.0,
            "brightness": round(brightness, 1)
        }
    if brightness > 245.0:
        return False, 0.0, brightness, "Image is severely overexposed (washed out). Please adjust lighting to avoid excessive glare.", {
            "resolution": f"{w}x{h}",
            "sharpness": 0.0,
            "brightness": round(brightness, 1)
        }

    # Glare / saturation ratio check
    saturated_pixels = np.sum(gray_arr > 250) / float(h * w)
    if saturated_pixels > 0.40:
        return False, 0.0, brightness, "Severe flash glare detected across >40% of the image. Please retake without direct harsh flash.", {
            "resolution": f"{w}x{h}",
            "sharpness": 0.0,
            "brightness": round(brightness, 1),
            "glare_fraction": round(saturated_pixels, 3)
        }

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

    # Reject if virtually zero textural detail (pure blur or solid color)
    if blur_variance < 8.0:
        return False, blur_variance, brightness, "Image appears out of focus or blurry. Please hold camera steady for a sharp image.", {
            "resolution": f"{w}x{h}",
            "sharpness": round(blur_variance, 1),
            "brightness": round(brightness, 1)
        }

    return True, blur_variance, brightness, "Quality check passed", {
        "resolution": f"{w}x{h}",
        "sharpness": round(blur_variance, 1),
        "brightness": round(brightness, 1)
    }


def detect_skin_pixels(rgb_arr):
    """
    Identifies skin pixels across diverse skin tones (Fitzpatrick types I-VI)
    using standard dermatological color-space boundaries:
      RGB condition: R > 40, G > 25, B > 15, max(R,G,B)-min(R,G,B) > 12, R > G, R > B
      YCbCr condition: 133 <= Cr <= 173 and 77 <= Cb <= 127 (broad spectrum)
    Returns:
        skin_mask: boolean 2D numpy array
        skin_fraction: float (0.0 to 1.0)
    """
    R = rgb_arr[:, :, 0]
    G = rgb_arr[:, :, 1]
    B = rgb_arr[:, :, 2]

    # RGB skin rules
    rgb_rule = (
        (R > 40) & (G > 25) & (B > 15) &
        (np.maximum(np.maximum(R, G), B) - np.minimum(np.minimum(R, G), B) > 12) &
        (R > G) & (R > B)
    )

    # YCbCr conversion
    # Y  =  0.299*R + 0.587*G + 0.114*B
    # Cb = -0.169*R - 0.331*G + 0.500*B + 128
    # Cr =  0.500*R - 0.419*G - 0.081*B + 128
    Cb = -0.168736 * R - 0.331264 * G + 0.5 * B + 128.0
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128.0

    ycbcr_rule = (Cr >= 130) & (Cr <= 180) & (Cb >= 75) & (Cb <= 135)

    skin_mask = rgb_rule | ycbcr_rule
    fraction = float(np.mean(skin_mask))
    return skin_mask, fraction


def extract_features_from_array(rgb_arr):
    """
    Extracts 24-dimensional feature vector from an RGB float numpy array.
    """
    h, w, _ = rgb_arr.shape
    total_pixels = float(h * w)

    R = rgb_arr[:, :, 0]
    G = rgb_arr[:, :, 1]
    B = rgb_arr[:, :, 2]
    total_intensity = R + G + B + 1e-6

    # 1. Spectrophotometric Erythema Index (EI = 100 * [log10(R) - log10(G)])
    safe_R = np.clip(R, 1.0, 255.0)
    safe_G = np.clip(G, 1.0, 255.0)
    erythema_map = 100.0 * (np.log10(safe_R) - np.log10(safe_G))
    mean_ei = float(np.mean(erythema_map))
    p90_ei = float(np.percentile(erythema_map, 90))

    # Red excess ratio: (R - G) / (R + G + B)
    red_excess = np.clip((R - G) / total_intensity, -1.0, 1.0)
    mean_red_excess = float(np.mean(red_excess)) * 100.0
    p90_red_excess = float(np.percentile(red_excess, 90)) * 100.0

    # Channel ratios
    rg_ratio = float(np.mean(R / (G + 1.0)))
    rb_ratio = float(np.mean(R / (B + 1.0)))

    # 2. HSV Color Space Metrics
    # Normalize RGB to [0, 1]
    norm_rgb = rgb_arr / 255.0
    max_c = np.max(norm_rgb, axis=2)
    min_c = np.min(norm_rgb, axis=2)
    delta = max_c - min_c

    # Hue calculation (0 to 360)
    hue = np.zeros_like(max_c)
    mask_r = (max_c == norm_rgb[:, :, 0]) & (delta > 1e-5)
    mask_g = (max_c == norm_rgb[:, :, 1]) & (delta > 1e-5)
    mask_b = (max_c == norm_rgb[:, :, 2]) & (delta > 1e-5)

    hue[mask_r] = 60.0 * (((norm_rgb[:, :, 1][mask_r] - norm_rgb[:, :, 2][mask_r]) / delta[mask_r]) % 6.0)
    hue[mask_g] = 60.0 * (((norm_rgb[:, :, 2][mask_g] - norm_rgb[:, :, 0][mask_g]) / delta[mask_g]) + 2.0)
    hue[mask_b] = 60.0 * (((norm_rgb[:, :, 0][mask_b] - norm_rgb[:, :, 1][mask_b]) / delta[mask_b]) + 4.0)

    # Saturation (0 to 1)
    sat = np.zeros_like(max_c)
    mask_sat = max_c > 1e-5
    sat[mask_sat] = delta[mask_sat] / max_c[mask_sat]
    val = max_c

    mean_hue = float(np.mean(hue))
    std_hue = float(np.std(hue))
    mean_sat = float(np.mean(sat)) * 100.0
    std_sat = float(np.std(sat)) * 100.0
    mean_val = float(np.mean(val)) * 100.0
    std_val = float(np.std(val)) * 100.0

    # 3. YCbCr Chrominance (Cr reflects red capillary dilation)
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128.0
    cr_mean = float(np.mean(Cr))
    cr_std = float(np.std(Cr))

    # 4. Skin Chrominance Presence
    _, skin_fraction = detect_skin_pixels(rgb_arr)

    # 5. Grayscale Conversion
    gray_arr = 0.299 * R + 0.587 * G + 0.114 * B

    # 6. Sobel Filter Roughness (Edge Gradient Density)
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
    grad_mag = np.hypot(sobel_h, sobel_v)
    mean_roughness = float(np.mean(grad_mag))
    p90_roughness = float(np.percentile(grad_mag, 90))

    # Edge direction entropy
    grad_angle = np.arctan2(sobel_v, sobel_h + 1e-6)
    hist, _ = np.histogram(grad_angle, bins=8, range=(-np.pi, np.pi))
    hist_norm = hist / (np.sum(hist) + 1e-6)
    direction_entropy = float(-np.sum([p * np.log2(p + 1e-6) for p in hist_norm if p > 0]))

    # Edge density: fraction of pixels with significant gradient
    edge_density = float(np.mean(grad_mag > 28.0)) * 100.0

    # 7. Discrete Laplacian Sharpness
    laplacian = (
        pad[:-2, 1:-1] +
        pad[2:, 1:-1] +
        pad[1:-1, :-2] +
        pad[1:-1, 2:] -
        4.0 * pad[1:-1, 1:-1]
    )
    laplacian_sharpness = float(np.var(laplacian))

    # 8. Chromatic Dispersion (patchiness of rash / erythema)
    hue_diff = np.abs(R - B) + np.abs(R - G)
    chromatic_dispersion = float(np.std(hue_diff))

    # 9. Luminance Convexity (Tissue Swelling & Distension indicator)
    # Swollen tissue has low high-frequency deviation and smooth gradient curvature
    smoothed = np.pad(gray_arr, 2, mode='edge')
    # Simple 5x5 box blur approximation via numpy
    smoothed_box = (
        smoothed[:-4, :-4] + smoothed[:-4, 1:-3] + smoothed[:-4, 2:-2] + smoothed[:-4, 3:-1] + smoothed[:-4, 4:] +
        smoothed[1:-3, :-4] + smoothed[1:-3, 1:-3] + smoothed[1:-3, 2:-2] + smoothed[1:-3, 3:-1] + smoothed[1:-3, 4:] +
        smoothed[2:-2, :-4] + smoothed[2:-2, 1:-3] + smoothed[2:-2, 2:-2] + smoothed[2:-2, 3:-1] + smoothed[2:-2, 4:] +
        smoothed[3:-1, :-4] + smoothed[3:-1, 1:-3] + smoothed[3:-1, 2:-2] + smoothed[3:-1, 3:-1] + smoothed[3:-1, 4:] +
        smoothed[4:, :-4] + smoothed[4:, 1:-3] + smoothed[4:, 2:-2] + smoothed[4:, 3:-1] + smoothed[4:, 4:]
    ) / 25.0
    high_freq_dev = np.abs(gray_arr - smoothed_box)
    luminance_convexity = float(np.mean(high_freq_dev))

    # 10. Texture Contrast & Homogeneity
    diff_h = np.abs(gray_arr[:, 1:] - gray_arr[:, :-1])
    texture_contrast = float(np.mean(diff_h ** 2)) / 100.0
    texture_homogeneity = float(np.mean(1.0 / (1.0 + diff_h))) * 100.0

    features = [
        round(mean_ei, 4),
        round(p90_ei, 4),
        round(mean_red_excess, 4),
        round(p90_red_excess, 4),
        round(rg_ratio, 4),
        round(rb_ratio, 4),
        round(mean_hue, 4),
        round(std_hue, 4),
        round(mean_sat, 4),
        round(std_sat, 4),
        round(mean_val, 4),
        round(std_val, 4),
        round(cr_mean, 4),
        round(cr_std, 4),
        round(skin_fraction, 4),
        round(mean_roughness, 4),
        round(p90_roughness, 4),
        round(direction_entropy, 4),
        round(laplacian_sharpness, 4),
        round(chromatic_dispersion, 4),
        round(luminance_convexity, 4),
        round(texture_contrast, 4),
        round(texture_homogeneity, 4),
        round(edge_density, 4)
    ]

    features_dict = dict(zip(FEATURE_NAMES, features))
    return features, features_dict


def process_image_file(img_path):
    """
    Full pipeline: loads image, handles orientation, checks quality, and extracts features.
    Returns:
        (is_acceptable, quality_message, features_list, features_dict, gray_arr)
    """
    if not os.path.exists(img_path):
        return False, "Image file not found on server.", None, None, None

    try:
        with Image.open(img_path) as pil_img:
            # Handle smartphone EXIF orientation
            pil_img = ImageOps.exif_transpose(pil_img)
            # Consistent working resolution (max 500x500 thumbnail preserving aspect ratio)
            pil_img.thumbnail((500, 500), Image.Resampling.BILINEAR)
            rgb_img = pil_img.convert("RGB")
            rgb_arr = np.array(rgb_img, dtype=np.float64)

        gray_img = ImageOps.grayscale(rgb_img)
        gray_arr = np.array(gray_img, dtype=np.float64)

    except Exception as e:
        return False, f"Invalid or corrupted image format: {str(e)}", None, None, None

    # Quality check
    acceptable, blur_score, brightness, quality_msg, q_details = assess_image_quality(gray_arr, rgb_arr)

    # Extract features regardless so metrics are available for diagnostic feedback
    features_list, features_dict = extract_features_from_array(rgb_arr)
    features_dict["sharpness_score"] = round(blur_score, 1)
    features_dict["brightness_score"] = round(brightness, 1)
    features_dict["quality_details"] = q_details

    return acceptable, quality_msg, features_list, features_dict, gray_arr
