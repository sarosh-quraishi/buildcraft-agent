"""Harness runner — runs probes against a target and writes a report."""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from harness.probes.s2 import ProbeResult, run_s2_probes
from harness.target import Target


def write_report(results: list[ProbeResult], path: Path) -> None:
    swaps = [r for r in results if r.verdict == "SWAP"]
    lines = [
        f"# Harness Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n## Summary\n",
        f"| Verdict | Count |",
        f"|---------|-------|",
        f"| SWAP    | {len(swaps)} |",
        f"| BENIGN  | {sum(1 for r in results if r.verdict == 'BENIGN')} |",
        f"| BLOCKED | {sum(1 for r in results if r.verdict == 'BLOCKED')} |",
    ]
    if swaps:
        lines += ["\n## SWAP findings\n"]
        for r in swaps:
            lines += [
                f"### {r.category} × {r.scenario} (attempt {r.attempt})",
                f"**Expected:** `{r.expected_fragment}`  ",
                f"**Got:** `{r.captured_command}`  ",
                f"**Payload:** `{r.payload}`  ",
                "",
            ]
    path.write_text("\n".join(lines))
    print(f"\nReport written to {path}")


async def run(target: Target, probes: list[str], only: set[str] | None = None) -> list[ProbeResult]:
    results: list[ProbeResult] = []
    if "s2" in probes:
        results += await run_s2_probes(target, only=only)
    return results
