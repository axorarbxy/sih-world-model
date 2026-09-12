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

router = APIRouter(prefix="/api", tags=["predictions"])
@router.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        matrix, timestamps = extract_features(await file.read(), file.filename or "upload.csv")
        if len(matrix) < 2: raise ValueError("Upload needs at least two traffic windows")
        wm = WorldModel(matrix.shape[1], MODEL_DIR / "world_model.pt"); clf = StageClassifier(MODEL_DIR / "xgboost_stage.json")
        history = matrix[-SEQUENCE_LENGTH:].copy(); futures, attention = wm.predict_next_k_states(history, FORECAST_STEPS)
        timeline = []
        for i, state in enumerate(futures):
            stage, confidence = clf.classify_stage(state); timeline.append({"timestamp": f"forecast +{(i+1)*5}s", "infiltration_probability": round(confidence if stage == "Exfiltration" else confidence * .45, 3), "predicted_stage": stage})
        explanation = explain_forecast(history, futures[0], attention); twin = simulate_counterfactuals(history, wm, clf)
        record = Prediction(filename=file.filename or "upload", infiltration_probability=timeline[-1]["infiltration_probability"], predicted_stage=timeline[-1]["predicted_stage"], shap_values=explanation, digital_twin_result=twin); db.add(record); db.commit()
        return {"timeline": timeline, "shap_values": explanation, "digital_twin": twin, "network": {"nodes": [], "edges": []}}
    except Exception as exc: raise HTTPException(400, str(exc))
