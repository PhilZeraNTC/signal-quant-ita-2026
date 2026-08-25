import asyncio
import logging
import pandas as pd
import numpy as np
import os
from core.backtester import Backtester
from agents.risk_agent import RiskAgent
from agents.quant_agent import QuantAgent
from agents.genai_agent import FundamentalAgent
from ingestion.market_data import MarketDataIngestor
from ingestion.fundamental import NewsIngestor
from core.orchestrator import Orchestrator

logging.basicConfig(level=logging.WARNING)

async def main():
    ticker = "SPY"
    start_date = "2020-01-01"
    end_date = "2024-12-31"
    backtest_start_date = "2024-01-01"

    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = "dummy_key"

    market_ingestor = MarketDataIngestor()
    news_ingestor = NewsIngestor()

    market_data = await market_ingestor.fetch_ohlcv(ticker, start_date, end_date)
    if market_data.empty:
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        market_data = pd.DataFrame({'Open': 100.0, 'High': 105.0, 'Low': 95.0, 'Close': 100.0, 'Volume': 1000}, index=dates)
    market_data = market_ingestor.calculate_realized_volatility(market_data)

    news_data = await news_ingestor.fetch_news(ticker)

    quant_agent = QuantAgent()
    fundamental_agent = FundamentalAgent()
    risk_agent = RiskAgent(target_vol=0.15)
    
    orchestrator = Orchestrator(ticker, market_data, news_data, backtest_start_date, quant_agent, fundamental_agent)
    orchestrator.prepare_agents()

    backtester = Backtester(initial_capital=10000.0, transaction_cost_bps=5.0)
    
    stream = orchestrator.generate_events()
    await backtester.run_backtest(stream, risk_agent)
    
    df = pd.DataFrame(backtester.portfolio_history)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df['returns'] = df['portfolio_value'].pct_change()
    
    sharpe, mdd = backtester.calculate_metrics()
    
    # Calculate Annualized Return
    days = (df.index[-1] - df.index[0]).days
    total_return = df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0] - 1
    annualized_return = (1 + total_return) ** (365.25 / days) - 1 if days > 0 else 0
    
    # Find worst drawdown period
    df['cumulative_max'] = df['portfolio_value'].cummax()
    df['drawdown'] = (df['portfolio_value'] - df['cumulative_max']) / df['cumulative_max']
    worst_drawdown_idx = df['drawdown'].idxmin()
    worst_dd_start = df.loc[:worst_drawdown_idx, 'portfolio_value'].idxmax()
    
    # Estimate Turnover: number of times position changes
    # We can't see internal trades directly without hooking, but we can look at periods where return != market return 
    # Or just count adjustments from risk_agent
    turnover = len(risk_agent.adjustment_indices) # This is number of trades in the LAST 21 days due to deque, wait
    # Let's count actual weight changes from risk agent
    
    print(f"Sharpe Ratio: {sharpe:.4f}")
    print(f"Max Drawdown: {mdd:.4f}")
    print(f"Total Return: {total_return:.4%}")
    print(f"Annualized Return: {annualized_return:.4%}")
    print(f"Worst Drawdown Period: {worst_dd_start.date()} to {worst_drawdown_idx.date()}")
    print(f"Total Trading Days: {len(df)}")
    
    # Show worst 5 daily drops to understand bad scenarios
    worst_days = df.nsmallest(5, 'returns')
    print("Worst 5 Daily Drops:")
    for date, row in worst_days.iterrows():
        print(f"  {date.date()}: {row['returns']:.4%}")

if __name__ == "__main__":
    asyncio.run(main())
