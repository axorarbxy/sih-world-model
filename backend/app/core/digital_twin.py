import numpy as np
from .xgboost_stage import StageClassifier

def _exfiltration_risk(states, classifier):
    values = []
    for state in states:
        stage, confidence = classifier.classify_stage(state)
        values.append(confidence if stage == "Exfiltration" else confidence * (0.15 + 0.12 * ["Reconnaissance", "Initial Access", "Lateral Movement", "Command & Control"].index(stage) if stage != "Exfiltration" else 1))
    return float(np.clip(np.mean(values), 0, 1))

def simulate_counterfactuals(history, world_model, classifier, action="block_port_445", k=5):
    future_a, _ = world_model.predict_next_k_states(history, k)
    intervened = history.copy()
    # Feature 13 is the normalized SMB/445 traffic count; neutralize it and SYN/RST pressure.
    if action == "block_port_445": intervened[-1][13] = -2.0; intervened[-1][3] *= .45; intervened[-1][5] *= .5
    future_b, _ = world_model.predict_next_k_states(intervened, k)
    risk_a, risk_b = _exfiltration_risk(future_a, classifier), _exfiltration_risk(future_b, classifier)
    return {"action": action, "future_a_risk": round(risk_a, 3), "future_b_risk": round(risk_b, 3), "recommendation": "Block Port 445" if risk_b < risk_a else "Continue monitoring", "future_a": [float(_exfiltration_risk([x], classifier)) for x in future_a], "future_b": [float(_exfiltration_risk([x], classifier)) for x in future_b]}
