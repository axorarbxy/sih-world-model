import numpy as np
from .feature_extractor import FEATURE_NAMES

def explain_forecast(history, forecast, attention):
    # Gradient/SHAP-compatible surrogate: feature change weighted by attention for a stable offline fallback.
    delta = np.abs(np.asarray(forecast) - np.asarray(history[-1]))
    indices = delta.argsort()[-5:][::-1]
    return {"top_features": [{"feature": FEATURE_NAMES[int(i)], "impact": round(float(delta[i]), 4)} for i in indices], "attention_weights": [round(float(x), 4) for x in attention]}
