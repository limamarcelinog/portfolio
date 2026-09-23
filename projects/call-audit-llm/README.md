# Sales call auditing with an LLM

A pipeline that scores recorded sales calls against a fixed rubric and rolls the
results up per rep: **transcript → anchored rubric evaluation → validated JSON →
per-rep aggregate**, with the scorer's own reliability measured and published
alongside the scores.

The model call is the least interesting part. Anyone can ask an LLM to rate a
call out of ten. The engineering is everything that decides whether the number
it returns is allowed to reach a human being.

---

## The problem this is actually solving

A sales manager wants to know which reps need coaching on what. Listening to
every call does not scale; listening to a sample means the sample decides. So
you score them automatically — and immediately hit four failure modes that a
naive implementation walks straight into:

**The model invents its own standard.** Asked to "rate discovery out of 3", it
grades against an internal notion of good that shifts between calls, and worse,
shifts with the *surrounding text* — a mediocre call reads better after a bad
one. The scores are not comparable, which was the entire point.

**The model invents its evidence.** It returns a confident, fluent quote that
justifies the score and does not appear in the transcript. In a dashboard this
is indistinguishable from a real quote until a rep reads their own feedback and
says "I never said that", at which point the system is finished.

**The scorer disagrees with itself.** Score the same call twice and the numbers
move. If nobody measures by how much, a gap between two reps gets reported as a
finding when it is noise.

**The aggregate outruns the data.** Two calls become a rep average, the average
becomes a ranking, and the ranking becomes a performance conversation.

Each of the four has a countermeasure in this repo, and each countermeasure is a
design decision rather than a feature.

---

## Design decisions

### The rubric does the judging, not the model

Every criterion has a **behavioural anchor for each level** — [`rubric/rubric.json`](rubric/rubric.json).
Not "3 = excellent discovery", but:

> **3:** The rep reached mechanism AND consequence, with the prospect stating a
> number, a deadline, or a named business risk in their own words.

This converts the task from judgment into classification. The model is not
asked how good the call was; it is asked which of four described situations
happened. Classification is a far more stable task, and when the standard has to
change, it changes in one JSON file rather than inside a prompt nobody can
diff meaningfully.

The rubric is versioned, and the version is stamped on every score. A score
carried forward across a rubric change is not comparable to a new one, and
without the stamp nobody finds out.

### The rubric generates the contract

[`src/schema.py`](src/schema.py) builds the JSON schema, the system prompt and
the completeness validator from the same `rubric.json`. Adding a criterion
changes all three together. Maintained by hand in three places, they drift, and
the drift surfaces as a scoring bug nobody can reproduce.

### Every score must cite the transcript, and the citation is checked

The structured-output schema guarantees the response parses and has the right
shape. It guarantees nothing about whether the content is true — it will
happily accept a 3 justified by a sentence nobody said.

So [`src/validate.py`](src/validate.py) checks that every `evidence_quote`
actually appears in the source. Normalisation forgives smart quotes,
non-breaking spaces and line wrapping; it does not forgive a changed word,
because a reworded quote is not the quote.

A score that fails grounding is **retried once with the failure stated back**,
and if it fails again the call is **dropped, loudly**. A missing score is
visibly missing. A wrong score that passed no check is invisible, and it is the
one that ends up in a performance review.

### The scorer's noise is measured and published

[`src/reliability.py`](src/reliability.py) scores the same calls N times and
reports, per criterion, the standard deviation, the worst spread, and the exact
agreement rate.

This matters more on current models than it used to: **`temperature` is no
longer a request parameter on this model family**, so run-to-run determinism is
not something you can dial down. Repeated runs will differ. The only
responsible response is to measure the difference and publish it next to the
scores.

That number is the resolution of the instrument. A 0.4 gap between two reps
means nothing if re-scoring the same calls moves the average by 0.4.

### The aggregate refuses to say more than the data supports

[`src/aggregate.py`](src/aggregate.py) applies two guards:

- **A minimum of three calls per rep.** Below it, the rep is reported and
  explicitly not ranked.
- **Pairwise differences are compared against their error bars.** A gap that
  does not clear `2 × combined standard error` is printed as *"inside the error
  bars — not a ranking"*, and a rep whose call-to-call spread has collapsed to
  the measured scoring noise is flagged, because at that point the calls are not
  distinguishable from each other either.

`not_applicable` is a first-class score, not a zero. If no objection came up in
a call, the rep is not penalised for failing to handle one — the criterion is
excluded from the mean instead. Treating an absent situation as a failed one is
the single most common way a rubric average becomes unfair.

---

## Running it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...          # or: ant auth login

python3 src/score.py transcripts/*.md --out results/run.jsonl
python3 src/reliability.py transcripts/rep_a_001.md transcripts/rep_b_001.md --runs 5
python3 src/aggregate.py results/run.jsonl --noise 0.15

python3 tests/test_offline.py         # no API key, no tokens
```

**Model:** `claude-opus-5`, adaptive thinking, effort `medium`, structured
output via `output_config.format`. Server-side refusal fallbacks are enabled —
a policy decline on one transcript should not take down a batch run.

**Estimated cost** (not measured — see below): roughly $0.05 per call scored, so
about $0.40 for all eight, and about $2 for a five-run reliability measurement
across them. For a real deployment the Batch API halves this and call scoring is
not latency-sensitive, which makes it the obvious production path.

---

## What is verified, and what is not

**Verified.** The offline suite runs and passes — 14 tests covering the output
contract, evidence grounding and the aggregation guards:

```
14 passed, 0 failed
```

Those are the parts that decide whether a wrong answer reaches a dashboard, and
they are pure functions, so they are testable without spending a token.

**Not verified.** I have not run the pipeline against the live API — no key was
available on the machine where this was written. So the numbers in the cost
estimate above are arithmetic, not measurement, and `results/` is empty rather
than filled with a sample run I could not produce honestly.

If you clone this and the API path errors, that is a real bug and I would like
to know.

---

## The transcripts are synthetic

All eight in [`transcripts/`](transcripts/) were written by me for this project.
No real call was recorded, transcribed or used, and no company, person or deal
in them exists. They are deliberately uneven — one rep who runs disciplined
discovery, one who pitches through the call, one in between — because a set of
uniformly good calls proves nothing about a scoring system.

The scenario is held constant across all eight (a mid-market retailer evaluating
warehouse inventory software) so that rep behaviour is the only thing that
varies. That is the only way a per-rep comparison means anything.

---

## What I would add next

- **Calibration against human scores.** The pipeline measures whether the model
  agrees with *itself*. It does not measure whether it agrees with a sales
  manager, which is a different and more important question. That needs a gold
  set scored by hand and a Cohen's kappa against it.
- **Drift monitoring.** Rubric version is stamped; model version is stamped. The
  missing piece is alerting when the same gold set starts scoring differently.
