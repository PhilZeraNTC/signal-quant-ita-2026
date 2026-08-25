# Signal Quant

## What This Is

A Multi-Agent Portfolio Manager operating on S&P 500 equities for the Itaú Asset Quant AI 2026 Challenge. It's written strictly in Python with an asynchronous architecture (`asyncio`) to prevent I/O bottlenecks.

## Core Value

Generate highly performant risk-adjusted returns by leveraging a LightGBM quant agent for volatility forecasting and a Gemini 1.5 Pro fundamental agent for deterministic sentiment extraction, integrated via volatility targeting.

## Requirements

### Validated

- ✓ Basic project skeleton created — 2026-08-11
- ✓ Risk Agent (Allocation): Volatility Targeting (inverse volatility allocation) — Validated in Phase 03: risk-allocation-backtesting
- ✓ Risk Agent: Sentiment Tilt (score * conviction factor) — Validated in Phase 03: risk-allocation-backtesting
- ✓ Risk Agent: Risk Bands (turnover control) to limit operations to 1-2 adjustments per month (reduce transaction costs) — Validated in Phase 03: risk-allocation-backtesting
- ✓ Backtester: Point-in-Time event-driven simulation — Validated in Phase 03: risk-allocation-backtesting
- ✓ Backtester: Generate signals on t_close, execute on t+1_open — Validated in Phase 03: risk-allocation-backtesting
- ✓ Backtester: Account for transaction costs (bps), calculate Sharpe Ratio and Max Drawdown — Validated in Phase 03: risk-allocation-backtesting
- ✓ Data Ingestion: use `yfinance` for market data/news. — v1.0
- ✓ Calculate logarithmic returns and 21-day Realized Volatility. — v1.0
- ✓ Strict Lookahead Bias handling: exact publication timestamps for news, separate t_close data from t+1_open execution. — v1.0
- ✓ Exponential Backoff for rate limits. — v1.0
- ✓ Quant Agent: LightGBM to predict future 21-day realized volatility. — v1.0
- ✓ Quant Agent: `Optuna` hyperparameter tuning. — v1.0
- ✓ Quant Agent: Purged Time-Series Split (Gap TimeSeriesSplit) for cross-validation to prevent overlapping volatility windows. — v1.0
- ✓ Fundamental Agent: Gemini 1.5 Pro (Google AI Pro via API), Temperature 0.0, JSON output. — v1.0
- ✓ Fundamental Agent: Extract continuous Sentiment Score [-1.0, 1.0] from financial text with a factual rationale extracted directly from text (mitigate hallucination). — v1.0

### Active

(None yet — planning next milestone)

### Out of Scope

- Synchronous execution — I/O bottlenecks must be avoided via strictly asynchronous architecture.
- Traditional technical indicators or standard risk models beyond 21-day RV — focused purely on LightGBM volatility and Gemini sentiment.
- Intra-day trading — execution is strictly t+1_open.

## Context

- Target: Itaú Asset Quant AI 2026 Challenge.
- Zero-Budget restriction: Must rely on free `yfinance` data and available Google AI Pro API.
- v1.0 MVP complete — implemented point-in-time backtester, volatility targeting, sentiment tilt, risk bands, LightGBM quant agent, and Gemini fundamental agent. Pipeline handles inference reliably with exponential backoff and sentiment fallbacks.

## Constraints

- **Tech Stack**: Python strictly with `asyncio` — To prevent I/O bottlenecks.
- **Tech Stack**: LightGBM and Optuna — For the quant agent.
- **Data Integrity**: Strict Lookahead Bias handling (Gap TimeSeriesSplit, t_close vs t+1_open) — Essential for robust quant models.
- **Cost/Budget**: Zero-budget data sources (`yfinance`) — Challenge restriction.
- **Execution Strategy**: Risk Bands limit operations to 1-2 times per month — Controls transaction costs.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Purged Time-Series Split | Prevents data leakage from overlapping 21-day volatility windows | ✓ Shipped in v1.0 MVP |
| Deterministic LLM Config | Temperature 0.0 with rationale extraction minimizes hallucination risk for the Fundamental agent | ✓ Shipped in v1.0 MVP |
| Optuna integration | Hyperparameter tuning must happen within the backtest inference loop just-in-time | ✓ Shipped in v1.0 MVP |
| API Fallback | Missing/failed LLM inferences map to 0.0 (neutral) sentiment to avoid crashing the pipeline | ✓ Shipped in v1.0 MVP |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-12 after v1.0 MVP milestone*
