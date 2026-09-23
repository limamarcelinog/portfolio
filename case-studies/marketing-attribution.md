# Multi-channel marketing attribution

**Company** Coders — tech education · built on the platform described in [Revenue data platform](revenue-data-platform.md)
**Role** Revenue Operations
**Stack** PostgreSQL · Supabase · SQL · Meta Ads · Google Ads · LinkedIn Ads · Python

> Work done inside a company system. Source code is proprietary and not published here.

---

## Context

Paid acquisition ran across Meta, Google and LinkedIn simultaneously, plus organic social and referrals. Each platform reports its own conversions, using its own attribution window, counting its own version of a lead. Add them up and you get more customers than the company actually sold.

## The problem

The board's question was simple and unanswerable: **which channel is worth more money next month?**

To answer it, three things had to be true at once, and none of them were:

1. **Ad spend had to meet the funnel at a shared key.** Platform reports end at "lead". The funnel continues for weeks through qualification, scheduling, the sales call and the close. Without joining those, a channel that produces cheap leads that never buy looks better than one that produces expensive leads that do.
2. **Attribution had to be a decision, not a default.** Each platform claims the conversion. Somebody has to decide what the company counts, write that rule down, and apply it consistently.
3. **The grain had to survive down to the creative.** "Meta is working" is not actionable. "This creative, in this campaign, produces leads that book calls at half the rate of the account average" is.

## What I built

**Ingestion and normalization per platform.** Each ad platform's spend, campaign, ad set and creative data lands in the raw layer on its own schedule and in its own vocabulary. Staging normalizes currency, timezone, date grain and naming so that a campaign has one identity regardless of which API described it.

**The join to the funnel.** Acquisition data is tied to the identity-resolved lead from the revenue platform, which means spend can be followed forward through every funnel stage — qualified, scheduled, call held, closed, paid, retained — rather than stopping at the platform's own conversion event.

**An explicit attribution model.** Rather than accepting each platform's self-reported conversions, the model applies one written rule, in SQL, in the trusted layer. Deduplication happens once, centrally, so the sum of channel results equals the company's actual result. When leadership wants to challenge the rule, they challenge one object — not five dashboards.

**Unit economics per channel and per creative.** Cost per lead, cost per qualified lead, cost per scheduled call, cost per acquisition, and conversion rate at every stage — cut by channel, campaign and creative, over any period.

**Lead scoring.** Behavioral and firmographic signals scored at the top of the funnel, so pre-sales works the list in the order most likely to convert rather than in arrival order.

## Why it changes decisions

The useful finding from this kind of model is rarely "channel X is good". It is that **the channel ranking flips depending on how far down the funnel you look**. A channel can win on cost per lead and lose badly on cost per acquisition, because its leads do not show up to calls. Budget conversations stop being about CPL — which is the metric the ad platform optimizes for — and start being about cost per closed customer, which is the metric the business is paid on.

## Prior work on the same problem

This is the third revenue organization where I have built this. At **V4 Company**, as Senior Data Analyst, I consolidated data across Google Ads, Meta Ads and multiple CRMs for a portfolio of client projects, monitoring CPL, conversion rate, ROI and LTV, and supporting A/B test design and post-change impact measurement. As **Head of Growth** there, I used the same models to find operational bottlenecks and run data-led experiments across multiple accounts at once.

## Related

- [Revenue data platform](revenue-data-platform.md) — the funnel model this attaches to
- [Customer health & churn prevention](customer-health-and-churn.md) — what happens after acquisition
