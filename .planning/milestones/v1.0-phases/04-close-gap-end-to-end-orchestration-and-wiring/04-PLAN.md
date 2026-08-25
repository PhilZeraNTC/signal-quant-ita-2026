---
wave: 04
depends_on:
  - phase: 03-risk-allocation-backtesting
files_modified:
  - core/orchestrator.py
  - main.py
autonomous: true
---

# Phase 04: Close gap: End-to-End Orchestration and Wiring

**⚠ probe fallback disabled (workflow.specless_probe_fallback=false): no probe-derived predicates generated for SPEC-absent sections this run.**

## 1. Goal
Implement the End-to-End Pipeline Orchestration to link Market Data & News to Quant & Fundamental Agents, and feed predictions into the RiskAgent & Backtester, enforcing `t_close` causality, fulfilling the missing requirements identified in the milestone audit.

## 2. Approach
- **In-Memory Data Handling:** Orchestrator will hold DataFrames in memory and pass directly to agents.
- **Historical Training Phase:** Trigger training of QuantAgent on historical data upfront.
- **Async Generator Driver:** The orchestrator will use an async generator to yield daily events to match `Backtester.run_backtest(stream)` signature. No async queues.
- **Wiring:** `main.py` will be rewritten to drop mocks, invoke ingestors, create the orchestrator, and feed the backtester.

## 3. Tasks

### Wave 1: Orchestrator Base Setup

<task>
  <read_first>
    - .planning/phases/04-close-gap-end-to-end-orchestration-and-wiring/04-CONTEXT.md
    - .planning/v1.0-MILESTONE-AUDIT.md
    - core/orchestrator.py
    - agents/quant_agent.py
  </read_first>
  <acceptance_criteria>
    - `core/orchestrator.py` contains the `Orchestrator` class.
    - `Orchestrator` has an initialization or setup method that accepts in-memory `market_data` and `news_data`.
    - `Orchestrator` explicitly invokes `QuantAgent.train()` (or equivalent method) with the historical dataset before event generation begins.
    - Resolves requirements: INGEST-01, INGEST-02.
  </acceptance_criteria>
  <action>
    Implement the base `Orchestrator` class in `core/orchestrator.py`. Design it to receive the fully ingested `market_data` and `news_data` DataFrames, along with a `backtest_start_date` parameter (e.g., '2024-01-01'). Add a method `prepare_agents` that extracts all market data strictly before this date and calls the LightGBM `QuantAgent`'s training method so the model is fitted prior to the daily simulation. The `generate_events()` async generator will then begin iterating exactly on this `backtest_start_date`, ensuring absolute zero lookahead bias.
  </action>
</task>

### Wave 2: Async Event Generator

<task>
  <read_first>
    - core/orchestrator.py
    - core/backtester.py
    - agents/genai_agent.py
    - agents/quant_agent.py
  </read_first>
  <acceptance_criteria>
    - `Orchestrator` exposes an async generator method `generate_events()`.
    - `generate_events()` yields point-in-time daily events suitable for `Backtester.run_backtest(stream)`.
    - Each yielded event includes real forecast volatility from `QuantAgent` and sentiment from `FundamentalAgent` using strictly data up to `t_close`.
    - Slicing strictly isolates data up to `t_close` to prevent lookahead bias.
    - Resolves requirements: INGEST-03, QUANT-01, FUND-02.
  </acceptance_criteria>
  <action>
    Implement the `generate_events` async generator in `core/orchestrator.py`. Iterate day-by-day over the simulation period. For each day (`t_close`), slice the market and news data to include only data up to that day. Pass the sliced data to `QuantAgent.predict()` and `FundamentalAgent.predict()` (or equivalent methods). Package these outputs into a daily event object/dict and `yield` it. This structure directly satisfies the backtester's expectation of a stream.
  </action>
</task>

### Wave 3: Main Wiring

<task>
  <read_first>
    - main.py
    - ingestion/market_data.py
    - ingestion/fundamental.py
    - core/backtester.py
  </read_first>
  <acceptance_criteria>
    - `main.py` instantiates `MarketDataIngestor` and `NewsIngestor` and fetches real data.
    - `mock_data_stream` is completely removed.
    - `main.py` instantiates the `Orchestrator` and passes the real data to it.
    - `main.py` passes the orchestrator's event generator to `Backtester.run_backtest()`.
    - The program executes end-to-end and outputs portfolio metrics (Sharpe, MDD).
    - Resolves requirements: RISK-01, RISK-02, BACK-01, BACK-02.
  </acceptance_criteria>
  <action>
    Rewrite `main.py` to remove the mock pipeline. Setup the ingestors to download data. Initialize the `Orchestrator`, `QuantAgent`, `FundamentalAgent`, `RiskAgent`, and `Backtester`. Wire the data from ingestion to the orchestrator, and feed the orchestrator's event stream into the backtester. Run the pipeline end-to-end and log the final Sharpe Ratio and Max Drawdown.
  </action>
</task>

## 4. Verification

- **Code Review:** Verify that `main.py` uses real classes and no mock components.
- **Execution:** Running `python main.py` completes without errors and prints realistic Sharpe Ratio and MDD.
- **Data Integrity:** Verify through code inspection that `generate_events` correctly slices data up to the current loop date before passing it to agent prediction methods.

### must_haves
- Async generator used for the event stream in Orchestrator.
- Historical training phase occurs before the backtest loop starts.
- Real data is fetched and propagated through the entire pipeline.
- End-to-end flow from ingestion to backtest execution works natively in `main.py`.
- No lookahead bias is introduced during the daily event generation.
- The following requirements are strictly fulfilled: INGEST-01, INGEST-02, INGEST-03, QUANT-01, FUND-02, RISK-01, RISK-02, BACK-01, BACK-02.

## 5. Artifacts this phase produces
- `core/orchestrator.py`: New module.
  - Class `Orchestrator`: Coordinates the data passing and event generation.
  - Method `Orchestrator.__init__`: Receives and stores in-memory data frames.
  - Method `Orchestrator.prepare_agents`: Trains the quant agent using historical data upfront.
  - Method `Orchestrator.generate_events`: Async generator yielding daily point-in-time events.
- `main.py`: Modified entrypoint replacing mock behavior with a fully wired pipeline.
