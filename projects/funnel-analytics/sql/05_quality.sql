-- =============================================================================
-- QUALITY — assertions about the data, expressed as queries.
--
-- Run: select * from quality.results order by passed, check_name;
--
-- One of these checks FAILS on the published dataset, on purpose. A suite that
-- has never caught anything is a suite nobody has tested. See the README.
-- =============================================================================

create schema if not exists quality;

create or replace view quality.results as

    select
        'leads: no row lost between bronze and silver'::text as check_name,
        (select count(*) from bronze.marketing_qualified_leads)
            = (select count(*) from silver.lead)             as passed,
        format('bronze %s, silver %s',
            (select count(*) from bronze.marketing_qualified_leads),
            (select count(*) from silver.lead))::text        as detail

    union all
    select
        'deals: no row lost between bronze and silver',
        (select count(*) from bronze.closed_deals)
            = (select count(*) from silver.deal),
        format('bronze %s, silver %s',
            (select count(*) from bronze.closed_deals),
            (select count(*) from silver.deal))

    union all
    select
        'lead id is unique in the source',
        not exists (
            select 1 from bronze.marketing_qualified_leads
            group by mql_id having count(*) > 1),
        format('%s duplicated ids', (
            select count(*) from (
                select 1 from bronze.marketing_qualified_leads
                group by mql_id having count(*) > 1) x))

    union all
    select
        'every deal traces back to a lead',
        not exists (
            select 1
            from bronze.closed_deals d
            left join bronze.marketing_qualified_leads l on l.mql_id = d.mql_id
            where l.mql_id is null),
        format('%s orphan deals', (
            select count(*)
            from bronze.closed_deals d
            left join bronze.marketing_qualified_leads l on l.mql_id = d.mql_id
            where l.mql_id is null))

    union all
    select
        'a deal never closes before its lead exists',
        not exists (select 1 from gold.fact_lead where days_to_close < 0),
        format('%s deals with a close date earlier than first contact', (
            select count(*) from gold.fact_lead where days_to_close < 0))

    union all
    select
        'origin stays inside the known domain',
        not exists (
            select 1 from silver.lead
            where origin not in (
                'organic_search', 'paid_search', 'social', 'unknown',
                'direct_traffic', 'email', 'referral', 'other',
                'display', 'other_publicities', 'not_informed')),
        format('%s unexpected values', (
            select count(distinct origin) from silver.lead
            where origin not in (
                'organic_search', 'paid_search', 'social', 'unknown',
                'direct_traffic', 'email', 'referral', 'other',
                'display', 'other_publicities', 'not_informed')))

    union all
    select
        'every cohort is fully observed at the horizon',
        not exists (select 1 from gold.fact_lead where not horizon_complete),
        format('%s leads not yet observable for the full %s-day horizon',
            (select count(*) from gold.fact_lead where not horizon_complete),
            (select horizon_days from gold.params));

comment on view quality.results is
    'Data quality assertions. Expect one documented failure on this dataset.';
