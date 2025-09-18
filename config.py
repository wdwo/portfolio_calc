# Configuration file 
import os
from pathlib import Path

# Get the current script's directory and project root
current_dir = Path(__file__).parent
project_root = current_dir

class Settings:
    # Define Paths from environment variables or defaults
    DB_PATH = os.getenv('DB_PATH', project_root / 'db')

    # Database 
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    DB_FILENAME = os.getenv('DB_FILENAME', 'dwo.db')
    DB_FULLPATH = DB_PATH / DB_FILENAME

    # Table names
    TRANSACTIONS_TABLE = 'equity_transactions'
    REALIZED_PNL_TABLE = 'realized_pnl'
    UNREALIZED_PNL_TABLE = 'unrealized_pnl'

    # Column names
    TICKER_COL = 'ticker'
    QUANTITY_COL = 'quantity'
    PRICE_COL = 'transacted_price'
    DATE_COL = 'transaction_date' # Assuming this column contains a date/datetime value
    FX_COL = 'fx'

    # Current stock price table and columns
    STOCK_DATA_TABLE = 'stock_data'
    TICKER_COL_STOCK_DATA = 'ticker_base'
    PRICE_COL_STOCK_DATA = 'last_price'

    # FX rate table and columns
    FX_DATA_TABLE = 'fx_data'
    CCY_COL_FX = 'CCY1'
    RATE_COL_FX = 'rate'
    
    # Transaction table currency column
    CCY_COL_TRANS = 'ccy'