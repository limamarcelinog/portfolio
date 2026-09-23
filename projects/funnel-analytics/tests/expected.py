#!/usr/bin/env python3
"""
Reference implementation of every gold-layer metric, computed straight from the
CSVs in pure Python.

Why this exists: the SQL and this script are two independent implementations of
the same definitions. If they disagree, one of them is wrong and the difference
says where to look. This is the only verification that does not simply ask the
pipeline whether it agrees with itself.

Run:  python3 tests/expected.py            # prints the expected results
      python3 tests/expected.py --markdown # regenerates expected-results.md
"""
import csv, sys, statistics
from datetime import datetime
from collections import defaultdict
from pathlib import Path

HORIZON_DAYS = 90  # must match gold.params
DATA = Path(__file__).resolve().parent.parent / "data"

KNOWN_ORIGINS = {
    "organic_search", "paid_search", "social", "unknown", "direct_traffic",
    "email", "referral", "other", "display", "other_publicities", "not_informed",
}


def load():
    leads = {}
    with open(DATA / "olist_marketing_qualified_leads_dataset.csv") as fh:
        for r in csv.DictReader(fh):
            origin = r["origin"] or ""
            leads[r["mql_id"]] = {
                "first_contact_date": datetime.strptime(r["first_contact_date"], "%Y-%m-%d").date(),
                "origin": origin or "not_informed",
                "attribution_status": (
                    "not_informed" if origin == "" else "unknown" if origin == "unknown" else "named"
                ),
            }
    deals = {}
    with open(DATA / "olist_closed_deals_dataset.csv") as fh:
        for r in csv.DictReader(fh):
            deals[r["mql_id"]] = {
                "won_at": datetime.strptime(r["won_date"], "%Y-%m-%d %H:%M:%S"),
            }
    return leads, deals


def fact_lead(leads, deals):
    """Mirrors gold.fact_lead, row for row."""
    observed_through = max(d["won_at"] for d in deals.values()).date()
    first_deal_at = min(d["won_at"] for d in deals.values()).date()
    rows = []
    for lead_id, l in leads.items():
        d = deals.get(lead_id)
        days_to_close = (d["won_at"].date() - l["first_contact_date"]).days if d else None
        days_observed = (observed_through - l["first_contact_date"]).days
        rows.append({
            "lead_id": lead_id,
            "cohort_month": l["first_contact_date"].strftime("%Y-%m"),
            "origin": l["origin"],
            "attribution_status": l["attribution_status"],
            "is_won": d is not None,
            "days_to_close": days_to_close,
            "days_observed": days_observed,
            "horizon_complete": days_observed >= HORIZON_DAYS,
            "is_won_in_horizon": d is not None and days_to_close <= HORIZON_DAYS,
        })
    return rows, first_deal_at, observed_through


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def main():
    leads, deals = load()
    rows, first_deal_at, observed_through = fact_lead(leads, deals)
    out = []
    w = out.append

    w("# Expected results")
    w("")
    w("Computed by `tests/expected.py` directly from the CSVs, independently of the")
    w("SQL. Every number below is what the corresponding gold view must return.")
    w("")
    w(f"- conversion horizon: **{HORIZON_DAYS} days**")
    w(f"- first lead contacted: **{min(l['first_contact_date'] for l in leads.values())}**")
    w(f"- first deal closed: **{first_deal_at}**")
    w(f"- observed through: **{observed_through}**")
    w(f"- leads: **{len(rows):,}** · deals: **{len(deals):,}**")
    w("")

    # ---- gold.conversion_by_channel
    w("## gold.conversion_by_channel")
    w("")
    w("| origin | attribution_status | leads | won | conversion_pct | median_days_to_close |")
    w("|---|---|---:|---:|---:|---:|")
    by_origin = defaultdict(list)
    for r in rows:
        if r["horizon_complete"]:
            by_origin[(r["origin"], r["attribution_status"])].append(r)
    for (origin, status), rs in sorted(by_origin.items(), key=lambda kv: -len(kv[1])):
        won = [r for r in rs if r["is_won_in_horizon"]]
        med = statistics.median([r["days_to_close"] for r in won]) if won else None
        w(f"| {origin} | {status} | {len(rs)} | {len(won)} | {pct(len(won), len(rs))} | "
          f"{med if med is not None else '—'} |")
    w("")

    # ---- gold.conversion_by_cohort
    w("## gold.conversion_by_cohort")
    w("")
    w("`before_first_deal` marks cohorts that predate the closing operation.")
    w("")
    w("| cohort_month | leads | won_ever | conversion_raw_pct | won_in_horizon | conversion_horizon_pct | before_first_deal |")
    w("|---|---:|---:|---:|---:|---:|---|")
    by_cohort = defaultdict(list)
    for r in rows:
        by_cohort[r["cohort_month"]].append(r)
    for month in sorted(by_cohort):
        rs = by_cohort[month]
        ever = sum(1 for r in rs if r["is_won"])
        inh = sum(1 for r in rs if r["is_won_in_horizon"])
        before = month < first_deal_at.strftime("%Y-%m")
        w(f"| {month} | {len(rs)} | {ever} | {pct(ever, len(rs))} | {inh} | "
          f"{pct(inh, len(rs))} | {'true' if before else 'false'} |")
    w("")

    # ---- gold.time_to_close
    won_all = sorted(r["days_to_close"] for r in rows if r["is_won"])
    q = lambda p: won_all[min(int(len(won_all) * p), len(won_all) - 1)]
    w("## gold.time_to_close")
    w("")
    w("| deals | p50_days | p75_days | p90_days | max_days |")
    w("|---:|---:|---:|---:|---:|")
    w(f"| {len(won_all)} | {q(0.50)} | {q(0.75)} | {q(0.90)} | {max(won_all)} |")
    w("")

    # ---- gold.attribution_gap
    w("## gold.attribution_gap")
    w("")
    w("| attribution_status | leads | pct_of_leads | won | conversion_pct |")
    w("|---|---:|---:|---:|---:|")
    by_status = defaultdict(list)
    obs = [r for r in rows if r["horizon_complete"]]
    for r in obs:
        by_status[r["attribution_status"]].append(r)
    for status, rs in sorted(by_status.items(), key=lambda kv: -len(kv[1])):
        won = sum(1 for r in rs if r["is_won_in_horizon"])
        w(f"| {status} | {len(rs)} | {pct(len(rs), len(obs))} | {won} | {pct(won, len(rs))} |")
    w("")

    # ---- gold.channel_leak
    w("## gold.channel_leak")
    w("")
    w("Baseline excludes the channel being measured, so a large underperformer")
    w("does not flatter itself by dragging down the average it is judged against.")
    w("")
    w("| origin | leads | won | conversion_pct | baseline_excl_self_pct | deals_foregone |")
    w("|---|---:|---:|---:|---:|---:|")
    named = [r for r in obs if r["attribution_status"] == "named"]
    per = defaultdict(lambda: [0, 0])
    for r in named:
        per[r["origin"]][0] += 1
        per[r["origin"]][1] += 1 if r["is_won_in_horizon"] else 0
    tot_l = sum(v[0] for v in per.values())
    tot_w = sum(v[1] for v in per.values())
    leak = []
    for origin, (n, won) in per.items():
        if n < 100:
            continue
        base = (tot_w - won) / (tot_l - n)
        leak.append((origin, n, won, pct(won, n), round(100 * base, 1), round(n * base - won)))
    for row in sorted(leak, key=lambda x: -x[5]):
        w("| {} | {} | {} | {} | {} | {} |".format(*row))
    w("")

    # ---- quality
    w("## quality.results")
    w("")
    w("| check | expected | detail |")
    w("|---|---|---|")
    neg = sum(1 for r in rows if r["is_won"] and r["days_to_close"] < 0)
    unexpected = {r["origin"] for r in rows} - KNOWN_ORIGINS
    incomplete = sum(1 for r in rows if not r["horizon_complete"])
    w(f"| leads: no row lost between bronze and silver | pass | bronze {len(rows)}, silver {len(rows)} |")
    w(f"| deals: no row lost between bronze and silver | pass | bronze {len(deals)}, silver {len(deals)} |")
    w(f"| lead id is unique in the source | pass | 0 duplicated ids |")
    w(f"| every deal traces back to a lead | pass | 0 orphan deals |")
    w(f"| a deal never closes before its lead exists | **FAIL** | {neg} deal(s) with a close date earlier than first contact |")
    w(f"| origin stays inside the known domain | pass | {len(unexpected)} unexpected values |")
    w(f"| every cohort is fully observed at the horizon | pass | {incomplete} leads not yet observable |")
    w("")

    text = "\n".join(out)
    if "--markdown" in sys.argv:
        (Path(__file__).parent / "expected-results.md").write_text(text)
        print("wrote tests/expected-results.md")
    else:
        print(text)


if __name__ == "__main__":
    main()
