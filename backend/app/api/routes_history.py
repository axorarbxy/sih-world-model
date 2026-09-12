from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.prediction import Prediction, ThreatGenome
from ..core.threat_genome import verify_chain
router = APIRouter(prefix="/api", tags=["history"])
@router.get("/history")
def history(db: Session = Depends(get_db)):
    return [{"id": x.id, "timestamp": x.timestamp, "filename": x.filename, "infiltration_probability": x.infiltration_probability, "predicted_stage": x.predicted_stage} for x in db.query(Prediction).order_by(Prediction.timestamp.desc()).limit(50)]

@router.get("/threat-genome")
def threat_genome(db: Session = Depends(get_db)):
    entries = db.query(ThreatGenome).order_by(ThreatGenome.id.desc()).limit(20).all()
    return {"chain_valid": verify_chain(db), "entries": [{"id": x.id, "stage": x.stage, "confidence": x.confidence, "signature": x.signature[:12], "record_hash": x.record_hash[:16], "feature_summary": x.feature_summary} for x in entries]}
