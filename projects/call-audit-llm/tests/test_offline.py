#!/usr/bin/env python3
"""Everything that can be verified without spending a token.

Deliberately covers the guards rather than the API call. The API call is the
part that cannot be tested offline; the guards are the part that decides whether
a wrong answer from it reaches a dashboard, and they are pure functions.

    python3 tests/test_offline.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aggregate import MIN_CALLS, comparisons, per_rep  # noqa: E402
from schema import CallScore, criterion_ids, json_schema, load_rubric  # noqa: E402
from validate import Ungrounded, check_grounded, ungrounded_quotes  # noqa: E402

RUBRIC = load_rubric()
IDS = criterion_ids(RUBRIC)

PASSED, FAILED = [], []


def check(name):
    def wrap(fn):
        try:
            fn()
        except AssertionError as exc:
            FAILED.append((name, str(exc) or "assertion failed"))
        except Exception as exc:  # noqa: BLE001
            FAILED.append((name, f"{type(exc).__name__}: {exc}"))
        else:
            PASSED.append(name)
        return fn
    return wrap


def full_score(overrides: dict | None = None, quote: str = "we lose two days") -> CallScore:
    overrides = overrides or {}
    return CallScore(
        criteria=[
            {
                "criterion_id": cid,
                "score": overrides.get(cid, "2"),
                "evidence_quote": quote,
                "reasoning": "r",
            }
            for cid in IDS
        ],
        coaching_note="n",
        deal_risk="medium",
    )


# --- the output contract ---------------------------------------------------

@check("schema enum is generated from the rubric, not hardcoded")
def _():
    enum = json_schema(RUBRIC)["properties"]["criteria"]["items"]["properties"]["criterion_id"]["enum"]
    assert enum == IDS, enum


@check("a response missing a criterion is rejected")
def _():
    try:
        CallScore(
            criteria=[{"criterion_id": IDS[0], "score": "2", "evidence_quote": "q", "reasoning": "r"}],
            coaching_note="n", deal_risk="low",
        )
    except Exception:
        return
    raise AssertionError("an incomplete response was accepted")


@check("a response scoring the same criterion twice is rejected")
def _():
    dup = [{"criterion_id": IDS[0], "score": "2", "evidence_quote": "q", "reasoning": "r"}] * 2
    dup += [{"criterion_id": c, "score": "2", "evidence_quote": "q", "reasoning": "r"} for c in IDS[1:-1]]
    try:
        CallScore(criteria=dup, coaching_note="n", deal_risk="low")
    except Exception:
        return
    raise AssertionError("a duplicated criterion was accepted")


@check("not_applicable is excluded from the mean, never counted as zero")
def _():
    s = full_score({IDS[0]: "3", IDS[1]: "1", IDS[2]: "not_applicable", IDS[3]: "2", IDS[4]: "2"})
    assert s.mean() == 2.0, s.mean()          # (3+1+2+2)/4, not /5
    zeroed = full_score({IDS[0]: "3", IDS[1]: "1", IDS[2]: "0", IDS[3]: "2", IDS[4]: "2"})
    assert zeroed.mean() == 1.6, zeroed.mean()


# --- evidence grounding ----------------------------------------------------

TRANSCRIPT = "**Dana:** We lose about two days a month, and it's getting worse.\n"


@check("an invented quote is caught")
def _():
    s = full_score(quote="We lose about four days a month")
    bad = ungrounded_quotes(s, TRANSCRIPT)
    assert len(bad) == len(IDS), bad


@check("a real quote passes")
def _():
    check_grounded(full_score(quote="We lose about two days a month"), TRANSCRIPT)


@check("smart quotes and line wrapping are forgiven; wording is not")
def _():
    check_grounded(full_score(quote="We  lose\nabout   two days a month"), TRANSCRIPT)
    try:
        check_grounded(full_score(quote="We lose about two days per month"), TRANSCRIPT)
    except Ungrounded:
        return
    raise AssertionError("a reworded quote was accepted")


@check("an empty quote is not grounding")
def _():
    try:
        check_grounded(full_score(quote=""), TRANSCRIPT)
    except Ungrounded:
        return
    raise AssertionError("an empty quote was accepted")


# --- aggregation guards ----------------------------------------------------

def rows(rep: str, means: list[float]) -> list[dict]:
    out = []
    for i, m in enumerate(means):
        # spread the call mean across criteria so per-criterion rollups exist
        out.append({
            "transcript_id": f"{rep}_{i:03d}", "rep_id": rep, "mean": m,
            "score": {"criteria": [
                {"criterion_id": c, "score": str(int(round(m))), "evidence_quote": "q", "reasoning": "r"}
                for c in IDS
            ]},
        })
    return out


@check(f"a rep below {MIN_CALLS} calls is not ranked")
def _():
    reps = per_rep(rows("rep_c", [2.0, 3.0]))
    assert reps["rep_c"]["rankable"] is False
    assert reps["rep_c"]["calls"] == 2


@check("a difference inside the error bars is not reported as a ranking")
def _():
    data = rows("rep_a", [2.0, 2.4, 1.6]) + rows("rep_b", [1.9, 2.3, 1.5])
    comp = comparisons(per_rep(data), noise_sd=0.15)[0]
    assert comp["difference"] < comp["threshold"], comp
    assert comp["distinguishable"] is False, comp


@check("a difference that clears the error bars is reported")
def _():
    data = rows("rep_a", [2.9, 3.0, 2.95]) + rows("rep_b", [1.0, 1.1, 0.95])
    comp = comparisons(per_rep(data), noise_sd=0.15)[0]
    assert comp["distinguishable"] is True, comp


@check("a rep whose spread sits at the noise floor is flagged")
def _():
    data = rows("rep_a", [2.0, 2.05, 1.95]) + rows("rep_b", [1.0, 1.05, 0.95])
    comp = comparisons(per_rep(data), noise_sd=0.15)[0]
    assert comp["at_noise_floor"] is True, comp


@check("an unranked rep never enters a pairwise comparison")
def _():
    data = rows("rep_a", [2.9, 3.0, 2.95]) + rows("rep_c", [1.0, 1.1])
    assert comparisons(per_rep(data), noise_sd=0.15) == []


@check("scores round-trip through the jsonl score.py writes")
def _():
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        for r in rows("rep_a", [2.0, 2.5, 3.0]):
            fh.write(json.dumps(r) + "\n")
        path = Path(fh.name)
    from aggregate import load
    assert per_rep(load(path))["rep_a"]["calls"] == 3
    path.unlink()


if __name__ == "__main__":
    for name in PASSED:
        print(f"  pass  {name}")
    for name, why in FAILED:
        print(f"  FAIL  {name}\n          {why}")
    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    raise SystemExit(1 if FAILED else 0)
