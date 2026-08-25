---
phase: 03-risk-allocation-backtesting
plan: 03
subsystem: backtesting
tags: [backtester, risk, volatility-targeting, sentiment-tilt]

requires:
  - phase: 01-data-ingestion
    provides: market data, sentiment scores
  - phase: 02-quant-fundamental-agents
    provides: volatility forecasts, sentiment convictions
provides:
  - Base backtester event loop with t_close/t+1_open point-in-time constraints
  - Volatility targeting capital allocation
  - Sentiment tilt via multiplicative modifier
  - Risk bands enforcing 2 adjustments per 21 trading days
  - Sharpe Ratio and Max Drawdown calculation
affects: []

actuals:
  tokens: 1500
  tasks: 3
  commits: 3

tech-stack:
  added: [pandas, numpy, asyncio]
  patterns: [point-in-time backtesting, event-driven async loops, inverse volatility targeting]

key-files:
  created: [core/backtester.py, agents/risk_agent.py, main.py]
  modified: []

key-decisions:
  - "Multiplicative modifier used for sentiment tilt"
  - "Rolling 21 trading days integer index used for risk bands limits instead of calendar dates"
  - "Fractional shares assumed for backtester simplicity"

patterns-established:
  - "Point-in-time strictness: signals at t_close, execution at t_plus_1_open"

requirements-completed: []

coverage: []

duration: 10min
completed: 2026-08-11
status: complete
---

# Phase 03: Risk Allocation & Backtesting Summary

**Point-in-time async backtester with inverse volatility targeting, sentiment tilt, and risk bands**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-11T15:51:00-03:00
- **Completed:** 2026-08-11T16:01:00-03:00
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Implemented base `Backtester` with async point-in-time event loop.
- Developed `RiskAgent` allocating capital via inverse volatility (`Target_Vol / Forecast_Vol`).
- Integrated sentiment tilt using `base_weight * (1 + sentiment * conviction_factor)`.
- Enforced risk bands limiting trades to 2 adjustments per rolling 21 trading days.
- Added flat bps transaction cost modeling and key risk metrics (Sharpe, MDD).
- Created executable `main.py` entrypoint.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: Base Volatility Targeting Backtest** - `54f32f4`
2. **Task 2: Sentiment Tilt Integration** - `f7e72b9` 
3. **Task 3: Risk Bands Enforcement** - `0ff779d`

## Files Created/Modified
- `core/backtester.py` - Async backtester event loop and trade execution
- `agents/risk_agent.py` - Capital allocation, sentiment tilt, and risk band tracking
- `main.py` - Backtest simulation script with mock data stream

## Decisions Made
- Used integer index for 21-day rolling window in `RiskAgent` rather than calendar dates to align directly with backtest event loop.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness
Backtester and risk allocation components are ready for real data streams.

---
*Phase: 03-risk-allocation-backtesting*
*Completed: 2026-08-11*
