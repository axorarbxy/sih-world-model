import torch
from torch import nn

class AttentionGRU(nn.Module):
    def __init__(self, features, hidden=64):
        super().__init__(); self.gru = nn.GRU(features, hidden, batch_first=True); self.attn = nn.Linear(hidden, 1); self.head = nn.Linear(hidden, features)
    def forward(self, x):
        output, _ = self.gru(x); weights = torch.softmax(self.attn(output).squeeze(-1), dim=1); context = (output * weights.unsqueeze(-1)).sum(1); return self.head(context), weights

class WorldModel:
    def __init__(self, features, weights_path=None):
        self.model = AttentionGRU(features); self.features = features
        if weights_path and weights_path.exists(): self.model.load_state_dict(torch.load(weights_path, map_location="cpu")); self.model.eval()
    @torch.no_grad()
    def predict_next_k_states(self, history, k=5):
        states = list(history.copy()); futures = []; attention = []
        for _ in range(k):
            x = torch.tensor(states[-8:], dtype=torch.float32).unsqueeze(0)
            nxt, weights = self.model(x); value = nxt.squeeze(0).numpy(); futures.append(value); attention = weights.squeeze(0).tolist(); states.append(value)
        return futures, attention
