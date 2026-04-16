"""
examples/basic_usage.py

Basic usage examples for the OCC Loans Python client.
"""

from occ_loans import OCCLoansClient

client = OCCLoansClient()

# ── 1. Check API health ────────────────────────────────────────────────────────
health = client.health()
print("API status:", health["status"])
print("Records in database:", f"{health['record_count']:,}")

# ── 2. Fetch all-time data for a single ticker (JSON) ─────────────────────────
result = client.get_loan_data("NVDA")
print(f"\nNVDA: {result['metadata']['total_records']} records")
print("First record:", result["data"][0])

# ── 3. Fetch a date range for multiple tickers ────────────────────────────────
result = client.get_loan_data(
    ["AAPL", "MSFT", "NVDA"],
    start_date="2024-01-01",
    end_date="2024-12-31",
)
print(f"\nAAPL/MSFT/NVDA 2024: {result['metadata']['total_records']} records")

# ── 4. Hedge loan balances only ───────────────────────────────────────────────
result = client.get_loan_data("GME", data_type="hedge")
print(f"\nGME hedge balance records: {result['metadata']['total_records']}")

# ── 5. Load into a pandas DataFrame ───────────────────────────────────────────
df = client.get_dataframe(["TSLA", "GME"], start_date="2021-01-01", end_date="2021-12-31")
print("\nDataFrame shape:", df.shape)
print(df.head())

# ── 6. Save to CSV ────────────────────────────────────────────────────────────
csv_text = client.get_loan_data_csv("AAPL", start_date="2024-01-01")
with open("aapl_loan_data.csv", "w") as f:
    f.write(csv_text)
print("\nSaved AAPL data to aapl_loan_data.csv")

# ── 7. List available tickers ─────────────────────────────────────────────────
tickers = client.get_tickers()
print(f"\nTotal tickers available: {len(tickers)}")
print("Sample:", tickers[:10])
