import numpy as np
from .xgboost_stage import StageClassifier

def _exfiltration_risk(states, classifier):
    values = []
    for state in states:
        stage, confidence = classifier.classify_stage(state)
        values.append(confidence if stage == "Exfiltration" else confidence * (0.15 + 0.12 * ["Reconnaissance", "Initial Access", "Lateral Movement", "Command & Control"].index(stage) if stage != "Exfiltration" else 1))
    return float(np.clip(np.mean(values), 0, 1))

def simulate_counterfactuals(history, world_model, classifier, action="block_port_445", k=5):
    if action not in {"block_port_445", "rate_limit_syn"}:
        raise ValueError(f"Unsupported mitigation action: {action}")
    future_a, _ = world_model.predict_next_k_states(history, k)
    intervened = history.copy()
    # Feature 13 is the normalized SMB/445 traffic count; neutralize it and SYN/RST pressure.
    if action == "block_port_445": intervened[-1][13] = -2.0; intervened[-1][3] *= .45; intervened[-1][5] *= .5
    if action == "rate_limit_syn": intervened[-1][3] *= .2; intervened[-1][0] *= .7
    future_b, _ = world_model.predict_next_k_states(intervened, k)
    risk_a, risk_b = _exfiltration_risk(future_a, classifier), _exfiltration_risk(future_b, classifier)
    # Avoid recommending a disruptive control for a numerical fluctuation that
    # disappears when the dashboard rounds risk to a percentage.
    reduction = risk_a - risk_b
    action_label = {"block_port_445": "Block Port 445", "rate_limit_syn": "Rate Limit SYN Packets"}[action]
    recommendation = action_label if reduction >= 0.02 else "Continue monitoring"
    return {"action": action, "future_a_risk": round(risk_a, 3), "future_b_risk": round(risk_b, 3), "risk_reduction": round(max(0.0, reduction), 3), "recommendation": recommendation, "future_a": [float(_exfiltration_risk([x], classifier)) for x in future_a], "future_b": [float(_exfiltration_risk([x], classifier)) for x in future_b]}

def simulate_minimum_action(history, world_model, classifier, k=5):
    candidates = [simulate_counterfactuals(history, world_model, classifier, action, k) for action in ("block_port_445", "rate_limit_syn")]
    best = max(candidates, key=lambda item: item["risk_reduction"])
    best["alternatives"] = [{"action": item["action"], "risk_reduction": item["risk_reduction"], "future_b_risk": item["future_b_risk"]} for item in candidates]
    return best
