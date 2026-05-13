# NSE EOD Data Pipeline - Project Tracker

**Stack:** Kite Connect | Airflow | dbt (raw > staging > marts) | PostgreSQL on Neon | Docker | Streamlit

**What it is:** A fully automated end-of-day data pipeline for NSE equities with a multi-page analytics front-end. Ingests OHLCV data via Kite Connect, transforms through a dbt layer, and surfaces market intelligence via Streamlit.

---

## What's Done

### Infrastructure
- [x] Dockerized setup with docker-compose
- [x] Airflow DAG with weekday-only schedule (Mon-Fri)
- [x] Kite Connect ingestion scripts
- [x] Cloud PostgreSQL on Neon (migrated from local)
- [x] dbt project with raw, staging, and marts layers

### dbt Layer
- [x] Raw models: source OHLCV ingestion
- [x] Staging models: type casting, cleaning, null handling
- [x] Marts: moving averages, rolling volatility (20-day)

### Streamlit App (4 pages)
- [x] Home: market breadth bar (red/green), page descriptions
- [x] Market Overview: stock universe heatmap, top gainers/losers tables
- [x] Stock Deep Dive: price + MA chart, daily returns chart, 20-day rolling vol chart
- [x] Screener: filter by daily return % and volume, table output, CSV download

---

## What's Missing (Recruiter Lens)

A recruiter evaluating this for a DA/DS/analytics role wants to see three things this project currently lacks:

1. **Data quality layer** - nothing validates that what came in is correct
2. **Analytical depth** - marts are thin, screener filters are weak, no actionable output
3. **Business value** - every page is descriptive (what happened) not prescriptive (what to watch)

---

## To-Do: Prioritized

### Priority 1 - Data Quality (foundational, low effort, high signal)

- [ ] Add dbt schema tests: `not_null` and `unique` on date + symbol in staging, accepted range on close > 0 and volume > 0
- [ ] Run `dbt test` as a DAG task after `dbt run`, log pass/fail count to a `pipeline_runs` table
- [ ] Fix DAG schedule if running in IST: `45 10 * * 1-5` fires at 10:45 AM IST (mid-session). Should be `30 16 * * 1-5` for post-close EOD pull
- [ ] Show last pipeline run status (rows ingested, tests passed) on Streamlit home page

**Why it matters to a recruiter:** Production data pipelines have validation. This shows engineering maturity, not just the ability to pull data.

---

### Priority 2 - Enrich the Marts (unlocks everything downstream)

- [ ] `mart_rsi`: RSI(14) using window functions on staging close prices
- [ ] `mart_atr`: ATR(14) on OHLC - needed for signal generation
- [ ] `mart_vol_ratio`: today volume / 20-day avg volume
- [ ] `mart_relative_strength`: 20-day return of stock minus 20-day return of Nifty50

These are all pure SQL dbt models on top of existing staging data.

**Why it matters to a recruiter:** Moving averages and rolling vol are table stakes. RSI, ATR, and relative strength show you understand what practitioners actually use.

---

### Priority 3 - Screener Upgrade (highest visibility improvement)

Current screener filters on daily return % and volume only. Replace/extend with:

- [ ] RSI range slider (e.g., filter stocks with RSI between 40 and 65)
- [ ] Volume ratio filter (vol ratio > 1.5 = unusual activity)
- [ ] Relative strength filter (outperforming Nifty50 over 20 days: yes/no toggle)
- [ ] 52-week high proximity slider (e.g., within 15% of 52W high)
- [ ] Display all indicator columns in the output table (sortable)
- [ ] "Sweep Setup" preset button: RSI < 60, vol ratio > 1.0, in original universe - one click populates all filters

**Why it matters to a recruiter:** A screener that filters on two columns is a table with a dropdown. A multi-factor screener with presets shows product thinking and analytical judgment.

---

### Priority 4 - Stock Deep Dive Upgrades

- [ ] Add RSI(14) subplot below price chart with reference lines at 50 and 60
- [ ] Replace or supplement rolling vol chart with ATR(14)
- [ ] If signals mart exists (Priority 5), plot entry markers on the price chart for that stock

**Why it matters to a recruiter:** Shows you know which indicators matter and why, not just that you can plot a chart.

---

### Priority 5 - Signals Page (transforms the project's category)

Add `4_Signals.py` to Streamlit. This is what elevates the project from "data dashboard" to "trading research system."

#### dbt / pipeline side
- [ ] Add signal generation logic as a dbt model or post-transform DAG task
- [ ] Write one row per signal to `mart_signals`: symbol, date, entry_ref (prior candle low), sl, tp (1.75 ATR), rsi_at_signal, atr_at_signal, in_original_universe

#### Streamlit side
- [ ] Today's signals table with all fields above
- [ ] Historical signal log (all signals since pipeline went live)
- [ ] Paper trade outcome tracker: exit date, exit price, R-multiple outcome
- [ ] Equity curve in R-multiples once paper trading data accumulates

**Why it matters to a recruiter:** This is the "so what" of the entire pipeline. Every upstream component exists to produce this. Closing the loop makes the project defensible end-to-end in an interview.

---

### Priority 6 - Market Overview Upgrades (polish)

- [ ] Heatmap color toggle: daily return vs 20-day relative strength vs Nifty
- [ ] Third table: "High Volume Activity" - vol ratio > 1.5 today, sorted by relative strength
- [ ] Shrink page description text on home page, it takes up prime real estate

---

### Priority 7 - Documentation (needed before sharing publicly)

- [ ] README: what the project does, stack, how to run locally, architecture diagram
- [ ] Architecture diagram in `/architecture` folder: DAG flow, dbt layer, DB schema, Streamlit pages
- [ ] `.env.example` already exists - confirm all required keys are documented
- [ ] Add GitHub link to CV once Priority 3 and 5 are done

---

## What This Project Demonstrates (for CV / interviews)

| Skill Area | Evidence |
|---|---|
| Data engineering | Airflow orchestration, dbt layering, Docker, cloud DB |
| SQL | dbt models: window functions for RSI/ATR, multi-table marts |
| Python | Kite Connect ingestion, Streamlit multi-page app |
| Product thinking | Multi-filter screener with presets, signal-to-action pipeline |
| Data quality | dbt tests, pipeline run logging (after Priority 1) |
| Domain knowledge | NSE universe, FNO-relevant indicators, systematic signal logic |

---

## Suggested CV Line (after Priority 3 + 5 are done)

"Built an end-to-end NSE EOD data pipeline (Kite Connect, Airflow, dbt, PostgreSQL, Docker) with a multi-page Streamlit analytics app featuring a multi-factor stock screener, RSI/ATR-based signal generation, and paper trade outcome tracking across a 100+ stock universe."
