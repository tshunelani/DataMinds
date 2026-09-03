from __future__ import annotations
from collections import defaultdict
import math, random

class ReinforcementLearner:
    """Tiny contextual bandit: operators get rewards from observed latency/cost deltas."""
    def __init__(self):
        self.stats = defaultdict(lambda: {"n": 0, "reward": 0.0})

    def choose(self, operators: list[str], epsilon: float = 0.2) -> str:
        if not operators:
            raise ValueError("No operators")
        if random.random() < epsilon:
            return random.choice(operators)
        def score(op):
            s = self.stats[op]
            return s["reward"] / s["n"] if s["n"] else 0.0
        return max(operators, key=score)

    def update(self, operator: str, reward: float):
        s = self.stats[operator]
        s["n"] += 1
        s["reward"] += reward

    def snapshot(self):
        return {k: {"trials": v["n"], "mean_reward": (v["reward"] / v["n"] if v["n"] else 0)} for k,v in self.stats.items()}
