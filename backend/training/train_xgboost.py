import sys; from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import numpy as np
from xgboost import XGBClassifier
from app.config import MODEL_DIR
rng=np.random.default_rng(42); x=rng.normal(0,1,(1500,14)); risk=x[:,3]+x[:,5]+x[:,13]; y=np.clip(((risk-risk.min())/(risk.max()-risk.min())*5).astype(int),0,4)
model=XGBClassifier(n_estimators=80, max_depth=4, objective="multi:softprob", num_class=5); model.fit(x,y); model.save_model(MODEL_DIR / "xgboost_stage.json"); print("saved xgboost_stage.json")
