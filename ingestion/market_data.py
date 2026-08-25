import asyncio
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import HTTPError, ConnectionError

logger = logging.getLogger(__name__)

class MarketDataIngestor:
    def __init__(self, max_retries=5):
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HTTPError, ConnectionError, TimeoutError))
    )
    def _fetch_history_sync(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Synchronous fetch wrapped with tenacity for rate limits and intermittent failures.
        """
        ticker_obj = yf.Ticker(ticker)
        # auto_adjust=True handles corporate events
        df = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)
        
        if df.empty:
            logger.warning(f"No data fetched for {ticker} between {start_date} and {end_date}")
            return df
            
        return df

    async def fetch_ohlcv(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Asynchronously fetches OHLCV data.
        """
        try:
            df = await asyncio.to_thread(self._fetch_history_sync, ticker, start_date, end_date)
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {e}")
            return pd.DataFrame()
        
        if not df.empty:
            df = self._clean_data(df)
        
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Forward-fill missing data up to 3 days, then drop remaining NaNs.
        """
        # Ensure DatetimeIndex and sort
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Forward fill up to 3 consecutive days
        df = df.ffill(limit=3)
        df = df.dropna()
        
        return df

    def calculate_log_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily logarithmic returns.
        """
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column.")
            
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        return df

    def calculate_realized_volatility(self, df: pd.DataFrame, window: int = 21) -> pd.DataFrame:
        """
        Calculate annualized realized volatility over a rolling window.
        """
        if 'Log_Return' not in df.columns:
            df = self.calculate_log_returns(df)
            
        df['Realized_Vol'] = df['Log_Return'].rolling(window=window).std() * np.sqrt(252)
        return df

    def align_for_prediction(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Shift target variables to strictly enforce t_close data being used to predict 
        future 21-day volatility.
        """
        if 'Realized_Vol' not in df.columns:
            df = self.calculate_realized_volatility(df)
            
        # Target for day t is the realized volatility 21 days in the future
        # df['Realized_Vol'].shift(-21) takes the volatility calculated at t+21 and puts it on row t
        df['Target_Vol_Future'] = df['Realized_Vol'].shift(-21)
        
        # Drop rows where we don't have a future target
        df = df.dropna(subset=['Target_Vol_Future'])
        return df
