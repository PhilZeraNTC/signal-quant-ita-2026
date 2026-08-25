# Phase 1: Data Ingestion - Plan

## Phase Goal
Establish reliable, lookahead-free market data and sentiment news ingestion using `yfinance`.

## Step-by-Step Implementation Plan

### 1. Requirements Setup
- Update `requirements.txt` with required libraries (`yfinance`, `pandas`, `numpy`, `tenacity`).

### 2. Market Data Ingestion (`ingestion/market_data.py`)
- Implement `MarketDataIngestor` class.
- Create an async method `fetch_ohlcv(ticker, start_date, end_date)`.
- Use `asyncio.to_thread` to wrap `yfinance.Ticker(ticker).history(auto_adjust=True)` to handle corporate events (splits/dividends).
- Decorate with `@retry` from `tenacity` for exponential backoff (catch `HTTPError` 429).
- Apply data integrity checks (forward-fill missing data up to 3 days).

### 3. Log Returns and RV Calculation (`ingestion/market_data.py`)
- Implement `calculate_log_returns(df)`: `np.log(df['Close'] / df['Close'].shift(1))`
- Implement `calculate_realized_volatility(df)`: rolling 21-day std dev annualized `* np.sqrt(252)`.
- Implement `align_for_prediction(df)`: Shift target variables to strictly enforce t_close data being used to predict future 21-day volatility. Explicitly: `df['Target_Vol_Future'] = df['Realized_Vol'].shift(-21)`.

### 4. Fundamental News Ingestion (`ingestion/fundamental.py`)
- Implement `NewsIngestor` class with dependency injection (e.g., passing a data source provider) so it can consume local CSV datasets for backtesting later instead of hardcoding `yfinance`.
- Create async method `fetch_news(ticker)`.
- Use `asyncio.to_thread` to wrap `yfinance.Ticker(ticker).news` when using the yfinance provider.
- Parse the `providerPublishTime` carefully. Discard or properly flag any news published after `t_close` if evaluating on day `t`.

### 5. Unit Testing
- Write tests mocking `yfinance` to simulate rate limits.
- Assert exponential backoff behaves correctly (Validation V-01).
- Assert lookahead bias check (Validation V-02).
- Assert missing data behavior (Validation V-03).
