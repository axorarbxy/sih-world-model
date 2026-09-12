import torch
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
    @torch.no_grad()
    def predict_next_k_states(self, history, k=5):
        states = list(history.copy()); futures = []; attention = []
        for _ in range(k):
            x = torch.tensor(states[-8:], dtype=torch.float32).unsqueeze(0)
            nxt, weights = self.model(x); value = nxt.squeeze(0).numpy(); futures.append(value); attention = weights.squeeze(0).tolist(); states.append(value)
        return futures, attention
