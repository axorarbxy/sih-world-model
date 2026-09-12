from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .api import routes_predict, routes_history, routes_stream
Base.metadata.create_all(bind=engine)
app = FastAPI(title="SIH World Model Cyber Defense API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(routes_predict.router); app.include_router(routes_history.router); app.include_router(routes_stream.router)
@app.get("/api/health")
def health(): return {"status": "online", "mode": "offline-first"}
