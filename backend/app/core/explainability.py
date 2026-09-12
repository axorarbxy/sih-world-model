import numpy as np
import torch
from torch import nn
from .feature_extractor import FEATURE_NAMES

class _ForecastHead(nn.Module):
    """SHAP adapter that exposes only the predicted next-state vector."""
    def __init__(self, model): super().__init__(); self.model = model
    def forward(self, states): return self.model(states)[0]

def explain_forecast(history, forecast, attention, world_model=None):
    """Return per-feature SHAP values when the optional local package works.

    Attention-weighted state deltas remain an explicit offline fallback for
    environments where SHAP cannot trace a particular PyTorch installation.
    """
    method = "attention-weighted state delta"
    delta = np.abs(np.asarray(forecast) - np.asarray(history[-1]))
    if world_model is not None:
        try:
            import shap
            sequence = np.asarray(history[-8:], dtype=np.float32)
            if len(sequence) < 8: sequence = np.pad(sequence, ((8-len(sequence), 0), (0, 0)))
            background = torch.tensor(sequence[None, :, :], dtype=torch.float32)
            explainer = shap.GradientExplainer(_ForecastHead(world_model.model), background)
            values = explainer.shap_values(background)
            values = values[0] if isinstance(values, list) else values
            delta = np.abs(np.asarray(values)).mean(axis=tuple(range(np.asarray(values).ndim - 1)))
            method = "SHAP GradientExplainer"
        except Exception:
            pass
    indices = delta.argsort()[-5:][::-1]
    return {"method": method, "top_features": [{"feature": FEATURE_NAMES[int(i)], "impact": round(float(delta[i]), 4)} for i in indices], "attention_weights": [round(float(x), 4) for x in attention]}
