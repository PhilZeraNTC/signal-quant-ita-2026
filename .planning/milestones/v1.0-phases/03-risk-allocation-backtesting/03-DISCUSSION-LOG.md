# Phase 3 Discussion Log
**Phase:** Risk Allocation & Backtesting
**Date:** 2026-08-11

## 1. Capital Allocation Formula
**Options:**
- Multiplicative modifier (e.g., base_weight * (1 + sentiment * conviction_factor))
- Additive tilt (e.g., base_weight + sentiment * conviction_factor)
- Bounded threshold (e.g., only adjust weight if sentiment crosses +/- 0.5)

**Selection:** Multiplicative modifier (e.g., base_weight * (1 + sentiment * conviction_factor))

## 2. Risk Bands Enforcement
**Options:**
- Strictly ignore the signal (hard enforce the 1-2 limit)
- Queue the trade for the next month
- Allow overrides only for extreme sentiment scores (e.g. > 0.8 or < -0.8)

**Selection:** Strictly ignore the signal (hard enforce the 1-2 limit)

## 3. Transaction Cost Modeling
**Options:**
- Flat basis points (bps) rate per trade (e.g. 5 bps per transaction)
- Dynamic slippage model scaled by LightGBM predicted volatility

**Selection:** Flat basis points (bps) rate per trade (e.g. 5 bps per transaction)

## 4. Backtester Event Loop
**Options:**
- Stream data point-by-point (simulates real-time strictly, safest against lookahead bias)
- Pre-calculate all signals then step through (much faster backtesting, but requires careful array alignment)

**Selection:** Stream data point-by-point (simulates real-time strictly, safest against lookahead bias)
