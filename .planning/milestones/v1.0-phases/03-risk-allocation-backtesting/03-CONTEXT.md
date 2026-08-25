---
phase: 3
---

# Phase 3 Context: Risk Allocation & Backtesting

## Domain
Implement Volatility Targeting, Sentiment Tilt, Risk Bands, and the Point-in-Time Event-driven Backtester.

## Implementation Decisions

### 1. Capital Allocation Formula
- **Decision:** Multiplicative modifier (e.g., base_weight * (1 + sentiment * conviction_factor)).
- **Implementation Detail:** The Gemini sentiment score [-1.0, 1.0] mathematically adjusts the LightGBM inverse-volatility base weight via a multiplicative modifier.

### 2. Risk Bands Enforcement
- **Decision:** Strictly ignore the signal (hard enforce the 1-2 limit).
- **Implementation Detail:** When a signal triggers but the 1-2 adjustments/month limit is reached, the system will hard enforce the limit by ignoring the signal.

### 3. Transaction Cost Modeling
- **Decision:** Flat basis points (bps) rate per trade (e.g. 5 bps per transaction).
- **Implementation Detail:** Transaction costs (BACK-03) are modeled as a flat bps rate per trade rather than a dynamic slippage model.

### 4. Backtester Event Loop
- **Decision:** Stream data point-by-point (simulates real-time strictly, safest against lookahead bias).
- **Implementation Detail:** The event-driven simulation (BACK-01) is structured to strictly stream data point-by-point to enforce point-in-time constraints, avoiding lookahead bias.

## Canonical Refs
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`

## Prior Decisions from Earlier Phases
- **Phase 1 (D-02):** All execution signals are generated on t_close data, and executed at t+1_open.
- **Phase 1 (D-03):** News must be strictly timestamped to ensure publication time is strictly prior to t_close for any signal generation.
- **Phase 1:** Asynchronous architecture (`asyncio`) is mandated project-wide to prevent I/O bottlenecks.
- **Phase 2:** Gemini produces strict JSON Structured Outputs `{"sentiment": Float, "rationale": String}` which eliminates regex parsing.
