-- =============================================================================
-- SILVER — typed, constrained, and honest about what is missing.
--
-- The constraints below are assertions, not decoration. If the source ever
-- violates one, the load fails here rather than producing a quietly wrong
-- number three layers downstream.
-- =============================================================================

create schema if not exists silver;

drop table if exists silver.deal cascade;
drop table if exists silver.lead cascade;

-- -----------------------------------------------------------------------------
-- silver.lead — one row per marketing qualified lead.
--
-- MODELLING DECISION: 'unknown' and an empty origin are NOT the same thing and
-- are never merged.
--   'unknown'      the source system classified the origin as unknown
--   'not_informed' the source sent us nothing at all
-- They behave differently (see tests/expected-results.md), and collapsing them
-- would hide a tracking defect behind an average.
-- -----------------------------------------------------------------------------
create table silver.lead (
    lead_id             text primary key,
    first_contact_date  date not null,
    landing_page_id     text,
    origin              text not null,
    attribution_status  text not null
        check (attribution_status in ('named', 'unknown', 'not_informed'))
);

insert into silver.lead (lead_id, first_contact_date, landing_page_id, origin, attribution_status)
select
    mql_id,
    first_contact_date::date,
    nullif(landing_page_id, ''),
    coalesce(nullif(origin, ''), 'not_informed'),
    case
        when coalesce(origin, '') = '' then 'not_informed'
        when origin = 'unknown'        then 'unknown'
        else                                'named'
    end
from bronze.marketing_qualified_leads;

-- -----------------------------------------------------------------------------
-- silver.deal — one row per closed deal, keyed by the lead that produced it.
--
-- The foreign key asserts that every deal traces back to a lead, and the unique
-- constraint on seller_id asserts that a seller is won once. Both hold in this
-- source; the constraints exist so that we find out immediately if that changes.
-- -----------------------------------------------------------------------------
create table silver.deal (
    lead_id                       text primary key references silver.lead (lead_id),
    seller_id                     text not null unique,
    sdr_id                        text,
    sr_id                         text,
    won_at                        timestamp not null,
    business_segment              text,
    lead_type                     text,
    lead_behaviour_profile        text,
    business_type                 text,
    has_company                   boolean,
    has_gtin                      boolean,
    average_stock                 text,
    declared_product_catalog_size numeric,
    -- NOT a business value: 95% of rows are zero and the maximum is 50,000,000.
    -- Self-declared at sign-up and never validated. Kept for completeness,
    -- excluded from every metric downstream.
    declared_monthly_revenue      numeric
);

insert into silver.deal (
    lead_id, seller_id, sdr_id, sr_id, won_at,
    business_segment, lead_type, lead_behaviour_profile, business_type,
    has_company, has_gtin, average_stock,
    declared_product_catalog_size, declared_monthly_revenue
)
select
    mql_id,
    seller_id,
    nullif(sdr_id, ''),
    nullif(sr_id, ''),
    won_date::timestamp,
    nullif(business_segment, ''),
    nullif(lead_type, ''),
    nullif(lead_behaviour_profile, ''),
    nullif(business_type, ''),
    case lower(nullif(has_company, '')) when 'true' then true when 'false' then false end,
    case lower(nullif(has_gtin, ''))    when 'true' then true when 'false' then false end,
    nullif(average_stock, ''),
    nullif(declared_product_catalog_size, '')::numeric,
    nullif(declared_monthly_revenue, '')::numeric
from bronze.closed_deals;

create index on silver.lead (first_contact_date);
create index on silver.lead (origin);
create index on silver.deal (won_at);

comment on schema silver is
    'Typed and constrained. One row per business entity, missing data made explicit.';
