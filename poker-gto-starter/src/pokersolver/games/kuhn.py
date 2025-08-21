
from __future__ import annotations
from typing import Tuple, List, Dict
import itertools

# Kuhn Poker implementation (2 players, deck J,Q,K). Ante 1, single bet allowed.
# Histories encoded as dict with: {'deal': (p0_card, p1_card), 'seq': str}
# Actions: 0 -> check/call ('c'), 1 -> bet ('b') or fold ('f') depending on context

CARDS = ['J', 'Q', 'K']
CARD_RANK = {c: i for i, c in enumerate(CARDS)}

class KuhnGame:
    def __init__(self):
        pass

    def deals(self):
        # All ordered deals without replacement
        for p0, p1 in itertools.permutations(CARDS, 2):
            yield (p0, p1)

    def initial_history(self, deal: Tuple[str, str]):
        return {'deal': deal, 'seq': ''}

    def current_player(self, history) -> int:
        # Player 0 acts first, then alternate until terminal
        seq = history['seq']
        return 0 if len(seq) % 2 == 0 else 1

    def is_terminal(self, history) -> bool:
        seq = history['seq']
        # Terminal if: 'cc' (showdown), 'bc' (call -> showdown), 'bf' (fold), 'cbf' (bet after check then fold), 'cbc' (call)
        return seq in ('cc', 'bc', 'bf', 'cbf', 'cbc')

    def terminal_utility(self, history) -> float:
        # Utility for current player perspective in CFR recursion is handled via sign flip.
        # Here return payoff for player who just acted? Simpler: return payoff for player to act next (current_player),
        # but CFR handles sign by negating on recursion, so we return payoff for player 0.
        seq = history['seq']
        p0, p1 = history['deal']
        pot = 2  # antes
        # Bets add +1 to pot, loser pays 1 more in call cases.
        if seq == 'bf':
            # P0 bet, P1 folded -> P0 wins pot + bet = 3; net +1 for P0 relative to antes (each anted 1)
            return 1.0
        if seq == 'cbf':
            # P0 checked, P1 bet, P0 folded -> P1 wins; for P0 it's -1
            return -1.0
        # Showdowns
        if seq == 'cc':
            return 1.0 if CARD_RANK[p0] > CARD_RANK[p1] else -1.0
        if seq == 'bc':
            # P0 bet, P1 called. Pot = 4; winner gets +2 over even split -> +2 for P0 if wins, else -2
            return 2.0 if CARD_RANK[p0] > CARD_RANK[p1] else -2.0
        if seq == 'cbc':
            # P0 checked, P1 bet, P0 called. Pot = 4
            return 2.0 if CARD_RANK[p0] > CARD_RANK[p1] else -2.0
        raise ValueError(f"Unexpected terminal seq: {seq}")

    def legal_actions(self, history) -> List[int]:
        seq = history['seq']
        # Start: actions are check (0) or bet (1)
        if seq == '':
            return [0, 1]
        if seq == 'c':  # after check by P0, P1 can check or bet
            return [0, 1]
        if seq == 'b':  # after bet by P0, P1 can call (0) or fold (1)
            return [0, 1]
        if seq == 'cb':  # after check then bet, P0 can call (0) or fold (1)
            return [0, 1]
        return []

    def next_history(self, history, action_index: int):
        seq = history['seq']
        if seq == '':
            action = 'c' if action_index == 0 else 'b'
        elif seq == 'c':
            action = 'c' if action_index == 0 else 'b'
        elif seq == 'b':
            action = 'c' if action_index == 0 else 'f'
        elif seq == 'cb':
            action = 'c' if action_index == 0 else 'f'
        else:
            raise ValueError(f"Illegal action from seq {seq}")
        return {'deal': history['deal'], 'seq': seq + action}

    def infoset_key(self, history) -> Tuple[str, int]:
        # Key = (private card for player to act) + '|' + public sequence
        p = self.current_player(history)
        card = history['deal'][p]
        key = f"{card}|{history['seq']}"
        return key, len(self.legal_actions(history))
