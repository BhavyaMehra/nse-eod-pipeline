CREATE DATABASE nse_warehouse;

\c nse_warehouse;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS raw.eod_prices (
    id              BIGSERIAL PRIMARY KEY,
    ticker          VARCHAR(20)     NOT NULL,
    trade_date      DATE            NOT NULL,
    open            NUMERIC(12, 4),
    high            NUMERIC(12, 4),
    low             NUMERIC(12, 4),
    close           NUMERIC(12, 4)  NOT NULL,
    volume          BIGINT,
    ingested_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE  (ticker, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_eod_ticker_date
    ON raw.eod_prices(ticker, trade_date DESC)