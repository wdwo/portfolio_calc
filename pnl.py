# Calculates realized and unrealized pnl for portfolio
# pnl.py
import pandas as pd
from db_io import connect_to_db, read_transactions, read_latest_prices, read_current_fx_rates, write_pnl_data
from config import Settings

def calculate_pnl_fifo(transactions: pd.DataFrame, latest_prices: dict, current_fx_rates: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates realized and unrealized P&L using the FIFO method.
    It now uses latest_prices and current_fx_rates to calculate unrealized P&L.
    """
    realized_pnl = []
    unrealized_positions = {}
    
    transactions = transactions.sort_values(by=[Settings.TICKER_COL, Settings.DATE_COL])
    
    # Create a mapping from ticker to currency for easy lookup later
    ticker_to_ccy = transactions.set_index(Settings.TICKER_COL)[Settings.CCY_COL_TRANS].to_dict()

    for _, row in transactions.iterrows():
        ticker = row[Settings.TICKER_COL]
        quantity = row[Settings.QUANTITY_COL]
        price = row[Settings.PRICE_COL]
        date = row[Settings.DATE_COL]
        fx = row[Settings.FX_COL]

        if ticker not in unrealized_positions:
            unrealized_positions[ticker] = []

        if quantity > 0:  # This is a BUY transaction
            cost_basis_per_share = (price * fx)
            unrealized_positions[ticker].append({
                'quantity': quantity,
                'price': price,
                'date': date,
                'cost_basis_per_share': cost_basis_per_share
            })
        elif quantity < 0:  # This is a SELL transaction
            # ... (realized P&L calculation logic, unchanged) ...
            sell_quantity_remaining = abs(quantity)
            if not unrealized_positions[ticker]:
                print(f"⚠️ Warning: Sell transaction for {ticker} has no corresponding buy position. Skipping.")
                continue

            while sell_quantity_remaining > 0 and unrealized_positions[ticker]:
                oldest_buy = unrealized_positions[ticker][0]
                buy_quantity = oldest_buy['quantity']
                buy_cost_basis_per_share = oldest_buy['cost_basis_per_share']
                
                if buy_quantity <= sell_quantity_remaining:
                    realized_gain = (price * fx - buy_cost_basis_per_share) * buy_quantity
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
                    realized_gain = (price * fx - buy_cost_basis_per_share) * sell_quantity_remaining
                    realized_pnl.append({
                        'symbol': ticker,
                        'realized_gain': realized_gain,
                        'buy_date': oldest_buy['date'],
                        'sell_date': date,
                        'quantity_sold': sell_quantity_remaining
                    })
                    unrealized_positions[ticker][0]['quantity'] -= sell_quantity_remaining
                    sell_quantity_remaining = 0
    
    # Calculate unrealized P&L from remaining positions
    unrealized_pnl_data = []
    for ticker, positions in unrealized_positions.items():
        # Check if there's any remaining quantity for the ticker
        total_remaining_quantity = sum(pos['quantity'] for pos in positions)
        # Only proceed if the total remaining quantity is positive
        if total_remaining_quantity > 0:
            if ticker in latest_prices and ticker in ticker_to_ccy:
                currency = ticker_to_ccy[ticker]
                if currency in current_fx_rates:
                    current_market_price = latest_prices[ticker]
                    current_fx_rate = current_fx_rates[currency]
                    for pos in positions:
                        # Unrealized gain now factors in both latest price and current FX rate
                        unrealized_gain = (current_market_price * current_fx_rate - pos['cost_basis_per_share']) * pos['quantity']
                        unrealized_pnl_data.append({
                            'symbol': ticker,
                            'quantity': pos['quantity'],
                            'cost_basis_per_share': pos['cost_basis_per_share'],
                            'current_market_price': current_market_price,
                            'current_fx_rate': current_fx_rate,
                            'unrealized_gain': unrealized_gain
                        })
                else:
                    print(f"⚠️ Warning: No current FX rate found for currency '{currency}'. Skipping unrealized P&L for {ticker}.")
            else:
                print(f"⚠️ Warning: No latest price or currency found for {ticker}. Skipping unrealized P&L calculation for this position.")
            
    return pd.DataFrame(realized_pnl), pd.DataFrame(unrealized_pnl_data)

def main():
    """Main function to run the P&L calculation script."""
    conn = connect_to_db()
    if not conn:
        return

    try:
        transactions_df = read_transactions(conn)
        latest_prices = read_latest_prices(conn)
        current_fx_rates = read_current_fx_rates(conn)
        if transactions_df.empty:
            return
        
        # Pass the latest_prices dictionary to the calculation function
        realized_df, unrealized_df = calculate_pnl_fifo(transactions_df, latest_prices, current_fx_rates)
        
        
        write_pnl_data(conn, realized_df, unrealized_df)

    finally:
        # conn.close()
        print("✅ Database connection closed.")

if __name__ == "__main__":
    main()