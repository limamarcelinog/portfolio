# Gabriel Lima Marcelino

**Revenue Operations & Data Engineering** · Florianópolis, Brazil · Open to remote and international roles

[Résumé](resume/) · [Case studies](case-studies/) · [Code](projects/) · [LinkedIn](https://www.linkedin.com/in/gabriellimamarcelino) · limamarcelinog@gmail.com

*[Versão em português](README.pt-BR.md)*

---

I build the data infrastructure that revenue teams actually run on — from the raw event a platform emits to the number a director makes a decision with.

Most people in Revenue Operations stop at the report. I own the whole chain: ingestion, data modeling in PostgreSQL, the semantic layer, the dashboards that consume it, and the go-to-market process on the other side. I have also managed the sales squads that use these numbers, which is why I build for the question being asked rather than for the metric that is easy to compute.

---

## What I do

**Revenue data platforms.** Layered modeling (raw → staging → trusted) on PostgreSQL/Supabase, materialized views and RPCs designed for read patterns, caching strategies, and a semantic layer so that one metric has exactly one definition across every team.

**Go-to-market operations.** Funnel modeling from first touch to customer success, multi-channel attribution, commercial KPI definition, commission logic, quota and forecast processes, and the reengagement flows that recover leads the funnel dropped.

**Delivery.** React/TypeScript dashboards for leadership, sales, pre-sales, marketing and CS — because a data platform nobody reads is not finished.

**Engineering discipline on production data.** Read-only by default, explicit impact analysis, migration with rollback and a validation plan before anything is applied. The method is written down: [Database engineering practice](case-studies/database-engineering-practice.md).

---

## Selected work

### Revenue data platform — the system my work is judged by

**[Read the case study →](case-studies/revenue-data-platform.md)**

The commercial data infrastructure of a tech education company. Every lead followed from the ad that produced it, through qualification, scheduling and the sales call, to the enrolled student and their success journey — in one model, with one definition per metric, instead of five teams exporting five versions of the same question.

Layered modeling (raw → staging → trusted) on PostgreSQL/Supabase · identity resolution across five source systems · a semantic layer in SQL · RPC contracts with authorization enforced in the database · fact-day caching · React and TypeScript dashboards for leadership, sales, pre-sales, marketing and customer success.

I own the operating side as well: commercial KPI definitions, commission logic, two sales squads, and the reengagement cadences that turn dormant funnel stages back into pipeline.

*Built inside a company — the code is proprietary. The case study covers the architecture, the trade-offs behind it and my specific contribution.*

### Also

| Case study | What it is |
|---|---|
| [Multi-channel marketing attribution](case-studies/marketing-attribution.md) | Tying Meta, Google and LinkedIn Ads spend to the conversion funnel, down to creative level — one written attribution rule instead of five platforms each claiming the same conversion |
| [Customer health & churn prevention](case-studies/customer-health-and-churn.md) | A health scoring model with a human-correctable score of record, and the internal application that made Customer Success proactive |
| [Database engineering practice](case-studies/database-engineering-practice.md) | How I change a production database without breaking it — the operating protocol I work by, and what running it caught |

---

## Code

Projects I designed and wrote myself, where the repository is mine to share.

| Project | Stack | What it is |
|---|---|---|
| [Lucreiai](projects/lucreiai.md) | React Native · Expo · Supabase · TypeScript | Unit-economics app for secondhand resellers: real profit per item after fees, shipping and refurbishment — not the gross margin people assume |
| [Desperta](projects/desperta.md) | Swift · iOS · AlarmKit · Vision | An alarm that only stops once you physically get up, verified by the camera |
| [Database engineering system](projects/database-engineering-system.md) | PostgreSQL · Supabase · AI agents | A specialist agent system that audits and evolves a production database under a strict operating protocol |

Full index with context: [projects/](projects/)

---

## What I do not publish

No company pipelines, metrics or business rules — not even with the data swapped. The logic is intellectual property, and changing the data does not change that. Work done inside companies appears here as case studies: the problem, the architecture, the trade-offs and my contribution, with no proprietary code. No credentials, no customer data, no tutorial projects.

That is why the case studies above have no repository attached. It is a deliberate choice, and the reasoning is in [the roadmap](roadmap.md#what-i-do-not-publish-and-why), along with [what I am building next](roadmap.md).

---

## Background in one paragraph

Seven years moving from running a business to running the data behind one. I started as a partner and project coordinator in a services company, where I took monthly revenue from R$20k to R$70k and managed a team of 15. I moved into marketing and revenue at V4 Company as Account Manager, then Head of Growth, then Senior Data Analyst — the point where the work stopped being about opinions and started being about queries. Since then: Revenue Operations at Atomic Apps, commercial coordination at Br24 (Bitrix24's highest-impact global partner) and Atomic Group, and now Revenue Operations at Coders, where I own the commercial data infrastructure and lead the data and technology squad.

Full history: [résumé](resume/).

---

## Stack

**Data** PostgreSQL · Supabase · SQL (modeling, window functions, query tuning, RLS) · Python · Power BI
**Application** React · TypeScript · Node.js · React Native / Expo
**Operations** Meta Ads · Google Ads · LinkedIn Ads · CRM and marketing automation · n8n · ClickUp

---

## Contact

- **Email** limamarcelinog@gmail.com
- **LinkedIn** [gabriellimamarcelino](https://www.linkedin.com/in/gabriellimamarcelino)
- **Location** Florianópolis, Santa Catarina, Brazil — available for remote work across time zones
