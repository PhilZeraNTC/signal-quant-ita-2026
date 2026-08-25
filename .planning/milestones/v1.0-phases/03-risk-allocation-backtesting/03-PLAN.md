---
wave: 1
depends_on: ["01-data-ingestion", "02-quant-fundamental-agents"]
files_modified:
  - core/backtester.py
  - agents/risk_agent.py
  - main.py
autonomous: true
---

# Phase 3 Plan: Risk Allocation & Backtesting

**Phase Goal**: As a quant researcher, I want to run a point-in-time backtest of a risk-allocated portfolio using my generated volatility and sentiment signals, so that I can evaluate its risk-adjusted performance.
**MVP Mode**: ENABLED (Vertical Slices)
**Tracer Mode**: ENABLED

> **Note**: probe fallback disabled (`workflow.specless_probe_fallback=false`); no probe-derived predicates generated for SPEC-absent sections this run.

## Tasks

<task id="base-backtest-tracer" type="tracer">
  <name>Tracer: Base Volatility Targeting Backtest</name>
  <description>Implement the point-in-time backtester event loop streaming data point-by-point. Calculate base volatility targeting allocation, execute trades with flat transaction costs, and output performance metrics.</description>
  <wave>1</wave>
  <dependencies></dependencies>
  <read_first>Read `core/backtester.py` and `agents/risk_agent.py` (or create them). Review `.planning/phases/03-risk-allocation-backtesting/03-CONTEXT.md` (Decision 3 & 4).</read_first>
  <action>
    1. Create `core/backtester.py` with an asynchronous event-driven loop (using `asyncio`) that streams data point-by-point (t_close for signal, t+1_open for execution).
    2. Create `agents/risk_agent.py` and implement `allocate_capital` as an async function using inverse volatility (Volatility Targeting formula: `Base_Weight = Target_Vol / Forecast_Vol`, using an annualized Target Volatility constant of 0.15).
    3. Add transaction cost modeling (flat bps) in the backtester logic.
    4. Calculate Sharpe Ratio and Max Drawdown at the end of the simulation.
    5. Wire it all together in an executable script using `asyncio.run()` to ensure an end-to-end run works.
  </action>
  <acceptance_criteria>
    1. The backtester strictly iterates point-by-point and separates t_close (signal) from t+1_open (execution).
    2. Capital is allocated using the Volatility Targeting formula (`Base_Weight = Target_Vol / Forecast_Vol` with Target_Vol=0.15) over the 21-day realized volatility.
    3. Each trade incurs a flat basis point transaction cost.
    4. The simulation outputs a mathematically valid Sharpe Ratio and Max Drawdown.
    5. <checkpoint:decision> Is the event loop cleanly separating data streaming from signal generation to guarantee zero lookahead bias?</checkpoint:decision>
  </acceptance_criteria>
</task>

<task id="sentiment-tilt" type="feature">
  <name>Sentiment Tilt Integration</name>
  <description>Incorporate the fundamental agent's sentiment score into the capital allocation via a multiplicative modifier.</description>
  <wave>2</wave>
  <dependencies>base-backtest-tracer</dependencies>
  <read_first>Review `.planning/phases/03-risk-allocation-backtesting/03-CONTEXT.md` (Decision 1). Read `agents/risk_agent.py`.</read_first>
  <action>
    1. Update `agents/risk_agent.py` to accept a sentiment score and conviction factor asynchronously.
    2. Apply the multiplicative modifier: `base_weight * (1 + sentiment * conviction_factor)`.
    3. Ensure the asynchronous backtester loop correctly awaits and passes the sentiment score to the risk agent during the simulation.
  </action>
  <acceptance_criteria>
    1. The final allocation weight is correctly adjusted by the sentiment score using the specified multiplicative modifier formula.
    2. The backtest execution loop reflects the sentiment-adjusted weights in its capital allocation.
  </acceptance_criteria>
</task>

<task id="risk-bands" type="feature">
  <name>Risk Bands Enforcement</name>
  <description>Strictly enforce a limit of 1-2 portfolio adjustments per month to control turnover.</description>
  <wave>2</wave>
  <dependencies>base-backtest-tracer</dependencies>
  <read_first>Review `.planning/phases/03-risk-allocation-backtesting/03-CONTEXT.md` (Decision 2). Read `agents/risk_agent.py`.</read_first>
  <action>
    1. Implement state tracking asynchronously in `agents/risk_agent.py` (or the backtester) to count portfolio adjustments within a rolling 21 trading days window without blocking the event loop.
    2. When a new signal triggers, asynchronously check if the rolling 21-day adjustment limit (e.g., 2) has been reached.
    3. If the limit is reached, hard enforce it by ignoring the signal and maintaining the previous allocation.
  </action>
  <acceptance_criteria>
    1. The system tracks the number of trades/adjustments per rolling 21 trading days window.
    2. Signals are strictly ignored if the rolling 21-day limit of 1-2 adjustments is already reached.
    3. Backtest logs or outputs verify that the turnover limit is never breached.
    4. <checkpoint:decision> DECISION RESOLVED: Tracking adjustments per rolling 21 trading days window (rejecting calendar month approach).</checkpoint:decision>
  </acceptance_criteria>
</task>

## Verification Criteria

- **Functional Verification**: The backtester can execute a full run from start to finish without errors, outputting a Sharpe Ratio and Max Drawdown.
- **Data Integrity Verification**: The backtester strictly streams data point-by-point, with no lookahead bias between t_close signals and t+1_open execution.
- **Logic Verification**: The final portfolio weights correctly reflect inverse volatility targeting, adjusted by the sentiment tilt, and constrained by the monthly turnover limit.

## Must Haves (Goal-Backward Verification)

- **Must have** a point-in-time event-driven loop in `core/backtester.py`.
- **Must have** inverse volatility allocation in `agents/risk_agent.py`.
- **Must have** sentiment tilt via multiplicative modifier implemented.
- **Must have** a hard-enforced risk band limiting trades to 1-2 per rolling 21 trading days.
- **Must have** flat basis points transaction costs applied to trades.
- **Must have** Sharpe Ratio and Max Drawdown calculations.

## Artifacts this phase produces

- `core/backtester.py`: Contains the `Backtester` class with an async `run_backtest` point-in-time event loop, `execute_trade` logic, transaction costs, and metric calculations (`calculate_sharpe_ratio`, `calculate_max_drawdown`).
- `agents/risk_agent.py`: Contains the `RiskAgent` class with the async `allocate_capital` function (volatility targeting, sentiment tilt, risk bands).
- `main.py`: Contains the async `main` function and `asyncio.run(main())` entry point, wired together to run the backtest end-to-end.
