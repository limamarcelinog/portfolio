# Commercial funnel — modeling and diagnosis

A layered PostgreSQL model over a public dataset of a real Brazilian company's sales funnel, and a written diagnosis of **where the funnel leaks and what the leak costs**.

The model exists to make the diagnosis trustworthy. The diagnosis is the point.

**Data** [Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist) — 8,000 marketing qualified leads and 842 closed deals, June 2017 to November 2018, with acquisition channel, first-contact date, close date, SDR, sales rep and business segment.

---

## The diagnosis

All conversion figures use a **fixed 90-day horizon**: a lead counts as converted only if it closed within 90 days of first contact. The reason is in [Why a fixed horizon](#why-a-fixed-horizon) — the raw numbers are not comparable and the difference is large enough to reverse conclusions.

### 1. Nearly a quarter of the funnel converts below baseline

| channel | leads | won | conversion | baseline (excl. self) | deals foregone |
|---|---:|---:|---:|---:|---:|
| social | 1,350 | 59 | **4.4%** | 8.5% | **55** |
| email | 493 | 12 | **2.4%** | 8.0% | **28** |
| other | 150 | 4 | 2.7% | 7.8% | 8 |
| display | 118 | 6 | 5.1% | 7.7% | 3 |
| referral | 284 | 21 | 7.4% | 7.7% | 1 |
| direct_traffic | 499 | 50 | 10.0% | 7.5% | −13 |
| paid_search | 1,586 | 150 | 9.5% | 7.1% | −37 |
| organic_search | 2,296 | 218 | 9.5% | 6.7% | −64 |

**Social and email together are 1,843 leads — 23% of every lead in the dataset — and produced 83 fewer deals than the same volume would have at the rate every other channel managed.** Across the eleven and a half months of lead capture, that is one lost deal every four days, concentrated in two channels.

Social is the expensive one, because it is also big. It is the third-largest source of leads and converts at half the baseline. And it is slow: a social lead that does close takes a median of **20 days**, against 10 for organic and paid search. Twice the wait for half the outcome.

Each channel is measured against how *every other* named channel performed, not against the overall average. This matters here: social is large enough that including it in its own baseline would lower the bar it is judged against and understate the gap.

### 2. The best-performing segment of the funnel cannot be invested in

| attribution | leads | share | conversion |
|---|---:|---:|---:|
| named channel | 6,841 | 85.5% | 7.6% |
| `unknown` | 1,099 | 13.7% | **14.3%** |
| not informed | 60 | 0.8% | **20.0%** |

**1,159 leads — 14.5% of the funnel — have no usable channel, and they convert at roughly twice the rate of the leads that do.**

This is the most actionable finding in the dataset and the easiest to miss, because it looks like a data problem rather than a commercial one. It is both. Something is producing the company's best leads, and nobody can say what it is, so nobody can spend more on it. The fix is not analytical — it is instrumentation.

Note that `unknown` and *not informed* are modeled separately and never merged. `unknown` means the source system classified the origin as unknown; *not informed* means nothing arrived at all. They convert differently (14.3% against 20.0%), and averaging them together would erase the distinction between a tracking gap and a pipeline gap.

### 3. The time series cannot be read as a trend

| cohort | leads | raw conversion | 90-day conversion | closing operation existed |
|---|---:|---:|---:|---|
| 2017-06 | 4 | 0.0% | 0.0% | no |
| 2017-07 | 239 | 0.8% | 0.0% | no |
| 2017-08 | 386 | 2.3% | 0.0% | no |
| 2017-09 | 312 | 2.2% | 0.0% | no |
| 2017-10 | 416 | 3.4% | 0.0% | no |
| 2017-11 | 445 | 4.0% | 1.8% | no |
| 2017-12 | 200 | 5.5% | 3.0% | yes |
| 2018-01 | 1,141 | 13.3% | 11.3% | yes |
| 2018-02 | 1,028 | 14.5% | 12.5% | yes |
| 2018-03 | 1,174 | 14.2% | 12.0% | yes |
| 2018-04 | 1,352 | 13.5% | 12.6% | yes |
| 2018-05 | 1,303 | 10.0% | 8.4% | yes |

**The first lead was contacted on 2017-06-14. The first deal closed on 2017-12-05.** For nearly six months the company captured leads while no closing operation existed.

Every cohort before December 2017 therefore reports a conversion rate that measures *when the sales team started*, not how good the leads were. Plotted as a single series it produces a beautiful upward curve that a stakeholder will read as "marketing is improving" and that means nothing of the sort. The honest series starts at 2018-01, and from there conversion is flat at 11–13% until May 2018, which drops to 8.4%.

That May drop is the only real movement in the whole series, and it is the one a naive chart buries inside the ramp.

### What this costs in money — and why I am not going to tell you

The dataset carries `declared_monthly_revenue`, and it is unusable: **95% of rows are zero and the maximum is 50,000,000**, self-declared at sign-up and never validated. There is no spend data either.

So the leak is quantified in deals, not currency. Converting it takes two numbers this dataset does not have — cost per lead by channel, and average contract value. With those, the arithmetic is one multiplication, and the model is already at the right grain to accept them.

Publishing a revenue figure derived from a field that is 95% zero would produce a more impressive README and a wrong number. The column is loaded into silver for completeness and excluded from every metric, with the reason written at the point of exclusion.

---

## Why a fixed horizon

| deals | p50 | p75 | p90 | max |
|---:|---:|---:|---:|---:|
| 842 | 14 days | 55 days | 162 days | 427 days |

Half of all deals close within two weeks. The slowest ten percent take more than five months, and one took over a year.

With a tail that long, "conversion rate" is not a property of a cohort — it is a property of how long you have been watching it. A lead contacted in May 2018 has had less opportunity to close than one contacted in January, so comparing their raw rates measures elapsed time. The fixed horizon gives every lead the same clock.

The observation window makes this tractable: the last lead was contacted on 2018-05-31 and the last close observed is 2018-11-14, which leaves 167 days of observation for even the newest cohort. **A 90-day horizon is fully observable for 100% of the data** — `quality.results` asserts exactly that, so the assumption fails loudly if the dataset is ever extended.

The horizon lives in `gold.params` as a single value. Changing it changes every metric consistently, which is why it is not written into each view.

---

## Running it

```bash
DATABASE_URL=postgresql://... ./ingest/load.sh
```

The script downloads the dataset, builds bronze → silver → gold → analysis → quality in order, and prints the quality results. It is idempotent: re-running rebuilds the whole pipeline from bronze.

```bash
python3 tests/expected.py     # the independent reference implementation
```

---

## The model

```
CSV ──▶ bronze ──▶ silver ──▶ gold ──▶ analysis views
```

**`bronze`** — the source exactly as it arrived. Every column is text, deliberately, so ingestion accepts the malformed row rather than failing at the door or silently dropping it. No casts, no cleaning, no opinions.

**`silver`** — typed and constrained, one row per business entity. The primary keys, the foreign key from deal to lead and the unique constraint on seller are assertions: they hold in this source, and they exist so that the load fails here if that ever changes, instead of producing a quietly wrong number three layers downstream.

**`gold`** — the layer a human reads. `gold.fact_lead` is the single grain — one row per marketing qualified lead — and every analysis view aggregates from it. No view redefines a metric.

**`quality`** — assertions expressed as queries, in `quality.results`.

| file | what it builds |
|---|---|
| [`sql/01_bronze.sql`](sql/01_bronze.sql) | landing tables, all text |
| [`sql/02_silver.sql`](sql/02_silver.sql) | typed tables, constraints, the attribution split |
| [`sql/03_gold.sql`](sql/03_gold.sql) | `params`, `observation_window`, `fact_lead` |
| [`sql/04_analysis.sql`](sql/04_analysis.sql) | the five views behind the diagnosis |
| [`sql/05_quality.sql`](sql/05_quality.sql) | the assertions |

---

## Verification

`sql/` and [`tests/expected.py`](tests/expected.py) are two independent implementations of the same definitions — one in SQL, one in plain Python straight off the CSVs. [`tests/expected-results.md`](tests/expected-results.md) records what every gold view must return.

If the two disagree, one is wrong and the difference points at which. This is the only check that does not consist of asking the pipeline whether it agrees with itself.

**Current status: the SQL has not been executed against a live PostgreSQL instance.** The numbers published above come from the Python reference implementation, which runs. I am not going to claim a green pipeline I have not watched run — if you clone this and `load.sh` errors, that is a real bug and I would like to know.

---

## One quality check fails, on purpose

```
FAIL  a deal never closes before its lead exists
      1 deal with a close date earlier than first contact
```

One row in the source has `won_date` before `first_contact_date`. It is left failing rather than filtered away, because a suite that has never caught anything is a suite nobody has tested, and because silently repairing a source defect is how a pipeline starts lying.

The correct handling depends on a decision the data cannot make: quarantine the row, correct it against a system of record, or accept it as a known defect. In a real engagement that is a conversation with whoever owns the CRM. Here it stays visible.

---

## What this dataset cannot answer

Worth stating, because a portfolio project that pretends its data is complete is not demonstrating judgment:

- **No spend.** Cost per lead, CAC and ROAS are not computable. Every efficiency claim above is in deals, not currency.
- **No deal value.** `declared_monthly_revenue` is 95% zero.
- **No intermediate funnel stages.** The dataset jumps from MQL to won. Real stage-by-stage conversion — contacted, qualified, meeting held, proposal — is not in it.
- **No lead cost by channel**, so "social is expensive" here means expensive in foregone deals, not in media spend.

---

## Data

Marketing Funnel by Olist, published on Kaggle under CC BY-NC-SA 4.0. The dataset is downloaded by `ingest/load.sh` and is not redistributed in this repository.
