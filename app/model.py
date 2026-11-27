import hashlib
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "lgbm_fraud.joblib"
MODEL_NAME = "fraud-lgbm"
MODEL_VERSION = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()[:12]

bundle = joblib.load(MODEL_PATH)


def predict(application: dict) -> dict:
    """Skor satu pengajuan, dengan preprocessing yang sama seperti notebook bagian 9."""
    X = pd.DataFrame([application])[bundle["features"]]
    for col, cats in bundle["categories"].items():
        X[col] = pd.Categorical(X[col], categories=cats)
    score = float(bundle["model"].predict_proba(X)[0, 1])
    threshold = float(bundle["threshold"])
    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "fraud_score": score,
        "is_fraud": score >= threshold,
        "threshold": threshold,
    }
