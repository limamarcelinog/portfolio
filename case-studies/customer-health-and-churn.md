# Customer health & churn prevention

**Company** Coders — tech education
**Role** Revenue Operations — data model, scoring rules and the internal application
**Stack** PostgreSQL · Supabase (dedicated schema, RPC-only access) · React 18 · TypeScript · Vite · TanStack Query

> Work done inside a company system. Source code is proprietary and not published here.

---

## Context

In education, revenue is not won at the sale. A student who disengages in month two becomes a refund request, a bad review and a lost referral. Customer Success knew this, and had roughly the information needed to act — spread across the learning platform, the support tool, the CRM and the memory of whoever ran the last call.

## The problem

CS was reactive by construction. Intervention happened when a student complained or asked for a refund, which is the point at which intervention is expensive and usually too late. The team needed to know **who to call today**, ranked, with the reason attached.

Two traps make health scoring fail in practice:

1. **A score nobody trusts is a score nobody uses.** If the number is a black box, CS overrides it with instinct and the system becomes decoration.
2. **A score with no owner drifts.** If nobody can correct it when it is wrong about a specific student, it stays wrong, and trust is lost permanently.

## What I built

**A dedicated schema with a strict access contract.** The health domain lives in its own schema, and the application reaches it **only through RPCs** — never raw SQL, never direct table access, never the shared public schema. Every call has a named contract and the authorization rule is enforced in the database. That contract is what let the frontend stay thin and the rules stay reviewable.

**Two scores, deliberately unequal.** The model computes a *suggested* score from behavioral signals, and an *effective* score that is the truth of record. The suggested score is prioritization only — it orders the queue, and it is always labeled as a suggestion. The effective score is what drives risk classification and color. A human can correct the effective score, and the correction is attributed and kept.

This separation is the design decision the whole system rests on. It gives the automated model room to be useful without letting it be wrong in a way nobody can fix, and it preserves the audit trail of who decided what.

**Red flags split by origin.** Commercial red flags — what was promised during the sale — and CS red flags — what is happening during delivery — are modeled and displayed separately, never summed into one number. They imply completely different interventions, and collapsing them destroys the signal. A student flagged because the sale over-promised needs an expectations conversation; a student flagged for absence needs a different call entirely.

**The internal application.** A six-screen React/TypeScript app: the prioritized queue, student detail with score history and the reason for each signal, red flag management, and the views CS leadership uses to see the portfolio as a whole. Every screen handles loading, error and empty states explicitly — an internal tool that shows a blank panel when a query fails is a tool the team stops opening.

**Ingestion from the platform.** Engagement and attendance data flows from the learning platform into the model on a schedule, so the queue reflects the current week rather than the last manual export.

## Why the architecture choices matter

The constraint that the frontend may only call RPCs looks restrictive until the rules change — and in a scoring system, the rules change constantly. Because every rule lives in the database behind a named contract, a change to how a signal is weighted is a database change with a migration and a rollback, applied once, immediately true everywhere. Had the logic lived in the React app, each rule change would have been a deploy, a cache invalidation, and a period where two versions of the truth were in production at once.

## Related

- [Revenue data platform](revenue-data-platform.md) — the funnel that delivers these customers
- [Database engineering practice](database-engineering-practice.md) — how rule changes reach production
