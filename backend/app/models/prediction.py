from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    filename: Mapped[str] = mapped_column(String(255))
    infiltration_probability: Mapped[float] = mapped_column(Float)
    predicted_stage: Mapped[str] = mapped_column(String(80))
    shap_values: Mapped[dict] = mapped_column(JSON)
    digital_twin_result: Mapped[dict] = mapped_column(JSON)
