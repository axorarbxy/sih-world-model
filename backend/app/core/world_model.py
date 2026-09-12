import torch
import numpy as np
from torch import nn

class AttentionGRU(nn.Module):
    def __init__(self, features, hidden=64):
        super().__init__()
        self.gru = nn.GRU(features, hidden, batch_first=True)
        # Transformer encoder complements the GRU with long-range temporal
        # dependencies across the network-state sequence.
        layer = nn.TransformerEncoderLayer(d_model=hidden, nhead=4, dim_feedforward=hidden * 2, dropout=.1, batch_first=True)
        self.transformer = nn.TransformerEncoder(layer, num_layers=2)
        self.attn = nn.Linear(hidden, 1); self.head = nn.Linear(hidden, features)
    def forward(self, x):
        recurrent, _ = self.gru(x)
        output = self.transformer(recurrent)
        weights = torch.softmax(self.attn(output).squeeze(-1), dim=1); context = (output * weights.unsqueeze(-1)).sum(1); return self.head(context), weights

class WorldModel:
    def __init__(self, features, weights_path=None):
        self.model = AttentionGRU(features); self.features = features
        if weights_path and weights_path.exists():
            try: self.model.load_state_dict(torch.load(weights_path, map_location="cpu")); self.model.eval()
            except RuntimeError: pass  # Re-train after model architecture upgrades.
        self.model.eval()
    @torch.no_grad()
    def predict_next_k_states(self, history, k=5):
        history = np.asarray(history, dtype=np.float32)
        if history.ndim != 2 or history.shape[1] != self.features:
            raise ValueError(f"history must have shape (windows, {self.features})")
        if len(history) == 0:
            raise ValueError("history must contain at least one network state")
        if k < 1:
            raise ValueError("forecast steps must be positive")
        states = [row.copy() for row in history]; futures = []; attention = []
        for _ in range(k):
            x = torch.from_numpy(np.asarray(states[-8:], dtype=np.float32)).unsqueeze(0)
            nxt, weights = self.model(x); value = nxt.squeeze(0).numpy(); futures.append(value); attention = weights.squeeze(0).tolist(); states.append(value)
        return futures, attention
