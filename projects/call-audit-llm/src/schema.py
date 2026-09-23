"""The output contract, built from the rubric rather than written beside it.

Adding a criterion to rubric/rubric.json changes the JSON schema, the system
prompt and the validator together. A contract maintained by hand in three places
drifts, and the drift shows up as a scoring bug nobody can reproduce.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "rubric" / "rubric.json"

Score = Literal["0", "1", "2", "3", "not_applicable"]
DealRisk = Literal["low", "medium", "high"]


def load_rubric() -> dict:
    return json.loads(RUBRIC_PATH.read_text())


def criterion_ids(rubric: dict) -> list[str]:
    return [c["id"] for c in rubric["criteria"]]


# --- what comes back -------------------------------------------------------

class CriterionScore(BaseModel):
    criterion_id: str
    score: Score
    evidence_quote: str = Field(
        description="A verbatim span from the transcript. Checked by validate.py."
    )
    reasoning: str

    @property
    def numeric(self) -> int | None:
        """None means the criterion did not apply, which is NOT the same as zero.

        Averaging a not-applicable as zero punishes a rep for a call where no
        objection happened to come up. It is excluded from the mean instead.
        """
        return None if self.score == "not_applicable" else int(self.score)


class CallScore(BaseModel):
    criteria: list[CriterionScore]
    coaching_note: str
    deal_risk: DealRisk

    @field_validator("criteria")
    @classmethod
    def _exactly_the_rubric(cls, v: list[CriterionScore]) -> list[CriterionScore]:
        expected = set(criterion_ids(load_rubric()))
        got = [c.criterion_id for c in v]
        if len(got) != len(set(got)):
            raise ValueError(f"duplicate criterion in response: {got}")
        if set(got) != expected:
            missing = expected - set(got)
            extra = set(got) - expected
            raise ValueError(f"criteria mismatch (missing={missing or '-'}, extra={extra or '-'})")
        return v

    def mean(self) -> float | None:
        applicable = [c.numeric for c in self.criteria if c.numeric is not None]
        return round(sum(applicable) / len(applicable), 3) if applicable else None


# --- what the API is told to produce ---------------------------------------

def json_schema(rubric: dict) -> dict:
    """The structured-output schema. Guarantees shape, and nothing else.

    Shape validity is not score validity: this schema happily accepts a score of
    3 justified by a quote that never appears in the transcript. That is what
    validate.py is for.
    """
    return {
        "type": "object",
        "properties": {
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion_id": {"type": "string", "enum": criterion_ids(rubric)},
                        "score": {"type": "string", "enum": ["0", "1", "2", "3", "not_applicable"]},
                        "evidence_quote": {"type": "string"},
                        "reasoning": {"type": "string"},
                    },
                    "required": ["criterion_id", "score", "evidence_quote", "reasoning"],
                    "additionalProperties": False,
                },
            },
            "coaching_note": {"type": "string"},
            "deal_risk": {"type": "string", "enum": ["low", "medium", "high"]},
        },
        "required": ["criteria", "coaching_note", "deal_risk"],
        "additionalProperties": False,
    }


def system_prompt(rubric: dict) -> str:
    """Renders the rubric into the prompt so the anchors are the only standard."""
    lines = [
        "You are auditing a recorded B2B sales call against a fixed rubric.",
        "",
        "Score each criterion by selecting the anchor that best matches what happened.",
        "Do not invent a standard of your own, and do not grade on a curve against",
        "other calls — you are not shown other calls. Pick the anchor.",
        "",
        "For every criterion, quote a verbatim span from the transcript as evidence.",
        "The quote must appear in the transcript exactly as written, character for",
        "character. If you cannot find a supporting span, that itself is evidence for",
        "a lower anchor — quote the moment where the thing should have happened.",
        "",
        "Judge only what is in the transcript. Do not assume what happened before or",
        "after the call, and do not credit the rep for intentions they did not voice.",
        "",
        f"RUBRIC {rubric['rubric_id']} v{rubric['version']} — scale {rubric['scale']['min']}–{rubric['scale']['max']}",
    ]
    for c in rubric["criteria"]:
        lines += ["", f"## {c['id']} — {c['name']}", c["question"], ""]
        for level, text in c["anchors"].items():
            label = "not_applicable" if level == "na" else level
            lines.append(f"  {label}: {text}")
    return "\n".join(lines)
