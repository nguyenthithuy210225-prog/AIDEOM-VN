"""Exercise 11: tabular Q-learning for adaptive budget policy."""

from __future__ import annotations

import numpy as np
import pandas as pd


STATES = ["Suy giảm", "Ổn định", "Tăng trưởng", "Rủi ro cao"]
ACTIONS = ["Truyền thống", "Số hóa nhanh", "AI dẫn dắt", "Bao trùm số", "Cân bằng"]

ACTION_SHARES = {
    "Truyền thống": {"K": 0.70, "D": 0.10, "AI": 0.10, "H": 0.10},
    "Số hóa nhanh": {"K": 0.25, "D": 0.45, "AI": 0.15, "H": 0.15},
    "AI dẫn dắt": {"K": 0.20, "D": 0.20, "AI": 0.45, "H": 0.15},
    "Bao trùm số": {"K": 0.30, "D": 0.20, "AI": 0.10, "H": 0.40},
    "Cân bằng": {"K": 0.30, "D": 0.25, "AI": 0.25, "H": 0.20},
}


def _reward(state: int, action: int) -> float:
    shares = ACTION_SHARES[ACTIONS[action]]
    base = 85 * shares["K"] + 105 * shares["D"] + 120 * shares["AI"] + 95 * shares["H"]
    if STATES[state] == "Suy giảm":
        base += 16 * shares["K"] + 10 * shares["H"]
    elif STATES[state] == "Tăng trưởng":
        base += 20 * shares["AI"] + 12 * shares["D"]
    elif STATES[state] == "Rủi ro cao":
        base += 22 * shares["H"] + 14 * shares["D"] - 20 * shares["AI"]
    return float(base)


def _transition(state: int, action: int, rng: np.random.Generator) -> int:
    shares = ACTION_SHARES[ACTIONS[action]]
    improve_prob = 0.18 + 0.22 * shares["D"] + 0.18 * shares["H"]
    risk_prob = 0.08 + 0.22 * shares["AI"] - 0.10 * shares["H"]
    u = rng.random()
    if u < risk_prob:
        return 3
    if u < risk_prob + improve_prob:
        return min(2, state + 1)
    if u > 0.88:
        return max(0, state - 1)
    return state


def train_q_learning(
    episodes: int = 700,
    alpha: float = 0.18,
    gamma: float = 0.90,
    epsilon: float = 0.18,
    seed: int = 42,
) -> dict:
    """Train a small tabular Q-learning policy."""
    rng = np.random.default_rng(seed)
    q = np.zeros((len(STATES), len(ACTIONS)))
    rewards = []
    for _ in range(episodes):
        state = int(rng.integers(0, len(STATES)))
        total = 0.0
        for _step in range(12):
            if rng.random() < epsilon:
                action = int(rng.integers(0, len(ACTIONS)))
            else:
                action = int(q[state].argmax())
            reward = _reward(state, action)
            nxt = _transition(state, action, rng)
            q[state, action] += alpha * (reward + gamma * q[nxt].max() - q[state, action])
            total += reward
            state = nxt
        rewards.append(total)
    q_table = pd.DataFrame(q, index=STATES, columns=ACTIONS)
    policy = pd.DataFrame({"state": STATES, "best_action": [ACTIONS[i] for i in q.argmax(axis=1)], "best_q": q.max(axis=1)})
    reward_trace = pd.DataFrame({"episode": np.arange(1, episodes + 1), "reward": rewards})
    return {"q_table": q_table, "policy": policy, "reward_trace": reward_trace}
