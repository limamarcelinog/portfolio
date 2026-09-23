-- =============================================================================
-- ANALYSIS — the views that answer the questions in the README.
-- All of them read gold.fact_lead. None of them redefine a metric.
-- =============================================================================

-- Conversion by acquisition channel, on the fixed horizon.
create or replace view gold.conversion_by_channel as
    select
        origin,
        attribution_status,
        count(*)                                                                as leads,
        count(*) filter (where is_won_in_horizon)                               as won,
        round(100.0 * count(*) filter (where is_won_in_horizon) / count(*), 1)  as conversion_pct,
        percentile_cont(0.5) within group (order by days_to_close)
            filter (where is_won_in_horizon)                                    as median_days_to_close
    from gold.fact_lead
    where horizon_complete
    group by origin, attribution_status
    order by leads desc;

-- Conversion by cohort, showing the raw number next to the comparable one.
-- before_first_deal marks the cohorts that predate the closing operation: their
-- conversion measures when the sales team started, not how good the leads were.
create or replace view gold.conversion_by_cohort as
    select
        f.cohort_month,
        count(*)                                                                    as leads,
        count(*) filter (where f.is_won)                                            as won_ever,
        round(100.0 * count(*) filter (where f.is_won) / count(*), 1)               as conversion_raw_pct,
        count(*) filter (where f.is_won_in_horizon)                                 as won_in_horizon,
        round(100.0 * count(*) filter (where f.is_won_in_horizon) / count(*), 1)    as conversion_horizon_pct,
        (f.cohort_month < date_trunc('month', w.first_deal_at)::date)               as before_first_deal
    from gold.fact_lead f
    cross join gold.observation_window w
    group by f.cohort_month, w.first_deal_at
    order by f.cohort_month;

-- How long a deal takes. The gap between p50 and p90 is what makes a fixed
-- horizon necessary in the first place.
create or replace view gold.time_to_close as
    select
        count(*)                                                        as deals,
        percentile_cont(0.50) within group (order by days_to_close)     as p50_days,
        percentile_cont(0.75) within group (order by days_to_close)     as p75_days,
        percentile_cont(0.90) within group (order by days_to_close)     as p90_days,
        max(days_to_close)                                              as max_days
    from gold.fact_lead
    where is_won;

-- How much of the funnel cannot be attributed to a channel, and how it performs.
create or replace view gold.attribution_gap as
    select
        attribution_status,
        count(*)                                                                as leads,
        round(100.0 * count(*) / sum(count(*)) over (), 1)                      as pct_of_leads,
        count(*) filter (where is_won_in_horizon)                               as won,
        round(100.0 * count(*) filter (where is_won_in_horizon) / count(*), 1)  as conversion_pct
    from gold.fact_lead
    where horizon_complete
    group by attribution_status
    order by leads desc;

-- The cost view: deals a channel did not produce, measured against how every
-- OTHER named channel performed. Excluding the channel from its own baseline
-- matters — a large underperformer drags down the average it is judged by.
create or replace view gold.channel_leak as
    with per_channel as (
        select
            origin,
            count(*)                                    as leads,
            count(*) filter (where is_won_in_horizon)   as won
        from gold.fact_lead
        where horizon_complete
          and attribution_status = 'named'
        group by origin
    ),
    total as (
        select sum(leads) as leads, sum(won) as won from per_channel
    )
    select
        p.origin,
        p.leads,
        p.won,
        round(100.0 * p.won / p.leads, 1)                                       as conversion_pct,
        round(100.0 * (t.won - p.won) / (t.leads - p.leads), 1)                 as baseline_excl_self_pct,
        round(p.leads * (t.won - p.won)::numeric / (t.leads - p.leads) - p.won) as deals_foregone
    from per_channel p
    cross join total t
    where p.leads >= 100
    order by deals_foregone desc;
