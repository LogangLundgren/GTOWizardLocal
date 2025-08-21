
import argparse
from .commands import solve_kuhn


def main():
    parser = argparse.ArgumentParser(prog='poker-gto', description='Poker GTO CLI (starter)')
    subparsers = parser.add_subparsers(dest='command')

    # We don't parse here; we delegate to command modules so they can be called directly too.
    subparsers.add_parser('solve-kuhn', help='Solve Kuhn Poker with CFR/CFR+')

    args, extra = parser.parse_known_args()

    if args.command == 'solve-kuhn':
        solve_kuhn.run(extra)
    else:
        parser.print_help()
