
import argparse
from ...engine.cfr import CFRTrainer
from ...games.kuhn import KuhnGame


def run(argv=None):
    parser = argparse.ArgumentParser(prog='poker-gto solve-kuhn', description='Solve Kuhn Poker with CFR/CFR+')
    parser.add_argument('--iterations', '-n', type=int, default=100000, help='Training iterations (default: 100k)')
    parser.add_argument('--algo', choices=['cfr', 'cfr+'], default='cfr+', help='Algorithm variant (default: cfr+)')
    parser.add_argument('--seed', type=int, default=42, help='RNG seed (default: 42)')
    args = parser.parse_args(argv)

    game = KuhnGame()
    trainer = CFRTrainer(game, algo=args.algo, seed=args.seed)
    trainer.train(iterations=args.iterations)
    avg = trainer.average_strategies()

    print("
Average strategy by infoset (card|history):")
    for key in sorted(avg.keys()):
        strat = avg[key]
        # Map action indices to labels based on history length
        hist = key.split('|', 1)[1]
        if hist in ['', 'c']:
            labels = ['check', 'bet']
        elif hist in ['b', 'cb']:
            labels = ['call', 'fold']
        else:
            labels = [f"a{i}" for i in range(len(strat))]
        parts = ", ".join(f"{lab}={p:.3f}" for lab, p in zip(labels, strat))
        print(f"  {key}: {parts}")
