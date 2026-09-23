"""Measures how much the scorer disagrees with itself.

The question this answers: if you score the same call twice, do you get the same
number? On this model family `temperature` no longer exists as a request
parameter, so determinism is not something you can dial in — repeated runs will
differ, and the only responsible move is to measure by how much and publish it.

That figure is not trivia. It is the resolution of the instrument. A half-point
gap between two reps means nothing if scoring the same call twice moves it by
half a point, and reporting that gap to the reps anyway is how a scoring system
loses its credibility permanently.

    python3 src/reliability.py transcripts/rep_a_001.md --runs 5
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import anthropic

from schema import load_rubric
from score import score_transcript


def measure(paths: list[Path], runs: int) -> dict:
    client = anthropic.Anthropic()
    rubric = load_rubric()

    per_criterion: dict[str, list[list[int]]] = defaultdict(list)
    per_call_means: list[list[float]] = []
    cost = 0.0

    for path in paths:
        means, criterion_runs = [], defaultdict(list)
        for _ in range(runs):
            scored = score_transcript(client, path, rubric)
            cost += scored.cost_usd
            means.append(scored.mean)
            for c in scored.score["criteria"]:
                if c["score"] != "not_applicable":
                    criterion_runs[c["criterion_id"]].append(int(c["score"]))
        per_call_means.append(means)
        for cid, values in criterion_runs.items():
            per_criterion[cid].append(values)
        print(f"  {path.stem}: {means}")

    criteria = {}
    for cid, calls in per_criterion.items():
        sds = [statistics.pstdev(v) for v in calls if len(v) > 1]
        exact = [len(set(v)) == 1 for v in calls]
        criteria[cid] = {
            "mean_sd": round(statistics.fmean(sds), 3) if sds else 0.0,
            "max_spread": max((max(v) - min(v)) for v in calls),
            "exact_agreement_rate": round(sum(exact) / len(exact), 3),
        }

    call_sds = [statistics.pstdev(m) for m in per_call_means if len(m) > 1]
    noise_sd = round(statistics.fmean(call_sds), 3) if call_sds else 0.0

    return {
        "runs_per_call": runs,
        "calls": len(paths),
        "scoring_noise_sd": noise_sd,
        "per_criterion": criteria,
        "cost_usd": round(cost, 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripts", nargs="+", type=Path)
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    print(f"scoring {len(args.transcripts)} call(s) x {args.runs} runs")
    result = measure(args.transcripts, args.runs)

    print(f"\nscoring noise (sd of the call mean across runs): {result['scoring_noise_sd']}")
    print(f"{'criterion':<24}{'mean sd':>9}{'max spread':>12}{'exact agree':>13}")
    for cid, m in sorted(result["per_criterion"].items(), key=lambda kv: -kv[1]["mean_sd"]):
        print(f"{cid:<24}{m['mean_sd']:>9}{m['max_spread']:>12}{m['exact_agreement_rate']:>13}")
    print(f"\ncost ${result['cost_usd']}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
