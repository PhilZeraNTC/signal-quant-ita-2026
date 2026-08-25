# Phase 1: Data Ingestion - Research

## Technical Domain
Data ingestion for a Quantitative Trading Robot using `yfinance`.

## Yfinance Async Patterns
- `yfinance` itself is fundamentally synchronous (using `requests`).
- To integrate `yfinance` in an `asyncio` architecture, calls must be offloaded to a thread pool using `asyncio.to_thread()` or `loop.run_in_executor()`.
- Historical data extraction must explicitly pass `auto_adjust=True` to handle corporate events (splits, dividends).
- Rate limiting is strict. We must implement exponential backoff (e.g., using `tenacity` or custom async loops with `asyncio.sleep()`) to avoid IP bans when fetching multiple tickers.
- News ingestion should employ dependency injection to allow swapping `yfinance` for a local CSV dataset provider during backtesting.

## Lookahead Bias Protection
- For OHLCV data, `yfinance` returns a dataframe. The index is the date/time.
- If we generate a signal for day `t`, we must strictly use data up to `t_close`.
- The execution happens at `t+1_open`.
- Therefore, the dataset fed to the quant model must ensure the target variable (future volatility) is aligned such that it only uses past information.

## Calculations
- **Log Returns:** `np.log(df['Close'] / df['Close'].shift(1))`
- **21-day Realized Volatility:** Standard deviation of log returns over a rolling 21-day window, annualized: `log_returns.rolling(window=21).std() * np.sqrt(252)`
- **Future Target Volatility:** We shift the realized volatility backwards to act as the target: `df['Target_Vol_Future'] = df['Realized_Vol'].shift(-21)`

## Validation Architecture
- Unit tests must mock `yfinance` to simulate rate-limit errors and verify the exponential backoff triggers correctly.
- Assertions must strictly check that the trailing 21-day window used for any given day `t` does not include data from `t+1`.
