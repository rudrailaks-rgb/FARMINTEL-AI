"""
FARMINTEL AI - Machine Learning Crop Yield Performance Regressor
Trains a Gradient Boosting Regressor to estimate the relative crop yield performance factor
(relative to USDA county historical baseline: 0.35x to 1.45x) conditioned on thermal
accumulation, water balance, and available water holding capacity.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

FEATURE_NAMES = [
    "gdd_base50_f",
    "mean_temp_c",
    "heat_stress_days_35c",
    "total_precip_in",
    "et0_in",
    "water_balance_in",
    "max_dry_spell_days",
    "topsoil_sand_pct",
    "topsoil_silt_pct",
    "topsoil_clay_pct",
    "topsoil_ph",
    "topsoil_om_pct",
    "profile_awc_cm",
    "drainage_class_num",
    "hydrologic_group_num"
]

class YieldPerformanceModelTrainer:
    def __init__(self, data_path: str = "backend/data/agricultural_ml_dataset.csv"):
        self.data_path = data_path
        self.models_dir = "backend/data/models"
        os.makedirs(self.models_dir, exist_ok=True)

    def train_and_evaluate(self) -> Dict[str, Any]:
        df = pd.read_csv(self.data_path)

        X = df[FEATURE_NAMES]
        y = df["yield_performance_index"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )

        gbr = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=5,
            random_state=42
        )
        gbr.fit(X_train, y_train)

        y_pred = gbr.predict(X_test)

        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

        feature_importances = {}
        for feat, imp in zip(FEATURE_NAMES, gbr.feature_importances_):
            feature_importances[feat] = round(float(imp), 4)

        sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

        report = {
            "model_name": "GradientBoosting_YieldPerformance_Regressor",
            "model_version": "2.0.0",
            "algorithm": "GradientBoostingRegressor (100 estimators, lr=0.08, max_depth=5)",
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "metrics": {
                "r2_score": round(r2, 4),
                "mae": round(mae, 4),
                "rmse": round(rmse, 4),
                "test_mean_yield_factor": round(float(y_test.mean()), 3),
                "pred_mean_yield_factor": round(float(y_pred.mean()), 3)
            },
            "feature_importances": sorted_importances,
            "provenance": {
                "training_dataset": "agricultural_ml_dataset.csv (2,550 multi-region samples)",
                "input_sources": "NASA POWER MERRA-2 + USDA NRCS SSURGO SDA"
            }
        }

        model_path = os.path.join(self.models_dir, "yield_performance_model.joblib")
        metrics_path = os.path.join(self.models_dir, "yield_performance_metrics.json")

        joblib.dump(gbr, model_path)
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"Yield Performance Regressor trained. R2: {r2:.4f}, MAE: {mae:.4f}")
        return report

if __name__ == "__main__":
    trainer = YieldPerformanceModelTrainer()
    trainer.train_and_evaluate()
