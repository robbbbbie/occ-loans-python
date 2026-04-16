# occ-loans-python

Python client for the [OCC Loans API](https://occloans.com) — fetch historical OCC Stock Loan Program data for any ticker or date range.

**No API key required. No account needed. Completely free.**

## What is OCC Loan Data?

The [OCC Stock Loan Program](https://occloans.com) publishes daily stock borrow balances for thousands of securities. High or rising borrow balances can indicate increasing short interest, institutional hedging activity, or potential short squeeze conditions.

[OCC Loans](https://occloans.com) has collected and archived this data every trading day since **September 2018** — over 7 years of history — and made it accessible via a free REST API.

## Installation

No dependencies required for basic usage (just the standard `requests` library). Install `pandas` for DataFrame support.

```bash
pip install requests

# Optional — for get_dataframe() and examples
pip install pandas
```

Copy `occ_loans.py` into your project or clone this repo.

## Quick Start

```python
from occ_loans import OCCLoansClient

client = OCCLoansClient()

# Fetch all available data for NVDA
result = client.get_loan_data("NVDA")
print(result["metadata"])
# {'total_records': 1650, 'tickers_found': ['NVDA'], ...}

# Multiple tickers with a date range
result = client.get_loan_data(
    ["AAPL", "MSFT", "NVDA"],
    start_date="2024-01-01",
    end_date="2024-12-31",
)

# Load directly into a pandas DataFrame
df = client.get_dataframe(["TSLA", "GME"], start_date="2021-01-01")
print(df.head())
```

## API Reference

### `OCCLoansClient(base_url, timeout)`

| Parameter  | Default                      | Description                     |
|------------|------------------------------|---------------------------------|
| `base_url` | `https://occloans.com/api`   | API base URL                    |
| `timeout`  | `30`                         | Request timeout in seconds      |

---

### `get_loan_data(tickers, start_date, end_date, data_type) → dict`

Fetch loan data as a parsed JSON dict.

| Parameter    | Type                  | Required | Default    | Description                          |
|--------------|-----------------------|----------|------------|--------------------------------------|
| `tickers`    | `str` or `list[str]`  | Yes      | —          | One or more ticker symbols           |
| `start_date` | `str` or `date`       | No       | 2018-09-07 | Start date (YYYY-MM-DD)              |
| `end_date`   | `str` or `date`       | No       | latest     | End date (YYYY-MM-DD)                |
| `data_type`  | `str`                 | No       | `"both"`   | `"market"`, `"hedge"`, or `"both"`   |

Returns a dict with keys:
- `metadata` — record count, tickers found, date range
- `data` — list of records with `Symbol`, `Date`, `Market Loan-Loan Balance`, `Hedge Loan Balance`

---

### `get_loan_data_csv(tickers, start_date, end_date, data_type) → str`

Same as `get_loan_data` but returns raw CSV text. Useful for writing to disk or loading into pandas/Excel.

---

### `get_dataframe(tickers, start_date, end_date, data_type) → pandas.DataFrame`

Fetches CSV and returns a pandas DataFrame with a `DatetimeIndex`. Requires `pandas`.

---

### `get_tickers() → list[str]`

Returns all ticker symbols available in the dataset (thousands of securities).

---

### `health() → dict`

Returns API health status and total record count.

---

### `stats() → dict`

Returns aggregate usage statistics — most queried tickers, daily request counts, hourly patterns. No personal data.

## Examples

### Save historical data to CSV

```python
client = OCCLoansClient()
csv_text = client.get_loan_data_csv("AAPL")
with open("aapl_all_time.csv", "w") as f:
    f.write(csv_text)
```

### Analyze borrow trends with pandas

```python
import pandas as pd
from occ_loans import OCCLoansClient

client = OCCLoansClient()
df = client.get_dataframe("GME", start_date="2021-01-01", end_date="2021-12-31")

# Plot hedge loan balance over time
df_gme = df[df["Symbol"] == "GME"].set_index("Date")
df_gme["Hedge Loan Balance"].plot(title="GME Hedge Loan Balance 2021")
```

### Screen for rising short interest

See [`examples/short_squeeze_screener.py`](examples/short_squeeze_screener.py) for a complete screener that identifies tickers with significantly rising borrow balances over the past 30 trading days.

```bash
python examples/short_squeeze_screener.py
```

```
── Short Squeeze Candidates (Rising Borrow Trend) ──────────────────
Ticker      Latest Balance    30-Day Change        As Of
──────────────────────────────────────────────────────────
GME               $684.3M            +12.4%   2026-04-15
TSLA               $1.62B             +9.1%   2026-04-15
RIVN              $312.5M             +7.8%   2026-04-15
...
```

## Data Coverage

| Detail            | Value                              |
|-------------------|------------------------------------|
| Start date        | September 7, 2018                  |
| Update frequency  | Daily, after market close (~8PM ET)|
| Securities        | Thousands of US equities           |
| Data source       | Options Clearing Corporation (OCC) |
| Cost              | Free, no API key required          |

## Related Links

- **Web interface & interactive charts:** [occloans.com](https://occloans.com)
- **Full API documentation:** [occloans.com/#api](https://occloans.com/#api)
- **Data source:** [OCC Stock Loan Volume Reports](https://www.theocc.com/market-data/market-data-reports/volume-and-open-interest/stock-loan-volume)

## Disclaimer

OCC Loans data is for informational and educational purposes only. Nothing in this repository or on occloans.com constitutes investment advice. This project is not affiliated with the Options Clearing Corporation.
