import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import asyncio
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from ingestion.market_data import MarketDataIngestor
from ingestion.fundamental import NewsIngestor, NewsProvider

class MockFailingTicker:
    def __init__(self, fail_count):
        self.fail_count = fail_count
        self.attempts = 0
        
    def history(self, *args, **kwargs):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise HTTPError("Rate limited")
        
        # Return a simple dataframe
        dates = pd.date_range('2023-01-01', '2023-01-10')
        return pd.DataFrame({
            'Close': np.random.rand(10) * 100
        }, index=dates)

@pytest.fixture
def sample_ohlcv():
    dates = pd.date_range('2023-01-01', periods=50, freq='B')
    df = pd.DataFrame({
        'Close': np.linspace(100, 150, 50) + np.random.normal(0, 2, 50)
    }, index=dates)
    return df

@pytest.mark.asyncio
async def test_exponential_backoff():
    # V-01 (Rate Limit) test
    ingestor = MarketDataIngestor()
    
    mock_ticker = MockFailingTicker(fail_count=3)
    
    with patch('ingestion.market_data.yf.Ticker') as mock_yf:
        mock_yf.return_value = mock_ticker
        
        df = await ingestor.fetch_ohlcv('AAPL', '2023-01-01', '2023-01-10')
        
        assert not df.empty
        assert mock_ticker.attempts == 4 # 3 fails + 1 success

def test_data_integrity_forward_fill():
    # V-03
    ingestor = MarketDataIngestor()
    
    dates = pd.date_range('2023-01-01', periods=5)
    df = pd.DataFrame({'Close': [100, np.nan, np.nan, np.nan, 105]}, index=dates)
    
    cleaned = ingestor._clean_data(df)
    
    # 3 NaNs should be forward filled
    assert not cleaned['Close'].isna().any()
    assert len(cleaned) == 5
    assert cleaned['Close'].iloc[2] == 100

def test_target_shift_lookahead_bias(sample_ohlcv):
    # V-02 Lookahead bias test
    ingestor = MarketDataIngestor()
    
    processed = ingestor.align_for_prediction(sample_ohlcv)
    
    # We should have dropped the last 21 rows because we shifted -21
    assert len(processed) == len(sample_ohlcv) - 21
    
    rv_df = ingestor.calculate_realized_volatility(sample_ohlcv.copy())
    
    # target at index 0 should equal realized vol at index 21
    assert processed['Target_Vol_Future'].iloc[0] == rv_df['Realized_Vol'].iloc[21]
    
@pytest.mark.asyncio
async def test_news_timestamps():
    class MockNewsProvider:
        def get_news(self, ticker):
            return [
                {'providerPublishTime': 1672531200}, # 2023-01-01
                {'providerPublishTime': 1672617600}, # 2023-01-02
            ]
            
    ingestor = NewsIngestor(provider=MockNewsProvider())
    news = await ingestor.fetch_news('AAPL')
    
    assert len(news) == 2
    assert 'parsed_publish_time' in news[0]
    assert news[0]['parsed_publish_time'] == pd.to_datetime(1672531200, unit='s', utc=True)
