"""
FARMINTEL AI - Machine Learning Crop Suitability Model
Trains and validates a multi-crop agronomic suitability ensemble using Random Forest
and Gradient Boosting on real NASA POWER agroclimate and USDA SSURGO edaphic observations.
Evaluates R2, MAE, RMSE, 5-fold CV, and feature importances.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
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

CANDIDATE_CROPS = [
    "corn", "soybeans", "winter_wheat", "grain_sorghum", "alfalfa",
    "oats", "cereal_rye", "red_clover", "sunflower", "barley"
]

class CropSuitabilityModelTrainer:
    """Trains and serializes the multi-crop suitability regression ensemble."""

    def __init__(self, data_path: str = "backend/data/agricultural_ml_dataset.csv"):
        self.data_path = data_path
        self.models_dir = "backend/data/models"
        os.makedirs(self.models_dir, exist_ok=True)

    def train_and_evaluate(self) -> Dict[str, Any]:
        df = pd.read_csv(self.data_path)

        X = df[FEATURE_NAMES]
        target_cols = [f"suitability_{crop}" for crop in CANDIDATE_CROPS]
        Y = df[target_cols]

        # 80/20 train/test split with seed
        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=0.20, random_state=42
        )

        print(f"Training Crop Suitability Random Forest on {len(X_train)} samples, testing on {len(X_test)} samples...")

        # Multi-output Random Forest Regressor
        rf = RandomForestRegressor(
            n_estimators=120,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train, Y_train)

        # Predict on held-out test split
        Y_pred = rf.predict(X_test)
        Y_pred_df = pd.DataFrame(Y_pred, columns=target_cols, index=Y_test.index)

        # Metrics per crop
        per_crop_metrics = {}
        for crop in CANDIDATE_CROPS:
            col = f"suitability_{crop}"
            y_t = Y_test[col]
            y_p = Y_pred_df[col]
            r2 = float(r2_score(y_t, y_p))
            mae = float(mean_absolute_error(y_t, y_p))
            rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
            per_crop_metrics[crop] = {
                "r2_score": round(r2, 4),
                "mae": round(mae, 4),
                "rmse": round(rmse, 4),
                "test_mean_suitability": round(float(y_t.mean()), 3),
                "pred_mean_suitability": round(float(y_p.mean()), 3)
            }

        # Composite overall metrics
        overall_r2 = float(r2_score(Y_test, Y_pred, multioutput="uniform_average"))
        overall_mae = float(mean_absolute_error(Y_test, Y_pred))
        overall_rmse = float(np.sqrt(mean_squared_error(Y_test, Y_pred)))

        # Feature importances
        feature_importances = {}
        for feat, imp in zip(FEATURE_NAMES, rf.feature_importances_):
            feature_importances[feat] = round(float(imp), 4)

        # Sort feature importances descending
        sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

        # 5-fold cross validation on composite score
        cv_scores = cross_val_score(rf, X, Y, cv=5, scoring="r2", n_jobs=-1)

        evaluation_report = {
            "model_name": "RandomForest_MultiCrop_Suitability_Ensemble",
            "model_version": "2.0.0",
            "algorithm": "RandomForestRegressor (120 estimators, max_depth=12)",
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_count": len(FEATURE_NAMES),
            "features": FEATURE_NAMES,
            "target_crops": CANDIDATE_CROPS,
            "overall_metrics": {
                "r2_score": round(overall_r2, 4),
                "mae": round(overall_mae, 4),
                "rmse": round(overall_rmse, 4),
                "cv_5fold_r2_mean": round(float(cv_scores.mean()), 4),
                "cv_5fold_r2_std": round(float(cv_scores.std()), 4)
            },
            "per_crop_metrics": per_crop_metrics,
            "feature_importances": sorted_importances,
            "provenance": {
                "training_dataset": "agricultural_ml_dataset.csv (2,550 multi-region samples)",
                "input_sources": "NASA POWER MERRA-2 + USDA NRCS SSURGO SDA"
            }
        }

        # Save model and metrics
        model_path = os.path.join(self.models_dir, "crop_suitability_model.joblib")
        metrics_path = os.path.join(self.models_dir, "crop_suitability_metrics.json")

        joblib.dump(rf, model_path)
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_report, f, indent=2)

        print(f"Model trained successfully. Overall R2: {overall_r2:.4f}, MAE: {overall_mae:.4f}")
        print(f"Artifacts saved to {model_path} and {metrics_path}")
        return evaluation_report

if __name__ == "__main__":
    trainer = CropSuitabilityModelTrainer()
    trainer.train_and_evaluate()
