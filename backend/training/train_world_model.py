"""Offline synthetic training, replace synthetic_states with CIC-IDS/CTU feature matrices later."""
import sys; from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import numpy as np, torch
from app.core.world_model import AttentionGRU
from app.config import MODEL_DIR
rng = np.random.default_rng(42); states = rng.normal(0, 1, (800, 14)); states[400:, [3,5,13]] += np.linspace(0, 5, 400)[:,None]
x = torch.tensor(np.stack([states[i:i+8] for i in range(len(states)-8)]), dtype=torch.float32); y = torch.tensor(states[8:], dtype=torch.float32)
model = AttentionGRU(14); opt = torch.optim.Adam(model.parameters(), lr=.003)
for _ in range(30): opt.zero_grad(); prediction, _ = model(x); loss = torch.nn.functional.mse_loss(prediction, y); loss.backward(); opt.step()
torch.save(model.state_dict(), MODEL_DIR / "world_model.pt"); print("saved world_model.pt", float(loss))
