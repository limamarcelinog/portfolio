# Expected results

Computed by `tests/expected.py` directly from the CSVs, independently of the
SQL. Every number below is what the corresponding gold view must return.

- conversion horizon: **90 days**
- first lead contacted: **2017-06-14**
- first deal closed: **2017-12-05**
- observed through: **2018-11-14**
- leads: **8,000** · deals: **842**

## gold.conversion_by_channel

| origin | attribution_status | leads | won | conversion_pct | median_days_to_close |
|---|---|---:|---:|---:|---:|
| organic_search | named | 2296 | 218 | 9.5 | 10.0 |
| paid_search | named | 1586 | 150 | 9.5 | 10.0 |
| social | named | 1350 | 59 | 4.4 | 20 |
| unknown | unknown | 1099 | 157 | 14.3 | 9 |
| direct_traffic | named | 499 | 50 | 10.0 | 8.5 |
| email | named | 493 | 12 | 2.4 | 14.5 |
| referral | named | 284 | 21 | 7.4 | 11 |
| other | named | 150 | 4 | 2.7 | 9.0 |
| display | named | 118 | 6 | 5.1 | 8.5 |
| other_publicities | named | 65 | 3 | 4.6 | 35 |
| not_informed | not_informed | 60 | 12 | 20.0 | 6.5 |

## gold.conversion_by_cohort

`before_first_deal` marks cohorts that predate the closing operation.

| cohort_month | leads | won_ever | conversion_raw_pct | won_in_horizon | conversion_horizon_pct | before_first_deal |
|---|---:|---:|---:|---:|---:|---|
| 2017-06 | 4 | 0 | 0.0 | 0 | 0.0 | true |
| 2017-07 | 239 | 2 | 0.8 | 0 | 0.0 | true |
| 2017-08 | 386 | 9 | 2.3 | 0 | 0.0 | true |
| 2017-09 | 312 | 7 | 2.2 | 0 | 0.0 | true |
| 2017-10 | 416 | 14 | 3.4 | 0 | 0.0 | true |
| 2017-11 | 445 | 18 | 4.0 | 8 | 1.8 | true |
| 2017-12 | 200 | 11 | 5.5 | 6 | 3.0 | false |
| 2018-01 | 1141 | 152 | 13.3 | 129 | 11.3 | false |
| 2018-02 | 1028 | 149 | 14.5 | 128 | 12.5 | false |
| 2018-03 | 1174 | 167 | 14.2 | 141 | 12.0 | false |
| 2018-04 | 1352 | 183 | 13.5 | 171 | 12.6 | false |
| 2018-05 | 1303 | 130 | 10.0 | 109 | 8.4 | false |

## gold.time_to_close

| deals | p50_days | p75_days | p90_days | max_days |
|---:|---:|---:|---:|---:|
| 842 | 14 | 55 | 162 | 427 |

## gold.attribution_gap

| attribution_status | leads | pct_of_leads | won | conversion_pct |
|---|---:|---:|---:|---:|
| named | 6841 | 85.5 | 523 | 7.6 |
| unknown | 1099 | 13.7 | 157 | 14.3 |
| not_informed | 60 | 0.8 | 12 | 20.0 |

## gold.channel_leak

Baseline excludes the channel being measured, so a large underperformer
does not flatter itself by dragging down the average it is judged against.

| origin | leads | won | conversion_pct | baseline_excl_self_pct | deals_foregone |
|---|---:|---:|---:|---:|---:|
| social | 1350 | 59 | 4.4 | 8.5 | 55 |
| email | 493 | 12 | 2.4 | 8.0 | 28 |
| other | 150 | 4 | 2.7 | 7.8 | 8 |
| display | 118 | 6 | 5.1 | 7.7 | 3 |
| referral | 284 | 21 | 7.4 | 7.7 | 1 |
| direct_traffic | 499 | 50 | 10.0 | 7.5 | -13 |
| paid_search | 1586 | 150 | 9.5 | 7.1 | -37 |
| organic_search | 2296 | 218 | 9.5 | 6.7 | -64 |

## quality.results

| check | expected | detail |
|---|---|---|
| leads: no row lost between bronze and silver | pass | bronze 8000, silver 8000 |
| deals: no row lost between bronze and silver | pass | bronze 842, silver 842 |
| lead id is unique in the source | pass | 0 duplicated ids |
| every deal traces back to a lead | pass | 0 orphan deals |
| a deal never closes before its lead exists | **FAIL** | 1 deal(s) with a close date earlier than first contact |
| origin stays inside the known domain | pass | 0 unexpected values |
| every cohort is fully observed at the horizon | pass | 0 leads not yet observable |
