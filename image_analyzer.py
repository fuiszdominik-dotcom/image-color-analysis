import os
import exifread
import joblib
import pandas as pd
from openpyxl import Workbook
from histogram import create_hsv_histogram
from colors import (
    prepare_image,
    get_average_hsv,
    get_dominant_hsv,
    get_dominant_colors_hsv,
    estimate_white_balance,
    estimate_dynamic_range,
    estimate_color_depth,
    get_color_distribution,
    pct
)

try:
    from features import extract_features_for_training
except Exception:
    extract_features_for_training = None

# Random Forest modell betöltése
try:
    rf_model, rf_features = joblib.load("rf_model.pkl")
    print("Random Forest modell betöltve.")
except Exception:
    rf_model = None
    rf_features = None
    print("Random Forest modell nem található, kategorizálás kihagyva.")


def collect_exif_fields(image_path):
    data = {
        "Fájlnév": os.path.basename(image_path),
        "Gyártó": "",
        "Modell": "",
        "Készítés ideje": "",
        "GPS szélesség": "",
        "GPS hosszúság": "",
        "Megjegyzés": "",
        "Átlagos Hue (°)": 0, "Átlagos Sat (%)": 0, "Átlagos Val (%)": 0,
        "Domináns Hue (Hisztogram °)": 0, "Domináns Sat (%)": 0, "Domináns Val (%)": 0,
        "Top1_szín": "",
        "Top1_pct (%)": 0.0,
        "Top1_Hue (°)": 0.0,

        "Top2_szín": "",
        "Top2_pct (%)": 0.0,
        "Top2_Hue (°)": 0.0,

        "Top3_szín": "",
        "Top3_pct (%)": 0.0,
        "Top3_Hue (°)": 0.0,

        "Domináns színek (Top3)": "",

        "Fehéregyensúly R arány (%)": 0,
        "Fehéregyensúly G arány (%)": 0,
        "Fehéregyensúly B arány (%)": 0,
        "Fehéregyensúly típusa": "",
        "Fényesség min": 0,
        "Fényesség max": 0,
        "Dinamikatartomány": 0,
        "HDR jellemző": "",
        "Színmélység (bit)": 0,
    }

    try:
        # EXIF olvasás
        if image_path.lower().endswith((".jpg", ".jpeg")):
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)

            if not tags:
                data["Megjegyzés"] = "Nincsenek EXIF metaadatok"
            else:
                if "Image Make" in tags:
                    data["Gyártó"] = str(tags["Image Make"])
                if "Image Model" in tags:
                    data["Modell"] = str(tags["Image Model"])
                if "EXIF DateTimeOriginal" in tags:
                    data["Készítés ideje"] = str(tags["EXIF DateTimeOriginal"])
                if "GPS GPSLatitude" in tags:
                    data["GPS szélesség"] = str(tags["GPS GPSLatitude"])
                if "GPS GPSLongitude" in tags:
                    data["GPS hosszúság"] = str(tags["GPS GPSLongitude"])

                if not any([
                    data["Gyártó"],
                    data["Modell"],
                    data["Készítés ideje"],
                    data["GPS szélesség"]
                ]):
                    data["Megjegyzés"] = "Kevés metaadat"
        else:
            data["Megjegyzés"] = "Formátum nem tartalmaz EXIF-et"

    except Exception as e:
        data["Megjegyzés"] = f"Hiba: {e}"

    return data


def fill_color_features(image_path, base_data):

    pre = prepare_image(image_path, full_res_dynamic=False)

    # Színelemzés
    h, s, v = get_average_hsv(image_path, pre=pre)
    base_data["Átlagos Hue (°)"] = h
    base_data["Átlagos Sat (%)"] = s
    base_data["Átlagos Val (%)"] = v

    dh, ds, dv = get_dominant_hsv(image_path, pre=pre)
    base_data["Domináns Hue (Hisztogram °)"] = dh
    base_data["Domináns Sat (%)"] = ds
    base_data["Domináns Val (%)"] = dv

    top = get_dominant_colors_hsv(image_path, top_n=3, pre=pre)
    while len(top) < 3:
        top.append(("", 0.0, 0.0))

    base_data["Top1_szín"] = top[0][0]
    base_data["Top1_pct (%)"] = top[0][1]
    base_data["Top1_Hue (°)"] = top[0][2]

    base_data["Top2_szín"] = top[1][0]
    base_data["Top2_pct (%)"] = top[1][1]
    base_data["Top2_Hue (°)"] = top[1][2]

    base_data["Top3_szín"] = top[2][0]
    base_data["Top3_pct (%)"] = top[2][1]
    base_data["Top3_Hue (°)"] = top[2][2]

    base_data["Domináns színek (Top3)"] = (
        f"{top[0][0]} ({top[0][1]}% – {top[0][2]}°) | "
        f"{top[1][0]} ({top[1][1]}% – {top[1][2]}°) | "
        f"{top[2][0]} ({top[2][1]}% – {top[2][2]}°)"
    )

    r_ratio, g_ratio, b_ratio, wb_text = estimate_white_balance(image_path, pre=pre)

    v_min, v_max, dyn_range, hdr_text = estimate_dynamic_range(image_path, pre=pre)

    depth = estimate_color_depth(image_path)

    base_data["Fehéregyensúly R arány (%)"] = r_ratio
    base_data["Fehéregyensúly G arány (%)"] = g_ratio
    base_data["Fehéregyensúly B arány (%)"] = b_ratio
    base_data["Fehéregyensúly típusa"] = wb_text
    base_data["Fényesség min"] = v_min
    base_data["Fényesség max"] = v_max
    base_data["Dinamikatartomány"] = dyn_range
    base_data["HDR jellemző"] = hdr_text
    base_data["Színmélység (bit)"] = depth

    row_stats = get_color_distribution(image_path, pre=pre)

    def get_row_pct(prefix, r):
        val = (row_stats.get(f"{prefix}_row{r}_col0", 0) +
               row_stats.get(f"{prefix}_row{r}_col1", 0) +
               row_stats.get(f"{prefix}_row{r}_col2", 0)) / 3
        return pct(val)

    pretty_rows = {
        "Zöld – felső (%)": get_row_pct("Zold", 0),
        "Zöld – középső (%)": get_row_pct("Zold", 1),
        "Zöld – alsó (%)": get_row_pct("Zold", 2),
        "Kék – felső (%)": get_row_pct("Kek", 0),
        "Kék – középső (%)": get_row_pct("Kek", 1),
        "Kék – alsó (%)": get_row_pct("Kek", 2),
        "Meleg – felső (%)": get_row_pct("Meleg", 0),
        "Meleg – középső (%)": get_row_pct("Meleg", 1),
        "Meleg – alsó (%)": get_row_pct("Meleg", 2),
        "Szürke – felső (%)": get_row_pct("Szurke", 0),
        "Szürke – középső (%)": get_row_pct("Szurke", 1),
        "Szürke – alsó (%)": get_row_pct("Szurke", 2),
    }

    base_data.update(pretty_rows)

    return base_data, row_stats, pre


def fill_rf_category(image_path, data, row_stats, pre=None):
    if rf_model is not None and rf_features is not None:
        try:
            # features.py-ből kinyerjük a tanításhoz használt jellemzőket
            if extract_features_for_training is not None:
                model_feats = extract_features_for_training(image_path, pre=pre)
            else:
                # Még se lehetne elérni a featurest -> használjuk a 3×3 színsáv statisztikákat és a jelenlegi adatokat
                model_feats = {**row_stats, **data}

            # A modell által várt oszlopokat rendezzük a helyes sorrendben
            row_for_model = {col: model_feats.get(col, 0) for col in rf_features}
            df_row = pd.DataFrame([row_for_model])

            # Becslés
            proba = rf_model.predict_proba(df_row)[0]
            max_proba = proba.max()

            UNKNOWN_THR = 0.35

            if max_proba < UNKNOWN_THR:
                data["Becsült kategoria"] = "ismeretlen"
            else:
                data["Becsült kategoria"] = rf_model.classes_[proba.argmax()]

        except Exception as e:
            data["Becsült kategoria"] = f"Hiba RF-ben: {e}"
    else:
        data["Becsült kategoria"] = "Nincs modell"

    return data


def read_exif(image_path):
    # EXIF és alapmezők
    data = collect_exif_fields(image_path)

    # Színjellemzők
    try:
        data, row_stats, pre = fill_color_features(image_path, data)
    except Exception as e:
        data["Megjegyzés"] = f"Hiba: {e}"
        row_stats = {}

    # Random Forest kategória
    data = fill_rf_category(image_path, data, row_stats, pre=pre)

    return data


def analyze_folder(folder_path, generate_histograms=True):
    # Mappában lévő képek feldolgozása és mentése Excel-be
    if not os.path.exists(folder_path):
        print(" A megadott mappa nem létezik.")
        return

    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(folder_path, filename)
            info = read_exif(path)
            results.append(info)

            if generate_histograms:
                hist_path = create_hsv_histogram(path)
                print(f" Hisztogram mentve: {hist_path}")

            print(f" Feldolgozva: {filename}")

    if not results:
        print(" Nincs feldolgozható kép a mappában.")
        return

    # Excel mentés
    save_to_excel(results)
    print(f"\nEredmények sikeresen elmentve: kep_szinelemzes_eredmenyek.xlsx")


def save_to_excel(data, output_path="kep_szinelemzes_eredmenyek.xlsx"):
    # Adatok mentése Excel (XLSX) formátumba
    wb = Workbook()
    ws = wb.active
    ws.title = "Kép színelemzés"

    headers = list(data[0].keys())
    ws.append(headers)

    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)
        cell.fill = cell.fill.copy(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    for row in data:
        ws.append(list(row.values()))

    for column_cells in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = max_length + 2

    wb.save(output_path)
