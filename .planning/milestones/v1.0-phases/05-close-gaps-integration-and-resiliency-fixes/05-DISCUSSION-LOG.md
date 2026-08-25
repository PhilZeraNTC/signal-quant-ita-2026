# 05-DISCUSSION-LOG

- **Optuna Tuning Execution:** User chose to run tuning once during `prepare_agents()` at the start of the backtest.
- **API Resilience Strategy:** User chose to add exponential backoff using `@retry`, and if all retries fail, return a neutral sentiment score (0.0).
- **Inference Data Alignment:** User chose to move the data slicing and alignment logic entirely inside the `Orchestrator`.
