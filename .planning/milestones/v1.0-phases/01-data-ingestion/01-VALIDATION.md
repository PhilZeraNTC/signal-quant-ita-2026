# Phase 1: Data Ingestion - Validation Strategy

**Phase:** 1-Data Ingestion
**Created:** 2026-08-11

## Nyquist Validation (Dimension 8)

- **V-01 (Rate Limit):** Ensure the ingestion pipeline correctly catches `HTTPError` 429 and applies exponential backoff up to 5 times.
- **V-02 (Lookahead):** Assert that a signal generated for date `T` accesses no `yfinance` data indexed > `T`.
- **V-03 (Data integrity):** Validate that missing OHLCV data points are forward-filled, up to a maximum of 3 consecutive days, before dropping the ticker.
