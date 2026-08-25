# Phase 04: Close gap: End-to-End Orchestration and Wiring

## Domain
E2E Pipeline Orchestration linking Market Data & News to Quant & Fundamental Agents, and then feeding those predictions into the RiskAgent & Backtester, all while enforcing `t_close` causality.

## Canonical Refs
- Phase 04 ROADMAP.md details
- Requirements INGEST-01, INGEST-02, INGEST-03, QUANT-01, FUND-02, RISK-01, RISK-02, BACK-01, BACK-02

## Decisions

### Pipeline Driver
The orchestrator will act as an async generator that yields daily events, which fits perfectly with the existing `Backtester.run_backtest(stream)` signature. We will not use async queues.

### Training vs Simulation
We will trigger a distinct "historical training phase" upfront to fit the QuantAgent (LightGBM) model on the full historical dataset. After the model is fitted, the orchestrator will start the daily event loop to simulate predictions one day at a time point-in-time.

### Data Passing
The orchestrator will hold the ingested DataFrames (Market data and News data) entirely in memory and pass them directly to the agents. We will avoid writing them to temporary disk or databases to maintain the simple, zero-budget approach.

## Code Context
- `main.py` currently mocks the pipeline via `mock_data_stream`.
- `core/orchestrator.py` exists but is empty and will now house the actual `Orchestrator` class replacing the mock behavior.
