import asyncio
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone
import os

from ingestion.market_data import MarketDataIngestor
from ingestion.fundamental import NewsIngestor
from agents.genai_agent import FundamentalAgent

async def run_benchmark():
    print("--- TASK 1: BENCHMARK ---")
    ticker = "SPY"
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    market_ingestor = MarketDataIngestor()
    df = await market_ingestor.fetch_ohlcv(ticker, start_date, end_date)
    
    if df.empty:
        print("Market data fetch failed.")
        return

    # Calculate returns
    df['returns'] = df['Close'].pct_change()
    
    # Calculate Total Cumulative Return
    total_return = df['Close'].iloc[-1] / df['Close'].iloc[0] - 1
    
    # Calculate Sharpe Ratio (risk-free=0)
    mean_return = df['returns'].mean()
    std_return = df['returns'].std()
    sharpe = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
    
    print(f"Total Cumulative Return: {total_return:.4%}")
    print(f"Sharpe Ratio (Annualized): {sharpe:.4f}")

async def run_news():
    print("\n--- TASK 2: GENAI CRASH DIAGNOSTIC ---")
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = 'dummy_key'
        
    ticker = "SPY"
    news_ingestor = NewsIngestor()
    news = await news_ingestor.fetch_news(ticker)
    
    if not news:
        print("No news retrieved from yfinance.")
    else:
        # Check dates available
        dates = [item.get('parsed_publish_time') for item in news if 'parsed_publish_time' in item]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            print(f"News available from {min_date.date()} to {max_date.date()}")
            
            # See if we actually have news for 2024-07-25 to 2024-08-02
            target_news = [
                n for n in news 
                if n.get('parsed_publish_time') and 
                pd.Timestamp('2024-07-25', tz='UTC') <= n['parsed_publish_time'] <= pd.Timestamp('2024-08-02', tz='UTC')
            ]
            print(f"News count in target window (July 25 - Aug 2, 2024): {len(target_news)}")
            
            if len(target_news) == 0:
                print("WARNING: yfinance API does not provide historical news for this specific window in the past.")
        else:
            print("No parsed dates available.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
    asyncio.run(run_news())
