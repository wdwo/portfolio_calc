# db_io.py
# # Database read and write interface functions

import pandas as pd
from sqlalchemy import create_engine, text
from config import Settings

# Example: "postgresql+psycopg2://user:password@localhost:5432/mydb"
DB_URL = f"postgresql+psycopg2://{Settings.DB_USER}:{Settings.DB_PASSWORD}@{Settings.DB_HOST}:{Settings.DB_PORT}/{Settings.DB_NAME}"

def connect_to_db():
    """Return an SQLAlchemy engine for the PostgreSQL database."""
    try:
        engine = create_engine(DB_URL)
        print("✅ Successfully connected to the PostgreSQL database.")
        return engine
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def read_transactions(engine):
    """Reads stock transactions from Postgres."""
    try:
        query = f"""
            SELECT {Settings.TICKER_COL}, {Settings.DATE_COL}, 
                   {Settings.QUANTITY_COL}, {Settings.PRICE_COL}, 
                   {Settings.FX_COL}, {Settings.CCY_COL_TRANS}
            FROM {Settings.TRANSACTIONS_TABLE}
            ORDER BY {Settings.TICKER_COL}, {Settings.DATE_COL};
        """
        df = pd.read_sql(query, engine)
        print(f"✅ Successfully read {len(df)} transactions.")
        return df
    except Exception as e:
        print(f"❌ Error reading data from table: {e}")
        return pd.DataFrame()


def read_latest_prices(engine):
    """Reads the latest stock prices from Postgres."""
    try:
        query = f"""
            SELECT {Settings.TICKER_COL_STOCK_DATA}, {Settings.PRICE_COL_STOCK_DATA}
            FROM {Settings.STOCK_DATA_TABLE};
        """
        df = pd.read_sql(query, engine)
        prices = df.set_index(Settings.TICKER_COL_STOCK_DATA)[Settings.PRICE_COL_STOCK_DATA].to_dict()
        print(f"✅ Successfully read {len(prices)} latest stock prices.")
        return prices
    except Exception as e:
        print(f"❌ Error reading latest prices: {e}")
        return {}


def read_current_fx_rates(engine):
    """Reads current FX rates from Postgres."""
    try:
        query = f"""
            SELECT {Settings.CCY_COL_FX}, {Settings.RATE_COL_FX}
            FROM {Settings.FX_DATA_TABLE};
        """
        df = pd.read_sql(query, engine)
        df[Settings.RATE_COL_FX] = pd.to_numeric(df[Settings.RATE_COL_FX], errors='coerce')
        df.dropna(subset=[Settings.RATE_COL_FX], inplace=True)
        fx_rates = df.set_index(Settings.CCY_COL_FX)[Settings.RATE_COL_FX].to_dict()
        print(f"✅ Successfully read {len(fx_rates)} FX rates.")
        return fx_rates
    except Exception as e:
        print(f"❌ Error reading FX rates: {e}")
        return {}


def write_pnl_data(engine, realized_df, unrealized_df):
    """Writes realized/unrealized P&L back to Postgres safely, replacing old rows."""
    try:
        # Open a connection and commit truncates first
        with engine.connect() as conn:
            if not realized_df.empty:
                conn.execute(text(f"TRUNCATE TABLE {Settings.REALIZED_PNL_TABLE} RESTART IDENTITY CASCADE;"))
                conn.commit()  # ensure the truncate is committed
            if not unrealized_df.empty:
                conn.execute(text(f"TRUNCATE TABLE {Settings.UNREALIZED_PNL_TABLE} RESTART IDENTITY CASCADE;"))
                conn.commit()

        # Now let Pandas insert rows
        if not realized_df.empty:
            realized_df.to_sql(Settings.REALIZED_PNL_TABLE, engine, if_exists='append', index=False)
            print(f"✅ Wrote {len(realized_df)} rows to {Settings.REALIZED_PNL_TABLE}.")
        else:
            print("ℹ️ No realized P&L data to write.")

        if not unrealized_df.empty:
            unrealized_df.to_sql(Settings.UNREALIZED_PNL_TABLE, engine, if_exists='append', index=False)
            print(f"✅ Wrote {len(unrealized_df)} rows to {Settings.UNREALIZED_PNL_TABLE}.")
        else:
            print("ℹ️ No unrealized P&L data to write.")

    except Exception as e:
        print(f"❌ Error writing to database: {e}")

