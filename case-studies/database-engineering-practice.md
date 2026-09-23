# Database engineering practice

**What it is** The operating protocol I work by when a production database is involved, and the specialist agent system that enforces it
**Stack** PostgreSQL · Supabase · SQL · AI agent orchestration

---

## Why this exists

Most damage to a production database is not caused by a hard problem. It is caused by a reasonable-sounding change applied by someone who understood 80% of the system — an index added by reading a `WHERE` clause, a column type altered without checking the existing values, a policy changed without tracing who depended on it.

I formalized my own practice into a written protocol and a system that refuses to skip steps, because I am the person who would otherwise skip them under deadline pressure.

## The central principle

**Never change before understanding.**

Every piece of work moves through eight stages, and none may be skipped for a change that matters:

```
DISCOVER → UNDERSTAND → DIAGNOSE → DESIGN → REVIEW → EXECUTE → VALIDATE → DOCUMENT
```

## Three operating modes

**Discovery** is the default and it is read-only. `SELECT`, `EXPLAIN`, catalog inspection, schema, indexes, constraints, policies, functions, triggers, dependency analysis, documentation. Writes, DDL and migrations are not merely discouraged here — they are outside the mode.

**Proposal** produces the change without applying it: the SQL, the migration, the index or constraint or policy, the backfill strategy and the rollback. Nothing reaches the database.

**Execution** requires explicit intent to change, and cannot begin until nine artifacts exist: diagnosis, evidence, impact analysis, dependencies, risk assessment, migration, rollback, validation plan, and a review by someone other than the author.

## The rules that cost the most to learn

- Never assume the schema. Query the real structure before recommending anything.
- Never assume cardinality. Measure first.
- Never recommend an index from a `WHERE` clause alone — check volume, selectivity, existing indexes, the execution plan, and the write-side cost.
- Never drop a column without a dependency trace, never alter a type without inspecting the data that exists, never touch a key without mapping the relationships.
- Never change row-level security without a security analysis.
- Never run a mass `UPDATE` or `DELETE` without a row estimate, a validated filter and a path back.

## The analysis format

Every recommendation of consequence answers the same ten questions, in the same order: **Problem · Evidence · Probable cause · Impact · Solution · Risk · Dependencies · Implementation · Rollback · Validation.**

The format is the point. "Evidence" prevents diagnosis by intuition. "Rollback" forces you to discover, before you apply anything, that some changes have no way back — which is usually the moment the plan changes.

## The agent system

The protocol is executed by fourteen specialist agents, routed by an orchestrator that loads only the ones a given task needs — a slow query does not summon the migration engineer:

| | |
|---|---|
| Orchestrator | Routing and minimum viable specialist set |
| Database architect · Schema modeler | Structure and modeling |
| SQL engineer · Query performance | Queries and execution plans |
| Data quality · Data observability · Data lineage | Correctness and traceability |
| Security & RLS · Supabase specialist | Authorization and platform surface |
| Migration engineer · Database reviewer | Change and independent review |
| Business rules · Data documentation | Meaning and the written record |

## What running it actually taught me

The protocol produces audit and incident reports, and two of them are worth naming because they changed how I work:

**An independent reviewer catches what self-verification cannot.** A review agent found a real defect in my own work that I had already verified as correct: the validation test I had written was constructed so that it could not fail. I had checked the change and missed the fact that my check was worthless. Self-review has a blind spot exactly at the place you are most confident.

**A read-only query is not automatically safe.** A `SELECT` with an unbounded series filled the database's temporary disk and caused a production incident. "Read-only" describes what a statement writes, not what it consumes. Every exploratory query now carries a short `statement_timeout`, and unbounded series generation is prohibited.

**Money is measured by running the real function.** When assessing whether a change affected sales commissions, a partial simulation gave the wrong sign. The only valid measurement was executing the actual production function for the actual month, before and after.

## Where the code lives

The protocol and agent definitions are mine and generalizable. The audits, diagnostics and migrations they have produced are specific to a company's production database and are not published. If you want to talk through the method, the reports, or what it caught — I am happy to walk through it in an interview.

## Related

- [Revenue data platform](revenue-data-platform.md) — the production system this protocol protects
- [Customer health & churn prevention](customer-health-and-churn.md) — where scoring rule changes go through it
