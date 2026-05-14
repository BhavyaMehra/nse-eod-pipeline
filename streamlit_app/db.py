import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_connection():
    return psycopg2.connect(
        host = os.getenv('NEON_HOST'),
        dbname = os.getenv('NEON_DB'),
        user = os.getenv('NEON_USER'),
        password = os.getenv('NEON_PASSWORD'),
        sslmode = 'require'
    )

@st.cache_data(ttl=3600)
def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def run_query_uncached(query):
    conn = get_connection()
    df = pd.read_sql(query)
    conn.close()
    return df
