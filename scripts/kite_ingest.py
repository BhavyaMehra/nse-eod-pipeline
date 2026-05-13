import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from kiteconnect import KiteConnect
from dotenv import load_dotenv
from datetime import date, datetime
import sys

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN')
FNO_PATH = os.path.join(os.path.dirname(__file__), 'fno_stocks.xlsx')

DB_CONFIG = {
    "host":     os.getenv('NEON_HOST'),
    "sslmode":  'require',
    "dbname":   os.getenv('NEON_DB'),
    "user":     os.getenv('NEON_USER'),
    "password": os.getenv('NEON_PASSWORD'),
}

def load_universe(path):
    df = pd.read_excel(path, engine='openpyxl')
    return df['Symbol'].dropna().str.strip().tolist()


def fetch_eod(kite, symbol, trade_date):
    instrument = f'NSE:{symbol}'
    try:
        data = kite.historical_data(
        instrument_token = kite.ltp(instrument)[instrument]['instrument_token'],
        from_date = trade_date,
        to_date = trade_date,
        interval = 'day'
        )

        if data:
            row = data[0]
            return (symbol, trade_date, row['open'], row['high'], row['low'], row['close'], row['volume'])
        
    except Exception as e:
        print(f'Failed {symbol}: {e}')

    return None

def fetch_nifty_eod(kite, trade_date):
    NIFTY_TOKEN = 256265
    try:
        data = kite.historical_data(
            instrument_token=NIFTY_TOKEN,
            from_date=trade_date,
            to_date=trade_date,
            interval='day'
        )
        if data:
            row = data[0]
            # volume is 0 for indices on Kite - stored as 0, handled in staging
            return ('NIFTY 50', trade_date, row['open'], row['high'], row['low'], row['close'], row['volume'])
    except Exception as e:
        print(f'Failed NIFTY 50: {e}')
    return None


def insert_records(conn, records):
    sql = """
        INSERT INTO raw.eod_prices (ticker, trade_date, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (ticker, trade_date) DO UPDATE SET
            open        = EXCLUDED.open,
            high        = EXCLUDED.high,
            low         = EXCLUDED.low,
            close       = EXCLUDED.close,
            volume      = EXCLUDED.volume,
            ingested_at = NOW()
    """

    with conn.cursor() as cur:
        execute_values(cur, sql, records)
    conn.commit()


def run():
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(ACCESS_TOKEN)

    universe = load_universe(FNO_PATH)

    if len (sys.argv) > 1:
        today = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        today = date.today()
        
    records = []
    failed = []

    print(f'Fetching EOD for {len(universe)} stocks on {today}.')

    for symbol in universe:
        row = fetch_eod(kite, symbol, today)
        if row:
            records.append(row)
        else:
            failed.append(symbol)

    print(f'Fetched: {len(records)} | Failed: {len(failed)}')

    if failed:
        print(f'Failed tickers: {failed}')

    nifty_row = fetch_nifty_eod(kite, today)
    if nifty_row:
        records.append(nifty_row)
        print('Nifty 50 fetched.')
    else:
        print('Nifty 50 fetch failed.')

    if records:
        conn = psycopg2.connect(**DB_CONFIG)
        insert_records(conn, records)
        conn.close()
        print('Data inserted into raw.eod_prices.')


if __name__ == "__main__":
    run()

