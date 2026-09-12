"""Hash-chained threat genome ledger.

The ledger is blockchain-inspired and deliberately local/offline for this
prototype. It provides tamper-evident sharing-ready threat signatures without
persisting packet payloads, hostnames, or source/destination IP addresses.
"""
import hashlib
import json
import numpy as np
from sqlalchemy.orm import Session
from ..models.prediction import ThreatGenome
from .feature_extractor import FEATURE_NAMES

GENE_INDEXES = [3, 5, 6, 7, 8, 9, 13]  # flags, timing/TTL, payload, SMB signal

def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def signature_for(state):
    genes = {FEATURE_NAMES[i]: round(float(np.asarray(state)[i]), 2) for i in GENE_INDEXES}
    return hashlib.sha256(_canonical(genes).encode()).hexdigest(), genes

def anchor_genome(db: Session, state, stage, confidence):
    signature, summary = signature_for(state)
    existing = db.query(ThreatGenome).filter_by(signature=signature).first()
    if existing: return existing, True
    latest = db.query(ThreatGenome).order_by(ThreatGenome.id.desc()).first()
    previous_hash = latest.record_hash if latest else "GENESIS"
    record_hash = hashlib.sha256(_canonical({"signature": signature, "stage": stage, "confidence": round(float(confidence), 4), "previous_hash": previous_hash}).encode()).hexdigest()
    genome = ThreatGenome(signature=signature, stage=stage, confidence=float(confidence), feature_summary=summary, previous_hash=previous_hash, record_hash=record_hash)
    db.add(genome); db.commit(); db.refresh(genome)
    return genome, False

def reputation(db: Session, state):
    signature, _ = signature_for(state)
    hit = db.query(ThreatGenome).filter_by(signature=signature).first()
    return {"known": bool(hit), "signature": signature[:12], "matched_stage": hit.stage if hit else None, "confidence": hit.confidence if hit else 0.0, "ledger_id": hit.id if hit else None}

def verify_chain(db: Session):
    prior = "GENESIS"
    for record in db.query(ThreatGenome).order_by(ThreatGenome.id):
        expected = hashlib.sha256(_canonical({"signature": record.signature, "stage": record.stage, "confidence": round(float(record.confidence), 4), "previous_hash": prior}).encode()).hexdigest()
        if record.previous_hash != prior or record.record_hash != expected: return False
        prior = record.record_hash
    return True
