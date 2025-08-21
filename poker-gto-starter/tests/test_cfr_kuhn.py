
from pokersolver.engine.cfr import CFRTrainer
from pokersolver.games.kuhn import KuhnGame


def test_train_kuhn_runs():
    game = KuhnGame()
    trainer = CFRTrainer(game, algo='cfr+', seed=1)
    trainer.train(iterations=2000)
    avg = trainer.average_strategies()
    assert len(avg) > 0
    # Strategies should be valid distributions
    for strat in avg.values():
        assert abs(sum(strat) - 1.0) < 1e-6
        assert all(0.0 <= x <= 1.0 for x in strat)
