# SIH World Model — Predictive Cyber Defense

Offline-first SIH26153 prototype that converts five-second traffic windows into network state vectors, forecasts future vectors with a hybrid GRU–Temporal Transformer and attention, and compares a baseline future to a Digital Twin mitigation future.

## Run on Windows

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python training\train_world_model.py
python training\train_xgboost.py
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, then upload a CIC-IDS style CSV or PCAP. Scapy reads PCAP directly; on Windows, install Npcap only if live packet capture is later added—offline file reading requires no capture driver.

## Architecture

- `feature_extractor`: five-second flow/packet aggregates, standardized to a state vector.
- `world_model`: hybrid GRU–Temporal Transformer plus attention predicts the next state vector (not merely an attack label).
- `xgboost_stage`: maps each predicted state to a MITRE ATT&CK stage.
- `digital_twin`: evaluates no-action and `block_port_445` trajectories and recommends mitigation when exfiltration risk declines.
- `explainability`: returns ranked state deltas plus learned attention weights. The production SHAP dependency is included for swapping in DeepExplainer after training with representative background states.
- `threat_genome`: a privacy-preserving, hash-chained ledger of derived malicious flow signatures. It stores no IP addresses or packet payloads and makes intelligence records tamper-evident for later federation.

## Demonstration storyline

1. Upload `backend/data/sample_network_traffic.csv`.
2. Point to the forecast/MITRE trajectory and click a forecast point to display its feature drivers.
3. Compare the two Digital Twin futures and present the minimum mitigation recommendation.
4. Show the **Adaptive Threat Genome** panel: it anchors only a derived feature signature, demonstrating shareable threat intelligence without raw traffic disclosure.

Run `docker compose up --build` for the optional container workflow.
