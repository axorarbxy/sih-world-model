from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.prediction import Prediction
router = APIRouter(prefix="/api", tags=["history"])
@router.get("/history")
def history(db: Session = Depends(get_db)):
    return [{"id": x.id, "timestamp": x.timestamp, "filename": x.filename, "infiltration_probability": x.infiltration_probability, "predicted_stage": x.predicted_stage} for x in db.query(Prediction).order_by(Prediction.timestamp.desc()).limit(50)]
