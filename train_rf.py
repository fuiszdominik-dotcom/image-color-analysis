import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split, StratifiedKFold,
    cross_val_score, GridSearchCV
)
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from features import extract_features_for_training

DATASET_DIR = "train_dataset"
OUT_MODEL = "rf_model.pkl"


def collect_training_data():
    rows = []
    for label in os.listdir(DATASET_DIR):
        class_dir = os.path.join(DATASET_DIR, label)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                full = os.path.join(class_dir, fname)
                feat = extract_features_for_training(full)
                feat["Kategoria"] = label
                rows.append(feat)
    return pd.DataFrame(rows)


def main():
    print("Tanító képek beolvasása...")
    df = collect_training_data()

    print("\nTanító adatok előnézete:")
    print(df.head())

    print("\nOsztályeloszlás:")
    print(df["Kategoria"].value_counts())

    # hiányzó értékek kitöltése
    if df.isna().any().any():
        df = df.fillna(0)

    # keverés
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    X = df.drop(columns="Kategoria")
    y = df["Kategoria"]

    print(f"\n {len(df)} képen tanítunk…")

    # kiegyensúlyozás osztálysúlyokkal
    classes = np.array(sorted(y.unique()))
    class_weights = compute_class_weight('balanced', classes=classes, y=y)
    class_weight_dict = {c: w for c, w in zip(classes, class_weights)}

    # hyperparaméter-rács
    param_grid = {
        'n_estimators': [300, 500, 700],
        'max_depth': [None, 10, 20],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    base_rf = RandomForestClassifier(
        random_state=42, n_jobs=-1, class_weight=class_weight_dict
    )
    grid_search = GridSearchCV(
        estimator=base_rf,
        param_grid=param_grid,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='accuracy',
        n_jobs=-1
    )
    grid_search.fit(X, y)
    rf_best = grid_search.best_estimator_
    print("\nLegjobb hiperparaméterek:", grid_search.best_params_)

    # hold‑out validáció
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    rf_hold = rf_best.fit(X_tr, y_tr)
    print("\nHold-out pontosság (20% teszt):", f"{rf_hold.score(X_te, y_te):.3f}")
    y_pred = rf_hold.predict(X_te)
    print("\nRészletes jelentés:")
    print(classification_report(y_te, y_pred, digits=3))
    print("Konfúziós mátrix:")
    print(confusion_matrix(y_te, y_pred))

    # 5-fold CV a legjobb modellel
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(rf_best, X, y, cv=cv, n_jobs=-1)
    print("\n 5-fold CV pontosságok:", [f"{s:.3f}" for s in cv_scores])
    print("Átlag ± szórás:", f"{cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # végső modell
    rf_final = rf_best.fit(X, y)
    # jellemzőfontosságok
    fi = rf_final.feature_importances_
    feature_cols = X.columns
    top = sorted(zip(feature_cols, fi), key=lambda x: x[1], reverse=True)[:15]
    print("\n Legfontosabb jellemzők:")
    for name, val in top:
        print(f"  {name}: {val:.3f}")

    joblib.dump((rf_final, list(feature_cols)), OUT_MODEL)
    print(f"\n Modell elmentve: {OUT_MODEL}")


if __name__ == "__main__":
    main()
