import numpy as np
from ..utils.mitre_mapping import MITRE_STAGES

class StageClassifier:
    """Loads a trained XGBoost model when present; deterministic heuristic otherwise."""
    def __init__(self, path=None):
        self.model = None
        if path and path.exists():
            import xgboost as xgb; self.model = xgb.XGBClassifier(); self.model.load_model(path)
    def classify_stage(self, state):
        if self.model:
            p = self.model.predict_proba(np.asarray(state).reshape(1, -1))[0]; index = int(p.argmax()); return MITRE_STAGES[index], float(p[index])
        score = float(np.clip((state[3] + state[5] + state[13]) / 5 + .35, 0, 1))
        index = min(4, max(0, int(score * 5))); return MITRE_STAGES[index], max(.55, score)
