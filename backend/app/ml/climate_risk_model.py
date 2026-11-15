"""
FARMINTEL AI - Machine Learning Climate Risk Classification Model
Trains a Gradient Boosting Classifier to estimate agroclimatic stress risk:
- Class 0: Low Risk / Optimal Hydrologic & Thermal Regime
- Class 1: Moderate Stress (Dry Spell or Heat Spike Exposure)
- Class 2: High Climate Stress (Acute Heat Waves, Severe Moisture Deficit)
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

FEATURE_NAMES = [
    "gdd_base50_f",
    "mean_temp_c",
    "heat_stress_days_35c",
    "total_precip_in",
    "et0_in",
    "water_balance_in",
    "max_dry_spell_days",
    "topsoil_sand_pct",
    "profile_awc_cm",
    "hydrologic_group_num"
]

class ClimateRiskModelTrainer:
    def __init__(self, data_path: str = "backend/data/agricultural_ml_dataset.csv"):
        self.data_path = data_path
        self.models_dir = "backend/data/models"
        os.makedirs(self.models_dir, exist_ok=True)

    def train_and_evaluate(self) -> Dict[str, Any]:
        df = pd.read_csv(self.data_path)

        X = df[FEATURE_NAMES]
        y = df["climate_risk_class"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        gb = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=5,
            random_state=42
        )
        gb.fit(X_train, y_train)

        y_pred = gb.predict(X_test)
        y_prob = gb.predict_proba(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted"))
        rec = float(recall_score(y_test, y_pred, average="weighted"))
        f1 = float(f1_score(y_test, y_pred, average="weighted"))
        cm = confusion_matrix(y_test, y_pred).tolist()

        feature_importances = {}
        for feat, imp in zip(FEATURE_NAMES, gb.feature_importances_):
            feature_importances[feat] = round(float(imp), 4)

        sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

        report = {
            "model_name": "GradientBoosting_ClimateRisk_Classifier",
            "model_version": "2.0.0",
            "algorithm": "GradientBoostingClassifier (100 estimators, lr=0.08, max_depth=5)",
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "classes": ["0: Low Risk", "1: Moderate Stress", "2: High Climate Stress"],
            "metrics": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4)
            },
            "confusion_matrix": cm,
            "feature_importances": sorted_importances,
            "provenance": {
                "training_dataset": "agricultural_ml_dataset.csv (2,550 multi-region samples)",
                "input_sources": "NASA POWER MERRA-2 daily climate observations"
            }
        }

        model_path = os.path.join(self.models_dir, "climate_risk_model.joblib")
        metrics_path = os.path.join(self.models_dir, "climate_risk_metrics.json")

        joblib.dump(gb, model_path)
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Climate Risk Classifier trained. Accuracy: {acc:.4f}, F1: {f1:.4f}")
        return report

if __name__ == "__main__":
    trainer = ClimateRiskModelTrainer()
    trainer.train_and_evaluate()
