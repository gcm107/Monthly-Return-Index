import yfinance as yf
import pandas as pd

symbol = "SPY"
initial_investment = 1000000
dates_of_investment = ["1995-01-01", "2000-01-01", "2005-01-01", "2008-01-01"]
holding_period_years = 15

spy_data = yf.download(symbol, start="1995-01-01", end="2025-01-01", auto_adjust=True)
prices_monthly = spy_data.resample("ME").last()
adj_close = prices_monthly["Close"].copy()

if isinstance(adj_close.index, pd.MultiIndex):
    adj_close = adj_close.droplevel(0)

monthly_returns = adj_close.pct_change().dropna()
total_return_index = (1 + monthly_returns).cumprod()
total_return_index.iloc[0] = 1.0

results = []

for start_date_str in dates_of_investment:
    start_date = pd.Timestamp(start_date_str)
    end_date = start_date + pd.DateOffset(years=holding_period_years)
    
    start_idx = total_return_index.index[total_return_index.index >= start_date][0]
    end_idx = total_return_index.index[total_return_index.index <= end_date][-1]

    val = total_return_index.loc[start_idx]
    start_value = float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    val = total_return_index.loc[end_idx]
    end_value = float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
    multiplier = end_value / start_value
    
    final_value = initial_investment * multiplier
    
    results.append({
        'start_date': start_date_str,
        'end_date': end_idx.strftime('%Y-%m-%d'),
        'final_value': final_value,
        'total_return_pct': (multiplier - 1) * 100
    })

results_df = pd.DataFrame(results)
print(results_df[['start_date', 'end_date', 'final_value', 'total_return_pct']].to_string(index=False))

best = results_df.loc[results_df['final_value'].idxmax()]
worst = results_df.loc[results_df['final_value'].idxmin()]

best_multiplier = best['final_value'] / initial_investment
worst_multiplier = worst['final_value'] / initial_investment

print(f"\nBest Start Date: {best['start_date']} = ${best['final_value']:,.0f}")
print(f"Worst Start Date: {worst['start_date']} = ${worst['final_value']:,.0f}")