from PIL import Image, ImageStat
import colorsys
import numpy as np
from collections import Counter


def load_image(image_path, size=(150, 150)):
    img = Image.open(image_path).convert('RGB')
    return img.resize(size)


def rgb_to_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return round(h * 360, 1), round(s * 100, 1), round(v * 100, 1)


def prepare_image(image_path, full_res_dynamic=False):
    img_small = load_image(image_path)

    hsv_small = img_small.convert("HSV")
    hsv_np = np.array(hsv_small).astype(np.float32)

    H_deg = (hsv_np[:, :, 0] / 255.0) * 360.0
    S_pct = (hsv_np[:, :, 1] / 255.0) * 100.0
    V_pct = (hsv_np[:, :, 2] / 255.0) * 100.0

    rgb_np = np.array(img_small)

    stat = ImageStat.Stat(img_small)
    rgb_mean = stat.mean

    if full_res_dynamic:
        img_full_hsv = Image.open(image_path).convert("HSV")
        v_raw = np.array(img_full_hsv)[:, :, 2].astype(np.float32)
    else:
        v_raw = hsv_np[:, :, 2].astype(np.float32)

    return {
        "img_small": img_small,
        "rgb_np": rgb_np,
        "hsv_np": hsv_np,
        "H_deg": H_deg,
        "S_pct": S_pct,
        "V_pct": V_pct,
        "rgb_mean": rgb_mean,
        "V_raw": v_raw,
    }


def get_average_hsv(image_path, pre=None):
    # Átlagos szin
    try:
        if pre is None:
            img = load_image(image_path)
            np_img = np.array(img)
        else:
            np_img = pre["rgb_np"]

        avg_rgb = np_img.mean(axis=(0, 1))
        r, g, b = avg_rgb
        return rgb_to_hsv(r, g, b)

    except Exception as e:
        print(f" HSV átlaghiba a {image_path} fájlnál: {e}")
        return 0, 0, 0


def get_dominant_hsv(image_path, bin_deg=10, pre=None):
    # Domináns szin hisztogram alapon
    try:
        if pre is None:
            img = load_image(image_path)
            hsv = img.convert("HSV")
            hsv_np = np.array(hsv).astype(np.float32)

            H = (hsv_np[:, :, 0] / 255.0) * 360.0
            S = (hsv_np[:, :, 1] / 255.0) * 100.0
            V = (hsv_np[:, :, 2] / 255.0) * 100.0
        else:
            H = pre["H_deg"]
            S = pre["S_pct"]
            V = pre["V_pct"]

        # Hue hisztogram
        bins = np.arange(0, 360 + bin_deg, bin_deg)
        hist, edges = np.histogram(H.flatten(), bins=bins)
        idx = np.argmax(hist)

        lo, hi = edges[idx], edges[idx + 1]
        mask = (H >= lo) & (H < hi)

        return (
            round(float(H[mask].mean()), 1),
            round(float(S[mask].mean()), 1),
            round(float(V[mask].mean()), 1),
        )

    except Exception as e:
        print(f"Domináns szín hiba: {image_path} -> {e}")
        return 0, 0, 0


def get_dominant_colors_hsv(image_path, top_n=3, pre=None):
    try:
        if pre is None:
            img = load_image(image_path)
            hsv = img.convert("HSV")
            hsv_np = np.array(hsv).astype(np.float32)

            H = hsv_np[:, :, 0]
            H_deg = (H / 255.0) * 360.0
        else:
            H_deg = pre["H_deg"]

        # színkategória minden pixelre
        bins = np.array([get_color_name(h) for h in H_deg.flatten()])
        total = len(bins) if len(bins) else 1

        counts = Counter(bins)
        ranked = counts.most_common(top_n)

        out = []
        for color, cnt in ranked:
            mask = (bins == color)
            avg_hue = float(H_deg.flatten()[mask].mean()) if mask.any() else 0.0
            ratio = cnt / total
            pct_val = pct(ratio)
            out.append((color, pct_val, round(avg_hue, 1)))

        return out

    except Exception as e:
        print(f"Domináns szín hiba: {image_path} -> {e}")
        return [("", 0.0, 0.0)] * top_n


def estimate_white_balance(image_path, pre=None):
    try:
        if pre is None:
            img = load_image(image_path)
            stat = ImageStat.Stat(img)

            r_mean, g_mean, b_mean = stat.mean
        else:
            r_mean, g_mean, b_mean = pre["rgb_mean"]

        avg_gray = (r_mean + g_mean + b_mean) / 3

        # Arányok
        r_ratio = r_mean / avg_gray
        g_ratio = g_mean / avg_gray
        b_ratio = b_mean / avg_gray

        # Kiértékelés (Becslés)
        if r_ratio > 1.05 and g_ratio < 1.0:
            balance_type = "Meleg (pirosas tónus)"
        elif b_ratio > 1.05 and r_ratio < 1.0:
            balance_type = "Hideg (kékes tónus)"
        elif abs(r_ratio - b_ratio) < 0.05 and abs(r_ratio - g_ratio) < 0.05:
            balance_type = "Semleges / Fehér kiegyensúlyozott"
        else:
            balance_type = "Vegyes / Bizonytalan"

        return round(r_ratio, 2), round(g_ratio, 2), round(b_ratio, 2), balance_type

    except Exception as e:
        print(f" Fehéregyensúly hiba: {e}")
        return 0, 0, 0, "Hiba"


def estimate_dynamic_range(image_path, pre=None):
    # Kép fényesség dinamikatartományának becslés
    try:
        if pre is None:
            img = Image.open(image_path).convert("HSV")
            v_channel = np.array(img)[:, :, 2]
        else:
            v_channel = pre["V_raw"]

        # Percentilis-alapú fényességértékek
        v_min = np.percentile(v_channel, 5)   # alsó 5% (árnyékok kihagyva)
        v_max = np.percentile(v_channel, 95)  # felső 5% (kiégett részek kihagyva)

        dyn_range = v_max - v_min

        # Kategorizálás
        if dyn_range < 60:
            hdr_text = "Alacsony dinamikatartomány (sötét / árnyékos kép)"
        elif dyn_range < 120:
            hdr_text = "Közepes dinamikatartomány"
        elif dyn_range < 200:
            hdr_text = "Magas dinamikatartomány"
        else:
            hdr_text = "Nagyon magas dinamikatartomány (HDR jellegű)"

        return round(float(v_min), 1), round(float(v_max), 1), round(float(dyn_range), 1), hdr_text

    except Exception as e:
        return 0, 0, 0, f"Hiba a fényesség-elemzésnél: {e}"


def estimate_color_depth(image_path):
    # Színmélység becslése
    try:
        img = Image.open(image_path)
        mode = img.mode

        # PIL mód alapján becslés
        if mode == "RGB":
            depth = 8
        elif mode == "RGBA" or mode == "I;16":
            depth = 16
        else:
            depth = 8

        return depth

    except Exception as e:
        print(f" Színmélység hiba: {e}")
        return 0


def get_color_distribution(image_path, pre=None):
    # 3x3 felosztás
    try:
        if pre is None:
            img = load_image(image_path)

            hsv = img.convert("HSV")
            hsv_np = np.array(hsv).astype(np.float32)

            H_deg = (hsv_np[:, :, 0] / 255.0) * 360.0
            S = hsv_np[:, :, 1].astype(np.float32)
        else:
            H_deg = pre["H_deg"]
            S = pre["hsv_np"][:, :, 1].astype(np.float32)

        h, w = H_deg.shape
        row_h = h // 3
        col_w = w // 3
        gray_thr = 40.0

        def ratios(Hd, Sd):
            total = Hd.size if Hd.size else 1

            green = ((Hd >= 60) & (Hd <= 150)).sum() / total
            blue = ((Hd >= 180) & (Hd <= 260)).sum() / total
            warm = (((Hd >= 0) & (Hd <= 60)) | ((Hd >= 300) & (Hd < 360))).sum() / total
            gray = (Sd <= gray_thr).sum() / total

            return float(green), float(blue), float(warm), float(gray)

        out = {}

        for r_idx in range(3):
            for c_idx in range(3):
                y1, y2 = r_idx * row_h, (r_idx + 1) * row_h if r_idx < 2 else h
                x1, x2 = c_idx * col_w, (c_idx + 1) * col_w if c_idx < 2 else w

                g, b, w_, gr = ratios(H_deg[y1:y2, x1:x2], S[y1:y2, x1:x2])

                label = f"row{r_idx}_col{c_idx}"
                out[f"Zold_{label}"] = g
                out[f"Kek_{label}"] = b
                out[f"Meleg_{label}"] = w_
                out[f"Szurke_{label}"] = gr
        return out

    except Exception:
        return {}


def get_color_name(hue):
    h = float(hue)
    if h < 15 or h >= 345:
        return "Piros"
    elif 15 <= h < 45:
        return "Narancs"
    elif 45 <= h < 75:
        return "Sárga"
    elif 75 <= h < 150:
        return "Zöld"
    elif 150 <= h < 210:
        return "Cián/Türkiz"
    elif 210 <= h < 270:
        return "Kék"
    elif 270 <= h < 310:
        return "Lila"
    elif 310 <= h < 345:
        return "Pink/Magenta"
    return "Ismeretlen"


def pct(x):
    # 0–1 arányból százalék (0–100) tizedes pontossággal.
    try:
        return round(float(x) * 100, 1)
    except:
        return 0.0