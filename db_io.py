# db_io.py
# # Database read and write interface functions

import sqlite3
import pandas as pd
from config import Settings

def connect_to_db():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(Settings.DB_FULLPATH)
        print("✅ Successfully connected to the database.")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def read_transactions(conn):
    """
    Reads all stock transactions from the database using the column names 
    defined in the Settings class.
    """
    try:
        # Use column names from the Settings class
        query = f"SELECT `{Settings.TICKER_COL}`, `{Settings.DATE_COL}`, `{Settings.QUANTITY_COL}`, `{Settings.PRICE_COL}`, `{Settings.FX_COL}`, `{Settings.CCY_COL_TRANS}` FROM {Settings.TRANSACTIONS_TABLE} ORDER BY `{Settings.TICKER_COL}`, `{Settings.DATE_COL}`"
        df = pd.read_sql_query(query, conn)
        print(f"✅ Successfully read {len(df)} transactions.")
        return df
    except sqlite3.Error as e:
        print(f"❌ Error reading data from table: {e}")
        return pd.DataFrame()
    

def read_latest_prices(conn):
    # Reads the latest stock prices from the stock_data table.
    # Returns:
    #    A dictionary mapping ticker to its latest price.
    
    try:
        query = f"SELECT `{Settings.TICKER_COL_STOCK_DATA}`, `{Settings.PRICE_COL_STOCK_DATA}` FROM {Settings.STOCK_DATA_TABLE}"
        df = pd.read_sql_query(query, conn)
        
        # Convert DataFrame to a dictionary for easy lookup
        prices = df.set_index(Settings.TICKER_COL_STOCK_DATA)[Settings.PRICE_COL_STOCK_DATA].to_dict()
        print(f"✅ Successfully read {len(prices)} latest stock prices.")
        return prices
    except sqlite3.Error as e:
        print(f"❌ Error reading latest prices from table: {e}")
        return {}

def read_current_fx_rates(conn):
    # Reads current foreign exchange rates from the fx_data table.
    # Returns:
    #     A dictionary mapping currency code to its current rate.
    try:
        query = f"SELECT `{Settings.CCY_COL_FX}`, `{Settings.RATE_COL_FX}` FROM {Settings.FX_DATA_TABLE}"
        df = pd.read_sql_query(query, conn)
        
        # Ensure rate column is numeric
        df[Settings.RATE_COL_FX] = pd.to_numeric(df[Settings.RATE_COL_FX], errors='coerce')
        df.dropna(subset=[Settings.RATE_COL_FX], inplace=True)
        
        # Convert DataFrame to a dictionary for easy lookup
        fx_rates = df.set_index(Settings.CCY_COL_FX)[Settings.RATE_COL_FX].to_dict()
        print(f"✅ Successfully read {len(fx_rates)} current FX rates.")
        return fx_rates
    except sqlite3.Error as e:
        print(f"❌ Error reading FX rates from table: {e}")
        return {}


def write_pnl_data(conn, realized_df, unrealized_df):
    """Writes the realized and unrealized P&L data back to the database."""
    try:
        if not realized_df.empty:
            realized_df.to_sql(Settings.REALIZED_PNL_TABLE, conn, if_exists='replace', index=False)
            print(f"✅ Successfully wrote {len(realized_df)} rows to {Settings.REALIZED_PNL_TABLE}.")
        else:
            print(f"ℹ️ No realized P&L data to write.")

        if not unrealized_df.empty:
            unrealized_df.to_sql(Settings.UNREALIZED_PNL_TABLE, conn, if_exists='replace', index=False)
            print(f"✅ Successfully wrote {len(unrealized_df)} rows to {Settings.UNREALIZED_PNL_TABLE}.")
        else:
            print(f"ℹ️ No unrealized P&L data to write.")
    except sqlite3.Error as e:
        print(f"❌ Error writing to database: {e}")