# Phase 04 Discussion Log

**Date:** 2026-08-11

## Area 1: Pipeline Driver
- **Options presented:** Generator vs Asyncio Queue
- **User selected:** Keep it simple: use an async generator that yields daily events, matching the current Backtester signature.

## Area 2: Training vs Simulation
- **Options presented:** Upfront historical training vs Incremental training
- **User selected:** Trigger a distinct 'historical training phase' upfront to fit the model, then run the daily event loop using the fitted model for predictions.

## Area 3: Data Passing
- **Options presented:** In-memory DataFrames vs Temporary files
- **User selected:** Hold DataFrames entirely in memory and pass them directly to agents (fastest, fits the zero-budget/simple constraint).
