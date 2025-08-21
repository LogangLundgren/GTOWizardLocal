# poker-gto (starter)

A minimal **Python** foundation for a GTO solver project. Starts with a 
**CFR/CFR+ toy solver for Kuhn Poker**, a tiny game that's perfect for validating the engine. 

> Roadmap: Kuhn → Leduc → HU NLH preflop abstraction → postflop abstractions.

## Quick start

```bash
# from repo root
python -m pokersolver.cli.main solve-kuhn --iterations 200000 --algo cfr+

# or, if installed as a package
poker-gto solve-kuhn --iterations 200000 --algo cfr+
```

You’ll see average strategies by information set (e.g., `J:`, `Q:`, `K:` with histories).

## Project layout
```
src/
  pokersolver/
    engine/
      cfr.py           # CFR / CFR+ core
    games/
      kuhn.py          # Kuhn Poker game model
    cli/
      main.py          # Argparse-based CLI
      commands/
        solve_kuhn.py  # CLI command implementation

tests/
  test_cfr_kuhn.py     # Sanity tests for convergence/valid strategy
```

## Design notes
- **Algorithm**: CFR and CFR+ options. CFR+ keeps regrets non-negative and uses linear averaging.
- **Infoset**: `card|history`, where `history` is a string of actions like `""`, `"c"`, `"b"`, `"cb"`, etc.
- **Actions**: `c`(check/call), `b`(bet), `f`(fold). Kuhn has a single betting round with one bet allowed.
- **No external deps** for this toy setup.

## Next steps
- Implement **Leduc Hold’em** under `games/` for richer validation.
- Add **best-response** computation to estimate exploitability.
- Introduce **CSV export** for average strategies and a simple **range heatmap** view later.
- Abstract `Game` interface so CFR works across games with minimal glue.
```
