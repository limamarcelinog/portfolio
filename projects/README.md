# Code

Projects I designed and wrote myself.

| Project | Stack | What it is |
|---|---|---|
| [**Commercial funnel — modeling and diagnosis**](funnel-analytics/) | PostgreSQL · SQL · Python | A layered model (bronze → silver → gold) over a real company's public funnel data, and a written diagnosis of where the funnel leaks: 23% of leads converting below baseline, 14.5% unattributable and converting twice as well as the rest, and a time series that cannot be read as a trend because the sales team did not exist for its first six months |
| [Lucreiai](lucreiai.md) | React Native · Expo · TypeScript · Supabase | A unit-economics app for secondhand resellers. Real profit per item after platform fees, shipping and refurbishment — with a test suite that proves the TypeScript and PostgreSQL implementations of the profit formula agree to the cent |
| [Desperta](desperta.md) | Swift · iOS · AlarmKit · Vision | An alarm that rings with the native Clock's authority and stops only after a physical mission the camera verifies. Domain logic in a separate Swift package, tested without a device |
| [Database engineering system](database-engineering-system.md) | PostgreSQL · Supabase · AI agents | A fourteen-specialist agent system that audits and evolves a production database under a protocol where read-only is the default and execution requires nine artifacts |

### On repository access

These repositories are currently private. I am happy to grant access on request, or to walk through any of them in an interview — email limamarcelinog@gmail.com.

For systems built inside companies, where the code is proprietary and cannot be shared, see the [case studies](../case-studies/) instead.
