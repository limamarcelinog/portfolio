# Database engineering system

**A specialist agent system for working safely on a production PostgreSQL database**
**Stack** PostgreSQL · Supabase · SQL · AI agent orchestration
**Repository** Private — the protocol and agent definitions are generalizable; the audits and migrations they produced are company-specific

> For the method itself, the rules and what running it taught me, see the case study: [Database engineering practice](../case-studies/database-engineering-practice.md). This page describes the system as an artifact.

---

## What is in it

**An operating protocol.** One document defining the eight stages every change passes through, the three operating modes and what each permits, the standing rules about schema, cardinality, indexes, keys, row-level security and mass mutations, and the ten-part format every recommendation of consequence must answer.

**Fourteen specialist agent definitions.** Orchestrator, database architect, schema modeler, SQL engineer, query performance, data quality, security & RLS, migration engineer, Supabase specialist, data observability, data lineage, data documentation, business rules, and an independent database reviewer.

**Routing, so the system stays cheap.** The orchestrator determines the minimum set of specialists a task needs and loads only those. A slow query loads the query-performance and SQL engineer agents. A row-level security problem loads security and the Supabase specialist. A schema redesign loads architecture, modeling, lineage, migration and review. Loading all fourteen for every task would make the system expensive and its output vague.

**A session boot sequence.** Before any work: read the operating protocol, the current database summary, the known-risk register and the active-work log — then decide which agents are needed. The risk register is the part that matters most. It is where "this table's `status` column is stale and must not be trusted" lives, and it is the difference between an agent that helps and one that confidently recommends something the team already knows is wrong.

**A living record.** Structured directories for architecture documentation, migrations, audits and reports. Code is the executable state; the documentation is the architectural understanding, and the system treats keeping them in sync as part of the change, not as follow-up work.

## The design idea

The interesting constraint is not what the agents can do. It is what they **cannot** do.

The default mode is read-only, and that is enforced by the mode rather than requested politely. Producing a change and applying a change are different modes with a review gate between them. Execution cannot start until nine artifacts exist — including a rollback and a validation plan, which are precisely the two that get skipped when someone is in a hurry.

The reviewer agent is separate from the author agent for the same reason human code review exists, and it has already earned its place by finding a defect in work I had personally verified as correct.

## Reusability

The protocol and the agent definitions carry no company-specific content — they encode PostgreSQL and Supabase engineering practice, not one company's schema. The context files (database summary, risk register, active work) are the seam where a specific database plugs in. Pointing the system at a different database means rewriting those three files, not the protocol.
