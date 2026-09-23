"""Scores one transcript against the rubric.

    python3 src/score.py transcripts/rep_a_001.md
    python3 src/score.py transcripts/*.md --out results/run.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import anthropic
from pydantic import ValidationError

from schema import CallScore, json_schema, load_rubric, system_prompt
from validate import Ungrounded, check_grounded

MODEL = "claude-opus-5"
MAX_TOKENS = 16_000
EFFORT = "medium"           # see README — measured, not guessed
MAX_ATTEMPTS = 2

# USD per million tokens, claude-opus-5
PRICE_IN, PRICE_OUT = 5.00, 25.00


@dataclass
class Scored:
    transcript_id: str
    rep_id: str
    attempts: int
    score: dict
    mean: float | None
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str
    rubric_version: str


def _rep_id(path: Path) -> str:
    """rep_a_001.md -> rep_a"""
    return "_".join(path.stem.split("_")[:2])


def _call(client: anthropic.Anthropic, rubric: dict, transcript: str, correction: str | None):
    user = f"<transcript>\n{transcript}\n</transcript>"
    if correction:
        # A fresh request rather than a follow-up turn: continuing the
        # conversation would mean replaying thinking blocks under this model's
        # rules, and a repair does not need the failed attempt in context — it
        # needs the instruction that was missed, stated louder.
        user += (
            f"\n\nA previous attempt was rejected: {correction}\n"
            "Every evidence_quote must be copied character for character from "
            "inside the <transcript> block above."
        )
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt(rubric),
        messages=[{"role": "user", "content": user}],
        thinking={"type": "adaptive"},
        output_config={
            "effort": EFFORT,
            "format": {"type": "json_schema", "schema": json_schema(rubric)},
        },
        # A refused request otherwise just stops. Sales transcripts are benign,
        # but a classifier decline on one call should not take down a batch run.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )


def score_transcript(client: anthropic.Anthropic, path: Path, rubric: dict) -> Scored:
    transcript = path.read_text()
    correction, last_error = None, None
    tokens_in = tokens_out = 0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = _call(client, rubric, transcript, correction)
        tokens_in += response.usage.input_tokens
        tokens_out += response.usage.output_tokens

        if response.stop_reason == "refusal":
            raise RuntimeError(
                f"{path.name}: the model and its fallback both declined "
                f"({getattr(response.stop_details, 'category', 'unknown')})"
            )

        text = next(b.text for b in response.content if b.type == "text")
        try:
            parsed = CallScore.model_validate_json(text)
            check_grounded(parsed, transcript)
        except (ValidationError, Ungrounded, json.JSONDecodeError) as exc:
            last_error = str(exc)
            correction = last_error
            continue

        return Scored(
            transcript_id=path.stem,
            rep_id=_rep_id(path),
            attempts=attempt,
            score=parsed.model_dump(),
            mean=parsed.mean(),
            input_tokens=tokens_in,
            output_tokens=tokens_out,
            cost_usd=round(tokens_in / 1e6 * PRICE_IN + tokens_out / 1e6 * PRICE_OUT, 6),
            model=response.model,
            rubric_version=rubric["version"],
        )

    # Deliberately fatal. A score that failed its own validation is worse than a
    # missing score: the missing one is visibly missing.
    raise Ungrounded(f"{path.name}: rejected after {MAX_ATTEMPTS} attempts — {last_error}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripts", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, help="write one JSON object per line")
    args = ap.parse_args()

    rubric = load_rubric()
    client = anthropic.Anthropic()
    results, failures = [], 0

    for path in args.transcripts:
        try:
            scored = score_transcript(client, path, rubric)
        except anthropic.RateLimitError as exc:
            print(f"  rate limited on {path.name}; retry after "
                  f"{exc.response.headers.get('retry-after', '60')}s", file=sys.stderr)
            failures += 1
            continue
        except anthropic.APIStatusError as exc:
            print(f"  API error {exc.status_code} on {path.name}: {exc.message}", file=sys.stderr)
            failures += 1
            continue
        except anthropic.APIConnectionError:
            print(f"  network error on {path.name}", file=sys.stderr)
            failures += 1
            continue
        except (Ungrounded, RuntimeError) as exc:
            print(f"  rejected: {exc}", file=sys.stderr)
            failures += 1
            continue

        results.append(scored)
        retried = "" if scored.attempts == 1 else f"  ({scored.attempts} attempts)"
        print(f"  {scored.transcript_id}  mean {scored.mean}  "
              f"${scored.cost_usd:.4f}{retried}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("".join(json.dumps(asdict(r)) + "\n" for r in results))
        print(f"\nwrote {len(results)} scores to {args.out}")

    total = sum(r.cost_usd for r in results)
    print(f"\n{len(results)} scored, {failures} failed, ${total:.4f} total")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
