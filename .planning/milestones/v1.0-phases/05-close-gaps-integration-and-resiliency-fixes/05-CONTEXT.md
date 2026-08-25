# 05-CONTEXT

## Domain
This phase delivers integration bug fixes and resiliency improvements, specifically wiring Optuna tuning to the pipeline, adding exponential backoff to News and Gemini APIs, fixing the data slicing bug that drops the inference period, and making the ticker dynamic while ensuring the Orchestrator loop survives API errors.

## Decisions
- **Optuna Tuning Execution:** Run tuning once during `prepare_agents()` at the start of the backtest. (Simplest, meets MVP requirement).
- **API Resilience Strategy:** Add exponential backoff using `@retry`, and if all retries fail, return a neutral sentiment score (0.0) with 'API failure' rationale so the backtest doesn't crash.
- **Inference Data Alignment:** Move the data slicing and alignment logic entirely inside the `Orchestrator` to safely handle the training/inference splits internally.

## Canonical Refs
- `v1.0-MILESTONE-AUDIT.md`

## Code Context
- `main.py`
- `core/orchestrator.py`
- `agents/quant_agent.py`
- `agents/genai_agent.py`
- `ingestion/fundamental.py`
