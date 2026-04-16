"""
occ_loans.py - Python client for the OCC Loans API

Fetch historical OCC Stock Loan Program data for any ticker or date range.
Data covers September 2018 to present, updated daily after market close.

API documentation: https://occloans.com/#api
"""

import requests
from datetime import date, datetime

BASE_URL = "https://occloans.com/api"


class OCCLoansClient:
    """
    Client for the OCC Loans REST API.

    No API key or authentication required. All endpoints are publicly accessible.

    Example:
        client = OCCLoansClient()
        df = client.get_loan_data(["AAPL", "NVDA"], start_date="2024-01-01")
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "occ-loans-python/1.0"})

    # ------------------------------------------------------------------
    # Core endpoint
    # ------------------------------------------------------------------

    def get_loan_data(
        self,
        tickers: list[str] | str,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        data_type: str = "both",
    ) -> dict:
        """
        Fetch stock loan data for one or more tickers.

        Args:
            tickers:    Ticker symbol(s) — string or list of strings.
            start_date: Start date (YYYY-MM-DD string or date object). Defaults to
                        earliest available (September 7, 2018).
            end_date:   End date (YYYY-MM-DD string or date object). Defaults to
                        most recent trading day.
            data_type:  "market", "hedge", or "both" (default).

        Returns:
            Parsed JSON response dict with keys "metadata" and "data".

        Raises:
            requests.HTTPError: on non-2xx responses.
            ValueError: if tickers is empty.
        """
        if isinstance(tickers, str):
            tickers = [tickers]
        if not tickers:
            raise ValueError("At least one ticker is required.")

        params = {
            "tickers": ",".join(t.upper() for t in tickers),
            "data_type": data_type,
            "format": "json",
        }
        if start_date is not None:
            params["start_date"] = _format_date(start_date)
        if end_date is not None:
            params["end_date"] = _format_date(end_date)

        resp = self.session.get(
            f"{self.base_url}/loan-data", params=params, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_loan_data_csv(
        self,
        tickers: list[str] | str,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        data_type: str = "both",
    ) -> str:
        """
        Fetch stock loan data as raw CSV text.

        Useful for loading directly into pandas or writing to disk.

        Returns:
            CSV string.
        """
        if isinstance(tickers, str):
            tickers = [tickers]
        if not tickers:
            raise ValueError("At least one ticker is required.")

        params = {
            "tickers": ",".join(t.upper() for t in tickers),
            "data_type": data_type,
            "format": "csv",
        }
        if start_date is not None:
            params["start_date"] = _format_date(start_date)
        if end_date is not None:
            params["end_date"] = _format_date(end_date)

        resp = self.session.get(
            f"{self.base_url}/loan-data", params=params, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.text

    # ------------------------------------------------------------------
    # Utility endpoints
    # ------------------------------------------------------------------

    def get_tickers(self) -> list[str]:
        """Return all available ticker symbols in the dataset."""
        resp = self.session.get(f"{self.base_url}/tickers", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get("tickers", [])

    def health(self) -> dict:
        """Return API health status and basic system info."""
        resp = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def stats(self) -> dict:
        """Return aggregate usage statistics (no personal data)."""
        resp = self.session.get(f"{self.base_url}/stats", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # pandas helpers (optional — only imported if pandas is installed)
    # ------------------------------------------------------------------

    def get_dataframe(
        self,
        tickers: list[str] | str,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        data_type: str = "both",
    ):
        """
        Fetch loan data and return a pandas DataFrame.

        Requires pandas to be installed (`pip install pandas`).

        The DataFrame is indexed by Date with columns for each ticker's
        hedge and/or market loan balance.

        Returns:
            pandas.DataFrame with a DatetimeIndex.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for get_dataframe(). Install it with: pip install pandas")

        csv_text = self.get_loan_data_csv(
            tickers, start_date=start_date, end_date=end_date, data_type=data_type
        )
        import io
        df = pd.read_csv(io.StringIO(csv_text))
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(["Symbol", "Date"]).reset_index(drop=True)
        return df


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _format_date(d: str | date) -> str:
    if isinstance(d, str):
        # Validate format
        datetime.strptime(d, "%Y-%m-%d")
        return d
    return d.strftime("%Y-%m-%d")
