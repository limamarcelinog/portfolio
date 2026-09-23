#!/usr/bin/env bash
# Downloads the public dataset and builds every layer, from nothing, in order.
# Idempotent: re-running rebuilds the whole pipeline from bronze.
#
#   DATABASE_URL=postgresql://... ./ingest/load.sh
set -euo pipefail

: "${DATABASE_URL:?set DATABASE_URL to your Postgres/Supabase connection string}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data"
URL="https://www.kaggle.com/api/v1/datasets/download/olistbr/marketing-funnel-olist"

LEADS="$DATA/olist_marketing_qualified_leads_dataset.csv"
DEALS="$DATA/olist_closed_deals_dataset.csv"

if [ ! -f "$LEADS" ] || [ ! -f "$DEALS" ]; then
    echo "==> downloading dataset"
    mkdir -p "$DATA"
    curl -sSL --fail -o "$DATA/olist.zip" "$URL"
    unzip -oq "$DATA/olist.zip" -d "$DATA"
    rm -f "$DATA/olist.zip"
fi

echo "==> bronze"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f "$ROOT/sql/01_bronze.sql"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -c \
    "\copy bronze.marketing_qualified_leads(mql_id,first_contact_date,landing_page_id,origin) from '$LEADS' with (format csv, header true)"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -c \
    "\copy bronze.closed_deals(mql_id,seller_id,sdr_id,sr_id,won_date,business_segment,lead_type,lead_behaviour_profile,has_company,has_gtin,average_stock,business_type,declared_product_catalog_size,declared_monthly_revenue) from '$DEALS' with (format csv, header true)"

for f in 02_silver 03_gold 04_analysis 05_quality; do
    echo "==> $f"
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f "$ROOT/sql/$f.sql"
done

echo
echo "==> quality"
psql "$DATABASE_URL" -c "select passed, check_name, detail from quality.results order by passed, check_name;"
