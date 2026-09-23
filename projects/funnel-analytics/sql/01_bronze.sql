-- =============================================================================
-- BRONZE — source data exactly as it arrived.
--
-- Every column is text, deliberately. Bronze must accept whatever the source
-- emits, including the malformed row, so that ingestion never fails and a bad
-- value stays visible instead of being silently dropped at the door.
-- Casting and judgement happen in silver, where they can be reasoned about.
-- =============================================================================

create schema if not exists bronze;

drop table if exists bronze.marketing_qualified_leads cascade;
create table bronze.marketing_qualified_leads (
    mql_id              text,
    first_contact_date  text,
    landing_page_id     text,
    origin              text,
    _source_file        text        not null default 'olist_marketing_qualified_leads_dataset.csv',
    _ingested_at        timestamptz not null default now()
);

drop table if exists bronze.closed_deals cascade;
create table bronze.closed_deals (
    mql_id                        text,
    seller_id                     text,
    sdr_id                        text,
    sr_id                         text,
    won_date                      text,
    business_segment              text,
    lead_type                     text,
    lead_behaviour_profile        text,
    has_company                   text,
    has_gtin                      text,
    average_stock                 text,
    business_type                 text,
    declared_product_catalog_size text,
    declared_monthly_revenue      text,
    _source_file                  text        not null default 'olist_closed_deals_dataset.csv',
    _ingested_at                  timestamptz not null default now()
);

comment on schema bronze is
    'Source data as received. Text columns only, no constraints, no cleaning.';
