# main.py - (This is the complete, final version)

import pandas as pd
import matplotlib.pyplot as plt
import configparser

# Import all agents, including our new final strategy
from src.data.data_manager import DataManager
from src.risk.risk_manager import RiskManager
from src.strategies.sopr_ema_strategy import SoprEmaStrategy # <-- Import new strategy
from src.portfolio.portfolio_manager import PortfolioManager

def plot_results(results, data):
    """Plots the equity curve and trade signals."""
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # Plot equity curve
    ax1.plot(results.index, results['equity'], label='Portfolio Equity', color='blue')
    ax1.set_title('Final Strategy Performance', fontsize=16)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Portfolio Value ($)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    # Create a second y-axis for the price
    ax2 = ax1.twinx()
    ax2.plot(data.index, data['close'], label='BTC Price', color='gray', alpha=0.5, linewidth=0.75)
    ax2.set_ylabel('BTC Price ($)', color='gray')
    ax2.tick_params(axis='y', labelcolor='gray')
    ax2.set_yscale('log')
    
    # Plot buy and sell markers on the price chart
    trades = results[results['trades'].notna()]
    for idx, trade in trades['trades'].items():
        if trade['type'] == 'buy':
            ax2.scatter(idx, trade['price'], marker='^', color='green', s=150, zorder=5, label='Buy')
        elif trade['type'] == 'sell':
            ax2.scatter(idx, trade['price'], marker='v', color='red', s=150, zorder=5, label='Sell')
    
    # Consolidate legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    # To avoid duplicate labels, we can use a dictionary
    unique_labels = dict(zip(labels2 + labels, lines2 + lines))
    ax2.legend(unique_labels.values(), unique_labels.keys())
    
    plt.show()

def main():
    """Main function to run the final backtest."""
    # --- 1. Configuration & Data Loading ---
    data_manager = DataManager()
    
    price_df = data_manager.load_data('data/BTC_USDT_1d.csv', index_col='timestamp')
    sopr_df = data_manager.load_data('data/bitcoin_sopr_data.csv', index_col='date')
    sopr_df.rename(columns={'sopr_value': 'sopr'}, inplace=True)
    
    # Combine data sources
    data = pd.merge(price_df, sopr_df['sopr'], left_index=True, right_index=True, how='inner')
    
    # Calculate ATR for risk manager
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())
    low_close = abs(data['low'] - data['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    data['atr'] = true_range.rolling(window=14).mean()
    data = data.dropna()
    
    # --- 2. Initialize Agents ---
    risk_manager = RiskManager()
    strategies = {
        'default': SoprEmaStrategy() # Use our new final strategy
    }
    
    # --- 3. Run Backtest ---
    print("Initializing Portfolio Manager and running FINAL backtest...")
    portfolio_manager = PortfolioManager(
        data=data,
        strategies=strategies,
        risk_manager=risk_manager,
        initial_capital=100000.0,
        commission_pct=0.001,
        slippage_pct=0.0005
    )
    results = portfolio_manager.run_backtest()
    
    # --- 4. Analyze and Display Results ---
    final_equity = results['equity'].iloc[-1]
    initial_capital = results['equity'].iloc[0]
    total_return_pct = ((final_equity / initial_capital) - 1) * 100
    
    print("\n--- Backtest Finished ---")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Equity:    ${final_equity:,.2f}")
    print(f"Total Return:    {total_return_pct:.2f}%")
    print("-------------------------")
    
    plot_results(results, data)


if __name__ == "__main__":
    main()