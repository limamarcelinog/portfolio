# Lucreiai

**A unit-economics app for secondhand resellers**
**Stack** React Native 0.81 · Expo SDK 54 · TypeScript · Supabase (PostgreSQL) · TanStack Query · react-hook-form + zod
**Repository** [limamarcelinog/bricks](https://github.com/limamarcelinog/bricks) *(private — available on request)*

---

## The problem

A reseller buys an item for R$120, sells it for R$300, and believes they made R$180.

After the marketplace fee, the shipping they paid minus what the buyer covered, and the cost of refurbishing it, they made R$74. They are running a business on a number that is wrong by 2.4x, and they find out at the end of the month when the bank balance disagrees with the mental arithmetic.

Lucreiai computes the real number.

## The calculation

```
total_cost    = acquisition_cost + Σ extra_costs
net_shipping  = shipping_paid − shipping_charged_to_buyer
real_profit   = sale_price − total_cost − platform_fee − net_shipping
margin        = real_profit / sale_price
ROI           = real_profit / total_cost
```

Beyond profit per item: capital tied up in inventory, turnover in days-to-sell, sell-through rate, inventory aging, and profit broken down by sales channel and category — each over any period.

One level up from per-item profit sit **business expenses** (rent, electricity, internet) and the **monthly result**, which is sales profit minus what was actually paid out. An expense deliberately does not enter an item's profit — rent belongs to no single item, and allocating it there would corrupt the per-item decision the app exists to support. The **monthly target** is measured against the result, and each month keeps its own.

**Batch purchases** — "I took the whole box for R$200" — are allocated across the items. The allocation writes each item's own cost, which means the profit formula never needs a special case for them.

## Engineering decisions worth discussing

**The profit formula exists twice, on purpose, and a test proves they agree.** The app computes profit in TypeScript for instant feedback while the user is still typing; PostgreSQL computes it in a view for reporting. Two implementations of a money calculation is a bug waiting to happen, so `npm run test:paridade` runs both against the same data and compares them **to the cent**. The duplication is a deliberate trade — responsiveness in the UI, authority in the database — and the test is what makes the trade safe rather than reckless.

**The platform fee is frozen at sale time.** Marketplaces change their fee schedules. If the fee were read live, last year's profit would silently change every time a marketplace updated its pricing. The fee that applied at the moment of sale is stored with the sale.

**Margin is a ratio of totals, not an average of ratios.** Averaging per-item margins to get a portfolio margin is a classic error that overweights cheap items. The aggregations sum the numerators and denominators separately, and there is a test that fails if someone "simplifies" it back.

**Tests run against the real database, through the real auth path.** Each suite creates a disposable user, works through an authenticated session with the anon key — the same path the app uses, with row-level security in force — and deletes the user at the end. This catches the class of bug that mocked tests structurally cannot: an RLS policy that silently returns zero rows. The `service_role` key lives in `~/.config/supabase/`, never in the repository, and exists only to create and destroy the test user.

**Twelve test suites, each named for the rule it defends** — profit parity, auth and RLS in both directions, dashboard aggregations, registration atomicity, the stock trigger and frozen fee, editing and sale reversal, referential behavior on delete versus deactivate, batch allocation closing to the cent, channel and category reports reconciling to the dashboard total, period filtering, expenses versus item profit, and monthly targets.

## Why I built it

I wanted a project where the domain logic was genuinely non-trivial, where the correctness of a number mattered to a real person's livelihood, and where I owned every layer — the Postgres schema and its migrations, the row-level security, the domain module, the mobile app and the test strategy. Unit economics is the same problem I solve professionally at company scale, at a size where I could make every architectural decision myself.
