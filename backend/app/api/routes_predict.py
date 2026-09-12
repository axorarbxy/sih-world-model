from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.prediction import Prediction
from ..config import FORECAST_STEPS, MODEL_DIR, SEQUENCE_LENGTH
from ..core.feature_extractor import extract_features
from ..core.world_model import WorldModel
from ..core.xgboost_stage import StageClassifier
from ..core.digital_twin import simulate_counterfactuals
from ..core.explainability import explain_forecast
from ..core.threat_genome import anchor_genome, reputation

router = APIRouter(prefix="/api", tags=["predictions"])
@router.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        matrix, timestamps, network = extract_features(await file.read(), file.filename or "upload.csv")
        if len(matrix) < 2: raise ValueError("Upload needs at least two traffic windows")
        wm = WorldModel(matrix.shape[1], MODEL_DIR / "world_model.pt"); clf = StageClassifier(MODEL_DIR / "xgboost_stage.json")
        history = matrix[-SEQUENCE_LENGTH:].copy(); futures, attention = wm.predict_next_k_states(history, FORECAST_STEPS)
        timeline = []
        for i, state in enumerate(futures):
            stage, confidence = clf.classify_stage(state); timeline.append({"timestamp": f"forecast +{(i+1)*5}s", "infiltration_probability": round(confidence if stage == "Exfiltration" else confidence * .45, 3), "predicted_stage": stage})
        explanations = [explain_forecast(history if i == 0 else history[-7:].tolist() + futures[:i], state, attention) for i, state in enumerate(futures)]
        explanation = explanations[0]; twin = simulate_counterfactuals(history, wm, clf)
        genome, duplicate = anchor_genome(db, matrix[-1], timeline[-1]["predicted_stage"], timeline[-1]["infiltration_probability"])
        genome_status = reputation(db, matrix[-1]); genome_status.update({"anchored": not duplicate, "record_hash": genome.record_hash[:16]})
        record = Prediction(filename=file.filename or "upload", infiltration_probability=timeline[-1]["infiltration_probability"], predicted_stage=timeline[-1]["predicted_stage"], shap_values=explanation, digital_twin_result=twin); db.add(record); db.commit()
        return {"timeline": timeline, "shap_values": explanation, "explanations": explanations, "digital_twin": twin, "threat_genome": genome_status, "network": network}
    except Exception as exc: raise HTTPException(400, str(exc))
