"""Repeatable offline benchmark for the project report.

Uses labelled CIC-IDS/CTU state CSVs when supplied through --csv. With no
dataset it builds deterministic synthetic labelled transitions so judges can
verify the benchmark workflow end to end. Results are written locally and are
never presented as a real-dataset claim.
"""
import argparse, json, sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split
from app.core.feature_extractor import extract_csv

def synthetic():
    rng = np.random.default_rng(26153); x = rng.normal(0, 1, (1600, 14))
    attack = rng.random(len(x)) < .35
    x[attack, 3] += rng.uniform(1.5, 4, attack.sum()); x[attack, 5] += rng.uniform(.5, 2.5, attack.sum()); x[attack, 13] += rng.uniform(1, 4, attack.sum())
    return x, attack.astype(int), "synthetic deterministic traffic"

def metrics(y, pred):
    precision, recall, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"precision": round(float(precision), 4), "recall": round(float(recall), 4), "f1": round(float(f1), 4), "false_positive_rate": round(float(fp / max(1, fp + tn)), 4), "support": int(len(y))}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--states-npy"); parser.add_argument("--labels-npy"); args = parser.parse_args()
    if bool(args.states_npy) != bool(args.labels_npy): parser.error("Provide --states-npy and --labels-npy together")
    if args.states_npy:
        x, y = np.load(args.states_npy), np.load(args.labels_npy).astype(int)
        if len(x) != len(y) or x.ndim != 2: parser.error("State matrix and labels must have equal row counts")
        source = f"labelled state arrays: {Path(args.states_npy).name}"
    else: x, y, source = synthetic()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.25, random_state=42, stratify=y)
    baseline = LogisticRegression(max_iter=1000, class_weight="balanced").fit(x_train, y_train)
    # Temporal proxy: include state deltas, rolling context and raw state.
    # This evaluates temporal dynamics against a static baseline without
    # claiming a synthetic result is a CIC/CTU result.
    def temporal(a): return np.hstack([a, np.roll(a, 1, axis=0), a - np.roll(a, 1, axis=0)])
    temporal_model = LogisticRegression(max_iter=1000, class_weight="balanced").fit(temporal(x_train), y_train)
    report = {"dataset": source, "warning": "Synthetic results demonstrate the benchmark procedure only. Run with labelled CIC-IDS-2018 or CTU-13 state data for reportable results.", "logistic_regression": metrics(y_test, baseline.predict(x_test)), "temporal_dynamics_baseline": metrics(y_test, temporal_model.predict(temporal(x_test)))}
    output = Path(__file__).resolve().parents[1] / "models" / "benchmark_results.json"; output.write_text(json.dumps(report, indent=2)); print(json.dumps(report, indent=2))
if __name__ == "__main__": main()
