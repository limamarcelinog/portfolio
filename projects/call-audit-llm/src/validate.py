"""Semantic validation — the part the API's schema guarantee does not cover.

A structured output guarantees the JSON parses and matches the shape. It says
nothing about whether the content is true. The single highest-value check in a
rubric pipeline is whether the evidence quote actually exists in the source,
because a fluent invented quote is indistinguishable from a real one in a
dashboard, and it is the failure mode that destroys trust in the whole system
the first time a rep notices it.
"""
from __future__ import annotations

import re
import unicodedata

from schema import CallScore


class Ungrounded(ValueError):
    """Raised when a cited quote cannot be found in the transcript."""


def _normalise(text: str) -> str:
    """Forgives formatting, not content.

    Smart quotes, non-breaking spaces and line wrapping differ between the
    transcript and what a model echoes back; none of them change what was said.
    Word content is left alone — if a single word differs, the quote is not the
    quote, and this must fail.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def ungrounded_quotes(score: CallScore, transcript: str) -> list[tuple[str, str]]:
    """Returns (criterion_id, quote) for every quote absent from the transcript."""
    haystack = _normalise(transcript)
    bad = []
    for c in score.criteria:
        needle = _normalise(c.evidence_quote)
        if not needle or needle not in haystack:
            bad.append((c.criterion_id, c.evidence_quote))
    return bad


def check_grounded(score: CallScore, transcript: str) -> None:
    bad = ungrounded_quotes(score, transcript)
    if bad:
        detail = "; ".join(f"{cid}: {q!r}" for cid, q in bad)
        raise Ungrounded(f"{len(bad)} quote(s) not found in transcript — {detail}")
