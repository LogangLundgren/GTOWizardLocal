
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional
import random

@dataclass
class Infoset:
    key: str
    num_actions: int
    regret_sum: List[float] = field(default_factory=list)
    strategy_sum: List[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.regret_sum:
            self.regret_sum = [0.0] * self.num_actions
        if not self.strategy_sum:
            self.strategy_sum = [0.0] * self.num_actions

    def get_strategy(self, reach_prob: float, algo: str = 'cfr') -> List[float]:
        """Compute the current strategy via regret-matching (or RM+ for CFR+)."""
        if algo == 'cfr+':
            # Use positive regrets only
            positive_regrets = [max(r, 0.0) for r in self.regret_sum]
            normalizing_sum = sum(positive_regrets)
            if normalizing_sum > 0:
                strategy = [r / normalizing_sum for r in positive_regrets]
            else:
                strategy = [1.0 / self.num_actions] * self.num_actions
        else:
            normalizing_sum = sum([r if r > 0 else 0.0 for r in self.regret_sum])
            if normalizing_sum > 0:
                strategy = [(r if r > 0 else 0.0) / normalizing_sum for r in self.regret_sum]
            else:
                strategy = [1.0 / self.num_actions] * self.num_actions
        # Accumulate strategy
        for i in range(self.num_actions):
            self.strategy_sum[i] += reach_prob * strategy[i]
        return strategy

    def get_average_strategy(self) -> List[float]:
        normalizing_sum = sum(self.strategy_sum)
        if normalizing_sum > 0:
            return [s / normalizing_sum for s in self.strategy_sum]
        return [1.0 / self.num_actions] * self.num_actions


class CFRTrainer:
    def __init__(self, game, algo: str = 'cfr+', seed: Optional[int] = None):
        self.game = game
        self.algo = algo
        self.infosets: Dict[str, Infoset] = {}
        if seed is not None:
            random.seed(seed)

    def train(self, iterations: int = 100000):
        """Train CFR/CFR+ over many iterations by iterating over all private deals."""
        for t in range(1, iterations + 1):
            # Linear averaging weight for CFR+
            weight = t if self.algo == 'cfr+' else 1.0
            for deal in self.game.deals():
                self._cfr(self.game.initial_history(deal), reach=(1.0, 1.0), weight=weight)

    def _cfr(self, history, reach: Tuple[float, float], weight: float) -> float:
        if self.game.is_terminal(history):
            return self.game.terminal_utility(history)

        player = self.game.current_player(history)
        infoset_key, num_actions = self.game.infoset_key(history)
        node = self.infosets.get(infoset_key)
        if node is None:
            node = Infoset(infoset_key, num_actions)
            self.infosets[infoset_key] = node

        strategy = node.get_strategy(reach[player], algo=self.algo)
        action_utils = [0.0] * num_actions
        util = 0.0
        for a in range(num_actions):
            next_hist = self.game.next_history(history, a)
            next_reach = list(reach)
            next_reach[player] *= strategy[a]
            action_utils[a] = - self._cfr(next_hist, tuple(next_reach), weight)
            util += strategy[a] * action_utils[a]

        # Regret update
        for a in range(num_actions):
            regret = action_utils[a] - util
            if self.algo == 'cfr+':
                node.regret_sum[a] = max(0.0, node.regret_sum[a] + regret)
            else:
                node.regret_sum[a] += regret
        # Strategy averaging: add with weight for CFR+
        for a in range(num_actions):
            node.strategy_sum[a] += weight * (reach[1 - player]) * strategy[a]

        return util

    def average_strategies(self) -> Dict[str, List[float]]:
        return {k: v.get_average_strategy() for k, v in self.infosets.items()}

