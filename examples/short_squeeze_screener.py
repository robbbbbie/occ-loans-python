"""
examples/short_squeeze_screener.py

Screen for potential short squeeze candidates using OCC loan data.

Looks for stocks where borrow balances have risen significantly over the
past 30 trading days — a pattern that can precede a short squeeze if
a positive catalyst emerges.

Requires: pandas  (`pip install pandas`)
"""

from datetime import date, timedelta
from occ_loans import OCCLoansClient
import pandas as pd

# Tickers to screen — extend this list as needed
WATCHLIST = [
    "GME", "AMC", "BBBY", "TSLA", "NVDA", "RIVN", "LCID",
    "PLTR", "MSTR", "COIN", "HOOD", "SOFI", "UWMC", "OPEN",
]

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=60)  # ~42 trading days

client = OCCLoansClient()

print(f"Fetching OCC loan data for {len(WATCHLIST)} tickers...")
df = client.get_dataframe(
    WATCHLIST,
    start_date=START_DATE,
    end_date=END_DATE,
    data_type="hedge",
)

# Keep hedge loan balance column only
balance_col = "Hedge Loan Balance"
df = df[["Symbol", "Date", balance_col]].dropna()

results = []

for symbol, group in df.groupby("Symbol"):
    group = group.sort_values("Date")
    if len(group) < 10:
        continue

    recent = group.tail(5)[balance_col].mean()   # avg of last 5 trading days
    earlier = group.head(10)[balance_col].mean()  # avg of first 10 trading days

    if earlier == 0:
        continue

    pct_change = (recent - earlier) / earlier * 100
    latest_balance = group.iloc[-1][balance_col]

    results.append({
        "Ticker": symbol,
        "Latest Balance ($)": latest_balance,
        "30-Day Change (%)": round(pct_change, 1),
        "Latest Date": group.iloc[-1]["Date"].date(),
    })

results_df = pd.DataFrame(results)
results_df = results_df.sort_values("30-Day Change (%)", ascending=False)

print("\n── Short Squeeze Candidates (Rising Borrow Trend) ──────────────────")
print(f"{'Ticker':<8} {'Latest Balance':>18} {'30-Day Change':>15} {'As Of':>12}")
print("─" * 58)

for _, row in results_df.iterrows():
    bal = row["Latest Balance ($)"]
    bal_fmt = f"${bal/1e9:.2f}B" if bal >= 1e9 else f"${bal/1e6:.1f}M"
    chg = row["30-Day Change (%)"]
    chg_fmt = f"+{chg:.1f}%" if chg >= 0 else f"{chg:.1f}%"
    print(f"{row['Ticker']:<8} {bal_fmt:>18} {chg_fmt:>15} {str(row['Latest Date']):>12}")

print("\nData source: OCC Loans (https://occloans.com)")
print("Not investment advice. For informational purposes only.")
