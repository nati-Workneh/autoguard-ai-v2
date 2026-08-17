
import numpy as np
import torch
from torch import nn
from sklearn.base import BaseEstimator, ClassifierMixin


class _Net(nn.Module):
    def __init__(self, input_dim, hidden, activation, dropout):
        super().__init__()
        act_cls = {"relu": nn.ReLU, "leaky_relu": nn.LeakyReLU}[activation]
        layers, prev = [], input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), act_cls()]
            if dropout:
                layers.append(nn.Dropout(dropout))
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class TorchMLPClassifier(BaseEstimator, ClassifierMixin):
    """Minimal sklearn-compatible wrapper around a small PyTorch MLP, so it can sit
    inside the same preprocessing Pipeline and be joblib-exported like the classical
    candidates."""

    def __init__(self, hidden=(64,), activation="relu", dropout=0.0, lr=1e-3,
                 epochs=40, batch_size=512, seed=42):
        self.hidden = hidden
        self.activation = activation
        self.dropout = dropout
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.seed = seed

    def fit(self, X, y, X_val=None, y_val=None):
        torch.manual_seed(self.seed)
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32).reshape(-1, 1)
        self.model_ = _Net(X.shape[1], self.hidden, self.activation, self.dropout)
        opt = torch.optim.Adam(self.model_.parameters(), lr=self.lr)
        loss_fn = nn.BCEWithLogitsLoss()
        x_t, y_t = torch.tensor(X), torch.tensor(y)
        n = X.shape[0]
        rng = np.random.default_rng(self.seed)
        self.train_loss_history_, self.val_loss_history_ = [], []
        if X_val is not None:
            xv_t = torch.tensor(np.asarray(X_val, dtype=np.float32))
            yv_t = torch.tensor(np.asarray(y_val, dtype=np.float32).reshape(-1, 1))
        for _ in range(self.epochs):
            self.model_.train()
            order = rng.permutation(n)
            epoch_losses = []
            for start in range(0, n, self.batch_size):
                idx = order[start:start + self.batch_size]
                opt.zero_grad()
                loss = loss_fn(self.model_(x_t[idx]), y_t[idx])
                loss.backward()
                opt.step()
                epoch_losses.append(loss.item())
            self.train_loss_history_.append(float(np.mean(epoch_losses)))
            if X_val is not None:
                self.model_.eval()
                with torch.no_grad():
                    self.val_loss_history_.append(float(loss_fn(self.model_(xv_t), yv_t).item()))
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        self.model_.eval()
        X = np.asarray(X, dtype=np.float32)
        with torch.no_grad():
            logits = self.model_(torch.tensor(X)).numpy().reshape(-1)
        p1 = 1 / (1 + np.exp(-logits))
        return np.column_stack([1 - p1, p1])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
