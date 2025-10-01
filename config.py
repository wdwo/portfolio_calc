# Configuration file 
import os
from pathlib import Path

# Get the current script's directory and project root
current_dir = Path(__file__).parent
project_root = current_dir

class Settings:
    # Define Paths from environment variables or defaults

    DB_HOST = os.getenv('DB_HOST', 'postgres')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'dwoadmin')
    DB_PASSWORD= os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'dwo')


    # Table names
    TRANSACTIONS_TABLE = os.getenv('EQUITY_TRANSACTIONS_TABLE','equity_transactions')
    REALIZED_PNL_TABLE = os.getenv('REALIZED_PNL_TABLE','realized_pnl')
    UNREALIZED_PNL_TABLE = os.getenv('UNREALIZED_PNL_TABLE','unrealized_pnl')

    # Column names
    TICKER_COL = os.getenv('TICKER_COL','ticker')
    QUANTITY_COL = os.getenv('QUANTITY_COL','quantity')
    PRICE_COL = os.getenv('PRICE_COL','transacted_price')
    DATE_COL = os.getenv('DATE_COL','transaction_date') # Assuming this column contains a date/datetime value
    FX_COL = os.getenv('FX_COL','fx')

    # Current stock price table and columns
    STOCK_DATA_TABLE = os.getenv('STOCK_DATA_TABLE','stock_data')
    TICKER_COL_STOCK_DATA = os.getenv('TICKER_COL_STOCK_DATA','ticker_base')
    PRICE_COL_STOCK_DATA = os.getenv('PRICE_COL_STOCK_DATA','last_price')

    # FX rate table and columns
    FX_DATA_TABLE = os.getenv('FX_DATA_TABLE','fx_data')
    CCY_COL_FX = os.getenv('CCY_COL_FX','ccy1')
    RATE_COL_FX = os.getenv('RATE_COL_FX','rate')
    
    # Transaction table currency column
    CCY_COL_TRANS = os.getenv('CCY_COL_TRANS','ccy')