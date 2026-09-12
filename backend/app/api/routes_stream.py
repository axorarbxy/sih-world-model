import asyncio, json, numpy as np
from fastapi import APIRouter, WebSocket
from ..core.xgboost_stage import StageClassifier
router = APIRouter(tags=["stream"])
@router.websocket("/ws/stream")
async def stream(ws: WebSocket):
    await ws.accept(); clf = StageClassifier(); state = np.zeros(14)
    try:
        while True:
            try: payload = await asyncio.wait_for(ws.receive_text(), timeout=2); state = np.array(json.loads(payload).get("state", state), dtype=float)
            except asyncio.TimeoutError: state += np.random.normal(0, .08, 14)
            stage, confidence = clf.classify_stage(state); await ws.send_json({"predicted_stage": stage, "infiltration_probability": confidence if stage == "Exfiltration" else confidence*.45})
    except Exception: await ws.close()
