"""CLI entry point for the security harness.

Usage:
    python -m harness                          # run all S2 probes against buildcraft
    python -m harness --probe s2               # explicit probe selection
    python -m harness --category append_injection  # single category
    PROBE_BUDGET=1 python -m harness           # fast smoke test
"""
import argparse
import asyncio
import tempfile
from pathlib import Path

from harness.adapters import BuildcraftTarget
from harness.runner import run, write_report


def main():
    parser = argparse.ArgumentParser(description="Agent security harness")
    parser.add_argument("--probe", default="s2", help="Probe to run (default: s2)")
    parser.add_argument("--category", default=None, help="Limit to one attack category")
    parser.add_argument("--report", default="harness_report.md", help="Output report path")
    args = parser.parse_args()

    only = {args.category} if args.category else None

    with tempfile.TemporaryDirectory() as tmp:
        target = BuildcraftTarget(Path(tmp))
        results = asyncio.run(run(target, probes=[args.probe], only=only))
        write_report(results, Path(args.report))

        swaps = [r for r in results if r.verdict == "SWAP"]
        if swaps:
            print(f"\n{len(swaps)} SWAP(s) found — see {args.report}")
        else:
            print("\nNo swaps found.")


if __name__ == "__main__":
    main()
