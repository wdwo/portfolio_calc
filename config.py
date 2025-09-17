# Configuration file 
import os
from pathlib import Path

# Get the current script's directory and project root
current_dir = Path(__file__).parent
project_root = current_dir.parent

class Settings:
    # Define Paths from environment variables or defaults
    DB_PATH = os.getenv('DB_PATH', project_root / 'db')

    # Database 
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    DB_FILENAME = os.getenv('DB_FILENAME', 'dwo.db')

    # Table names
    TRANSACTIONS_TABLE = 'equity_transactions'
    REALIZED_PNL_TABLE = 'realized_pnl'
    UNREALIZED_PNL_TABLE = 'unrealized_pnl'