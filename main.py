import asyncio
import logging
from core.backtester import Backtester
from agents.risk_agent import RiskAgent
from agents.quant_agent import QuantAgent
from agents.genai_agent import FundamentalAgent
from ingestion.market_data import MarketDataIngestor
from ingestion.fundamental import NewsIngestor, YFinanceNewsProvider
from core.orchestrator import Orchestrator
import pandas as pd
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    ticker = "SPY"
    start_date = "2020-01-01"
    end_date = "2024-12-31"
    backtest_start_date = "2024-01-01"

    # Set dummy api key if not found, to allow simulation to proceed.
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = "dummy_key"

    logger.info("Initializing ingestors...")
    market_ingestor = MarketDataIngestor()
    news_ingestor = NewsIngestor()

    logger.info("Fetching market data...")
    market_data = await market_ingestor.fetch_ohlcv(ticker, start_date, end_date)
    
    if market_data.empty:
        logger.error("Failed to fetch market data. Fallback to dummy data for testing.")
        # Fallback to allow pipeline to run if offline or rate limited
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        market_data = pd.DataFrame({
            'Open': 100.0, 'High': 105.0, 'Low': 95.0, 'Close': 100.0, 'Volume': 1000
        }, index=dates)
        
    market_data = market_ingestor.calculate_realized_volatility(market_data)

    logger.info("Fetching news data...")
    news_data = await news_ingestor.fetch_news(ticker)

    logger.info("Initializing agents...")
    quant_agent = QuantAgent()
    fundamental_agent = FundamentalAgent()
    risk_agent = RiskAgent(target_vol=0.15)
    
    logger.info("Initializing orchestrator...")
    orchestrator = Orchestrator(
        ticker=ticker,
        market_data=market_data,
        news_data=news_data,
        backtest_start_date=backtest_start_date,
        quant_agent=quant_agent,
        fundamental_agent=fundamental_agent
    )

    logger.info("Training QuantAgent on historical data...")
    orchestrator.prepare_agents()

    logger.info("Running backtester...")
    backtester = Backtester(initial_capital=10000.0, transaction_cost_bps=5.0)
    
    stream = orchestrator.generate_events()
    await backtester.run_backtest(stream, risk_agent)
    
    sharpe, mdd = backtester.calculate_metrics()
    logger.info("Backtest Complete.")
    print(f"Sharpe Ratio: {sharpe:.4f}")
    print(f"Max Drawdown: {mdd:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
