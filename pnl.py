# Calculates realized and unrealized pnl for portfolio
# pnl.py
import pandas as pd
from db_io import connect_to_db, read_transactions, write_pnl_data
from config import Settings

def calculate_pnl_fifo(transactions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates realized and unrealized P&L using the FIFO method.
    It now handles buys (positive quantity) and sells (negative quantity).
    """
    realized_pnl = []
    unrealized_positions = {}
    
    # Sort transactions by ticker and date to ensure FIFO order
    transactions = transactions.sort_values(by=[Settings.TICKER_COL, Settings.DATE_COL])

    for _, row in transactions.iterrows():
        ticker = row[Settings.TICKER_COL]
        quantity = row[Settings.QUANTITY_COL]
        price = row[Settings.PRICE_COL]
        date = row[Settings.DATE_COL]
        fx = row[Settings.FX_COL]

        if ticker not in unrealized_positions:
            unrealized_positions[ticker] = []

        if quantity > 0:  # This is a BUY transaction
            cost_basis_in_base_currency = price * fx
            unrealized_positions[ticker].append({
                'quantity': quantity,
                'price': price,
                'date': date,
                'cost_basis': cost_basis_in_base_currency
            })
        elif quantity < 0:  # This is a SELL transaction
            sell_quantity_remaining = abs(quantity)
            if not unrealized_positions[ticker]:
                print(f"⚠️ Warning: Sell transaction for {ticker} has no corresponding buy position. Skipping.")
                continue

            # FIFO: Process oldest buy positions first
            while sell_quantity_remaining > 0 and unrealized_positions[ticker]:
                oldest_buy = unrealized_positions[ticker][0]
                buy_quantity = oldest_buy['quantity']
                buy_cost_basis = oldest_buy['cost_basis']
                
                if buy_quantity <= sell_quantity_remaining:
                    # Entire buy position is sold
                    realized_gain = (price * abs(quantity) * fx) - (buy_cost_basis / buy_quantity * buy_quantity)
                    realized_pnl.append({
                        'symbol': ticker,
                        'realized_gain': realized_gain,
                        'buy_date': oldest_buy['date'],
                        'sell_date': date,
                        'quantity_sold': buy_quantity
                    })
                    sell_quantity_remaining -= buy_quantity
                    unrealized_positions[ticker].pop(0)
                else:
                    # Partial sale of the oldest buy position
                    partial_sale_cost_basis = buy_cost_basis / buy_quantity * sell_quantity_remaining
                    realized_gain = (price * sell_quantity_remaining * fx) - partial_sale_cost_basis
                    realized_pnl.append({
                        'symbol': ticker,
                        'realized_gain': realized_gain,
                        'buy_date': oldest_buy['date'],
                        'sell_date': date,
                        'quantity_sold': sell_quantity_remaining
                    })
                    unrealized_positions[ticker][0]['quantity'] -= sell_quantity_remaining
                    unrealized_positions[ticker][0]['cost_basis'] -= partial_sale_cost_basis
                    sell_quantity_remaining = 0
    
    # Calculate unrealized P&L from remaining positions
    unrealized_pnl_data = []
    for ticker, positions in unrealized_positions.items():
        for pos in positions:
            # Need to get current market price in base currency
            current_market_price = 150 # Placeholder
            current_fx = 1.2 # Placeholder
            unrealized_gain = (current_market_price * current_fx * pos['quantity']) - pos['cost_basis']
            unrealized_pnl_data.append({
                'symbol': ticker,
                'quantity': pos['quantity'],
                'cost_basis': pos['cost_basis'],
                'current_market_value': current_market_price * current_fx * pos['quantity'],
                'unrealized_gain': unrealized_gain
            })
            
    return pd.DataFrame(realized_pnl), pd.DataFrame(unrealized_pnl_data)

def main():
    """Main function to run the P&L calculation script."""
    conn = connect_to_db()
    if not conn:
        return

    try:
        transactions_df = read_transactions(conn)
        if transactions_df.empty:
            return
        
        realized_df, unrealized_df = calculate_pnl_fifo(transactions_df)
        
        write_pnl_data(conn, realized_df, unrealized_df)

    finally:
        conn.close()
        print("✅ Database connection closed.")

if __name__ == "__main__":
    main()