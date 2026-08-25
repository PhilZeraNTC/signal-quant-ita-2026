import asyncio
import logging
from typing import List, Dict, Any, Protocol
import yfinance as yf
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class NewsProvider(Protocol):
    def get_news(self, ticker: str) -> List[Dict[str, Any]]:
        ...

class YFinanceNewsProvider:
    def get_news(self, ticker: str) -> List[Dict[str, Any]]:
        ticker_obj = yf.Ticker(ticker)
        return ticker_obj.news

class LocalCSVNewsProvider:
    def __init__(self, file_path: str):
        self.df = pd.read_csv(file_path)
        
    def get_news(self, ticker: str) -> List[Dict[str, Any]]:
        ticker_news = self.df[self.df['ticker'] == ticker]
        return ticker_news.to_dict('records')

class NewsIngestor:
    def __init__(self, provider: NewsProvider = None):
        # Dependency injection for testability/backtesting
        self.provider = provider or YFinanceNewsProvider()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def _fetch_news_sync(self, ticker: str) -> List[Dict[str, Any]]:
        return self.provider.get_news(ticker)

    async def fetch_news(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Asynchronously fetches news.
        """
        try:
            news_items = await asyncio.to_thread(self._fetch_news_sync, ticker)
        except Exception as e:
            logger.error(f"Failed to fetch news for {ticker}: {e}")
            return []
            
        processed_news = self._parse_news(news_items)
        return processed_news

    def _parse_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract strict publication timestamps.
        """
        processed = []
        for item in news_items:
            # yfinance returns providerPublishTime as a unix timestamp
            pub_time = item.get('providerPublishTime')
            if pub_time:
                # Convert to pandas datetime for easier comparisons later against t_close
                pub_datetime = pd.to_datetime(pub_time, unit='s', utc=True)
                item['parsed_publish_time'] = pub_datetime
                processed.append(item)
                
        return processed
