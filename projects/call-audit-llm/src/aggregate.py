"""Rolls call scores up per rep, and refuses to say more than the data supports.

Two guards, both of which exist because the alternative is a number that gets a
person managed on:

  1. A minimum call count. Ranking a rep on two calls is not measurement.
  2. A comparison against the instrument's own noise. If the gap between two
     reps is smaller than the spread you get re-scoring the same calls, the
     ranking is an artefact and is reported as such.

    python3 src/aggregate.py results/run.jsonl --noise 0.15
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

MIN_CALLS = 3


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def per_rep(rows: list[dict]) -> dict:
    by_rep = defaultdict(list)
    for r in rows:
        by_rep[r["rep_id"]].append(r)

    out = {}
    for rep, calls in sorted(by_rep.items()):
        means = [c["mean"] for c in calls if c["mean"] is not None]
        criteria = defaultdict(list)
        for c in calls:
            for crit in c["score"]["criteria"]:
                if crit["score"] != "not_applicable":
                    criteria[crit["criterion_id"]].append(int(crit["score"]))

        n = len(means)
        sd = statistics.pstdev(means) if n > 1 else None
        out[rep] = {
            "calls": n,
            "mean": round(statistics.fmean(means), 3) if means else None,
            "sd": round(sd, 3) if sd is not None else None,
            "standard_error": round(sd / math.sqrt(n), 3) if sd is not None and n else None,
            "rankable": n >= MIN_CALLS,
            "per_criterion": {
                cid: round(statistics.fmean(v), 2) for cid, v in sorted(criteria.items())
            },
        }
    return out


def comparisons(reps: dict, noise_sd: float | None) -> list[dict]:
    """Which pairwise differences survive the error bars."""
    rankable = {k: v for k, v in reps.items() if v["rankable"] and v["mean"] is not None}
    results = []
    for a, b in ((a, b) for a in rankable for b in rankable if a < b):
        ra, rb = rankable[a], rankable[b]
        diff = abs(ra["mean"] - rb["mean"])

        # Observed call-to-call spread already contains the scoring noise, so it
        # is the right basis for the error bar. noise_sd is reported alongside
        # as the floor: when the observed spread collapses to it, the calls are
        # not distinguishable from each other either.
        se_a = ra["standard_error"] or 0.0
        se_b = rb["standard_error"] or 0.0
        combined = math.sqrt(se_a ** 2 + se_b ** 2)
        threshold = 2 * combined

        results.append({
            "pair": f"{a} vs {b}",
            "difference": round(diff, 3),
            "threshold": round(threshold, 3),
            "distinguishable": bool(threshold) and diff > threshold,
            "at_noise_floor": (
                noise_sd is not None
                and ra["sd"] is not None and rb["sd"] is not None
                and max(ra["sd"], rb["sd"]) <= noise_sd
            ),
        })
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scores", type=Path, help="the .jsonl written by score.py")
    ap.add_argument("--noise", type=float, help="scoring_noise_sd from reliability.py")
    args = ap.parse_args()

    reps = per_rep(load(args.scores))

    print(f"{'rep':<10}{'calls':>7}{'mean':>8}{'sd':>8}{'se':>8}  status")
    for rep, m in reps.items():
        status = "" if m["rankable"] else f"below {MIN_CALLS} calls - not ranked"
        print(f"{rep:<10}{m['calls']:>7}{m['mean']!s:>8}{m['sd']!s:>8}{m['standard_error']!s:>8}  {status}")

    print("\nper criterion")
    all_criteria = sorted({c for m in reps.values() for c in m["per_criterion"]})
    print(f"{'rep':<10}" + "".join(f"{c[:14]:>16}" for c in all_criteria))
    for rep, m in reps.items():
        print(f"{rep:<10}" + "".join(f"{m['per_criterion'].get(c, '-')!s:>16}" for c in all_criteria))

    comps = comparisons(reps, args.noise)
    if comps:
        print("\npairwise")
        for c in comps:
            verdict = "real" if c["distinguishable"] else "inside the error bars - not a ranking"
            note = "  (rep spread is at the scoring-noise floor)" if c["at_noise_floor"] else ""
            print(f"  {c['pair']:<22} diff {c['difference']:<7} needs > {c['threshold']:<7} {verdict}{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
