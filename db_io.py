# db_io.py
# # Database read and write interface functions

import sqlite3
import pandas as pd
from config import Settings

def connect_to_db():
    # Establishes a connection to the SQLite database.
    try:
        conn = sqlite3.connect(Settings.DB_FILE)
        print("✅ Successfully connected to the database.")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def read_transactions(conn):
    # Reads all stock transactions from the database.
    try:
        query = f"SELECT * FROM {Settings.TRANSACTIONS_TABLE} ORDER BY symbol, date, type"
        df = pd.read_sql_query(query, conn)
        print(f"✅ Successfully read {len(df)} transactions.")
        return df
    except sqlite3.Error as e:
        print(f"❌ Error reading data from table: {e}")
        return pd.DataFrame()

def write_pnl_data(conn, realized_df, unrealized_df):
    # Writes the realized and unrealized P&L data back to the database.
    try:
        # Write realized P&L data
        if not realized_df.empty:
            realized_df.to_sql(Settings.REALIZED_PNL_TABLE, conn, if_exists='replace', index=False)
            print(f"✅ Successfully wrote {len(realized_df)} rows to {Settings.REALIZED_PNL_TABLE}.")
        else:
            print(f"ℹ️ No realized P&L data to write.")

        # Write unrealized P&L data
        if not unrealized_df.empty:
            unrealized_df.to_sql(Settings.UNREALIZED_PNL_TABLE, conn, if_exists='replace', index=False)
            print(f"✅ Successfully wrote {len(unrealized_df)} rows to {Settings.UNREALIZED_PNL_TABLE}.")
        else:
            print(f"ℹ️ No unrealized P&L data to write.")
            
    except sqlite3.Error as e:
        print(f"❌ Error writing to database: {e}")