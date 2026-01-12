from colors import (
    prepare_image,
    get_average_hsv,
    get_dominant_hsv,
    estimate_white_balance,
    estimate_dynamic_range,
    get_color_distribution
)
import numpy as np
from skimage.feature import canny
from skimage.transform import probabilistic_hough_line
from skimage.color import rgb2gray
from skimage.filters import sobel


def extract_features_for_training(image_path, pre=None):
    # Random Forest tanításhoz szükséges jellemzők kinyerése
    if pre is None:
        pre = prepare_image(image_path, full_res_dynamic=False)

    # Alapszín értékek
    h, s, v = get_average_hsv(image_path, pre=pre)
    dh, ds, dv = get_dominant_hsv(image_path, pre=pre)
    r_ratio, g_ratio, b_ratio, _ = estimate_white_balance(image_path, pre=pre)
    v_min, v_max, dyn_range, _ = estimate_dynamic_range(image_path, pre=pre)

    feat = {
        "Atlagos_Hue": h,
        "Atlagos_Sat": s,
        "Atlagos_Val": v,
        "Dominans_Hue": dh,
        "Dominans_Sat": ds,
        "Dominans_Val": dv,
        "WB_R": r_ratio,
        "WB_G": g_ratio,
        "WB_B": b_ratio,
        "Fenyesseg_min": v_min,
        "Fenyesseg_max": v_max,
        "Dinamikatartomany": dyn_range,
    }

    # 3×3 színeloszlás
    row_stats = get_color_distribution(image_path, pre=pre)
    feat.update(row_stats)

    # Hue‑hisztogram
    try:
        h_deg = pre["H_deg"]
        bins = [0, 60, 150, 260, 360]
        hist, _ = np.histogram(h_deg, bins=bins, density=False)
        total = hist.sum() if hist.sum() > 0 else 1
        hist = hist / total

        feat["Hue_pct_warm"] = float(hist[0])   # vörös/sárga – naplemente
        feat["Hue_pct_green"] = float(hist[1])  # zöld – erdei
        feat["Hue_pct_blue"] = float(hist[2])   # kék – víz/ég
        feat["Hue_pct_other"] = float(hist[3])  # egyéb

    except Exception:
        feat["Hue_pct_warm"] = 0.0
        feat["Hue_pct_green"] = 0.0
        feat["Hue_pct_blue"] = 0.0
        feat["Hue_pct_other"] = 0.0

    try:
        struct_feats = get_structural_features(pre["img_small"])
        feat.update(struct_feats)
    except Exception:
        feat["Textura_suruseg"] = 0.0
        feat["Vonalak_szama"] = 0

    return feat


def get_structural_features(img_small):
    img_gray = rgb2gray(np.array(img_small))
    edges = sobel(img_gray)
    edge_mean = np.mean(edges)

    canny_edges = canny(img_gray, sigma=2)
    lines = probabilistic_hough_line(canny_edges, threshold=10, line_length=15, line_gap=3)

    return {
        "Textura_suruseg": edge_mean,
        "Vonalak_szama": len(lines)
    }
