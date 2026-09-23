-- =============================================================================
-- GOLD — the layer the business reads. One row per lead, one definition per
-- metric, business rules applied exactly once and here.
-- =============================================================================

create schema if not exists gold;

-- The conversion horizon lives in one place. Changing it changes every metric
-- downstream consistently, which is the entire reason it is not hardcoded into
-- each view.
create or replace view gold.params as
    select 90::int as horizon_days;

-- -----------------------------------------------------------------------------
-- The observation window. These three dates govern how the data may be read.
--
--   first_lead_at    when lead capture began
--   first_deal_at    when the commercial operation began CLOSING
--   observed_through the last close we can possibly know about
--
-- first_deal_at is the one that gets forgotten, and it invalidates every cohort
-- before it. See the README.
-- -----------------------------------------------------------------------------
create or replace view gold.observation_window as
    select
        (select min(first_contact_date) from silver.lead) as first_lead_at,
        min(won_at)::date                                 as first_deal_at,
        max(won_at)::date                                 as observed_through
    from silver.deal;

-- -----------------------------------------------------------------------------
-- gold.fact_lead — the grain is one marketing qualified lead. Everything else
-- in this project aggregates from here.
--
--   is_won            closed at any point we can observe (biased — see below)
--   is_won_in_horizon closed within horizon_days of first contact (comparable)
--   horizon_complete  this lead has been observable for the full horizon
--
-- is_won is the number people ask for and the one that misleads: a lead
-- contacted last week has had less time to close than one contacted last year,
-- so comparing them measures elapsed time, not performance. is_won_in_horizon
-- gives every lead the same clock.
-- -----------------------------------------------------------------------------
create or replace view gold.fact_lead as
    select
        l.lead_id,
        l.first_contact_date,
        date_trunc('month', l.first_contact_date)::date      as cohort_month,
        l.origin,
        l.attribution_status,
        l.landing_page_id,
        (d.lead_id is not null)                              as is_won,
        d.won_at,
        (d.won_at::date - l.first_contact_date)              as days_to_close,
        (w.observed_through - l.first_contact_date)          as days_observed,
        ((w.observed_through - l.first_contact_date) >= p.horizon_days)
                                                             as horizon_complete,
        (d.lead_id is not null
            and (d.won_at::date - l.first_contact_date) <= p.horizon_days)
                                                             as is_won_in_horizon,
        d.sdr_id,
        d.sr_id,
        d.business_segment,
        d.lead_type,
        d.business_type
    from silver.lead l
    left join silver.deal d on d.lead_id = l.lead_id
    cross join gold.observation_window w
    cross join gold.params p;

comment on schema gold is
    'Business-readable layer. One documented grain, one definition per metric.';
