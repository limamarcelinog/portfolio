# What I am building next

Four projects, chosen to demonstrate the combination that is actually my profile: data modeling and SQL on one side, commercial reasoning on the other. A pure data engineer builds the pipeline. A pure analyst reads the chart. The work below does both in the same repository.

Three well-documented projects are worth more than ten shallow ones, so this list is deliberately short and will not grow.

---

## 1. End-to-end commercial funnel *(flagship)* — **built**

**→ [projects/funnel-analytics](projects/funnel-analytics/)** — the model and the written diagnosis. The dashboard layer is still open; the gold views are shaped to feed one.

**Data** [Marketing Funnel by Olist](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist) — a public dataset from a real Brazilian company: 8,000 marketing qualified leads and 842 closed deals, with acquisition channel, first-contact date, close date, SDR and sales rep, and business segment.

**What it contains**

- Ingestion into PostgreSQL/Supabase with layered modeling: bronze → silver → gold
- Conversion views by funnel stage, by channel and by cohort, plus time-to-close distribution
- A dashboard over the gold layer
- A README that does not stop at the model: a written diagnosis of **where the funnel leaks and what the leak costs**

**Why this one is the flagship.** Anyone can load a CSV and chart it. The work that distinguishes this is deciding what a "stage" is, what counts as a conversion, at what grain the fact table lives, and then reading the result as a commercial operator rather than as a chart. The diagnosis section is the point of the project — the modeling exists to make the diagnosis trustworthy.

---

## 2. LLM-based sales call auditing — **built**

**→ [projects/call-audit-llm](projects/call-audit-llm/)** — the rubric, the pipeline, the reliability measurement and the aggregation guards. The live API path is written but not yet run.

**Data** Synthetic call transcripts, written by me. No real customer or seller conversation is used.

**Pipeline** transcript → rubric-based evaluation through an LLM API → structured JSON score → aggregation per sales rep.

**What it demonstrates.** An LLM applied to a real operational problem with a structured, auditable output — not a chatbot. The interesting engineering is in the rubric: forcing a language model to return a score that is consistent enough to compare two sellers, and handling the cases where it will not.

---

## 3. Production-grade n8n workflows

**What it contains** Three or four workflows exported as JSON, each built with retry, idempotency (so a replay does not duplicate), error handling, a dead-letter path and logging.

**The README documents the failure each pattern prevents.** That is the part almost nobody publishes. Workflow screenshots are common; a written account of what breaks in production at 3 a.m. and which pattern absorbs it is not.

---

## 4. MCP server over analytical data

An MCP server exposing the metrics from project 1, so that a language model can query the funnel in natural language — "which channel had the worst close rate last quarter, and how much did that cost".

Small to build, and still rare in portfolios. It also closes the loop on the other three: the semantic layer from project 1 becomes the contract the model queries against, which is the same architectural idea I apply professionally.

---

## What I do not publish, and why

This matters more than the list above, so it is written down.

**No company pipelines, metrics or business rules — not even with the data swapped.** The logic is intellectual property, and swapping the data does not change that. Work I have done inside companies appears here as [case studies](case-studies/): the problem, the architecture, the trade-offs and my contribution, with no proprietary code. If you want to go deeper than a case study allows, ask me in an interview and I will walk you through the reasoning.

**No credentials, no customer data, no personal data.** Every project here runs on public datasets or on data I generated.

**No tutorial projects and no forks without contribution.** A Titanic notebook or a to-do list demonstrates that I can follow instructions. That is not the claim I am making.

**No more than four or five projects.** Depth is the signal. Breadth is noise.
