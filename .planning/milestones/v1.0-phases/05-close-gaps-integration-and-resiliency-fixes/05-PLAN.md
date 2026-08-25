---
wave: 1
depends_on: ["04-close-gap-end-to-end-orchestration-and-wiring"]
files_modified:
  - main.py
  - core/orchestrator.py
  - agents/quant_agent.py
  - agents/genai_agent.py
  - ingestion/fundamental.py
autonomous: true
---

# Phase 05: Close gaps: Integration and Resiliency Fixes

**Goal**: Deliver integration bug fixes and resiliency improvements: wire Optuna tuning, add exponential backoff/fallback to APIs, fix data slicing inference bug, and parameterize the Orchestrator ticker.

**User Story:** As a quantitative researcher, I want my backtest to run to completion utilizing tuned models and surviving external API rate limits, so that I can accurately evaluate the system's performance.

**Note:** Probe fallback disabled (`workflow.specless_probe_fallback=false`): no probe-derived predicates generated for SPEC-absent sections this run.

## Tasks

<task id="1" type="tracer">
  <title>Tracer Slice: Fix inference data slicing and dynamic ticker in Orchestrator</title>
  <description>Move data slicing and alignment logic from main.py into core/orchestrator.py to ensure the final 21 days of data are processed for inference instead of being dropped. Parameterize the ticker in Orchestrator.</description>
  <read_first>
    - main.py
    - core/orchestrator.py
  </read_first>
  <action>
    - Refactor main.py to pass the full raw dataset to Orchestrator.
    - Implement alignment logic inside Orchestrator to correctly separate training data from inference data (t+1_open) without dropping the final 21 days.
    - Update Orchestrator initialization to accept and use a dynamic ticker instead of hardcoded 'SPY'.
  </action>
  <acceptance_criteria>
    - The backtest execution loop runs to the end of the dataset without terminating 21 days early.
    - Orchestrator uses the provided dynamic ticker and no longer hardcodes 'SPY'.
    - Point-in-Time constraints remain intact (inference uses t_close to execute on t+1_open).
  </acceptance_criteria>
</task>

<task id="2" type="feature">
  <title>Wire Optuna Tuning into Backtest Initialization</title>
  <description>Invoke QuantAgent's Optuna tuning step during the backtest preparation phase to ensure the model uses optimized hyperparameters.</description>
  <read_first>
    - core/orchestrator.py
    - agents/quant_agent.py
  </read_first>
  <action>
    - Modify Orchestrator's initialization or agent preparation method to call `QuantAgent.optimize()`.
    - Ensure tuning only runs once before the backtest loop begins training.
  </action>
  <acceptance_criteria>
    - `QuantAgent.optimize()` is successfully invoked by Orchestrator before the first prediction.
    - Model predictions reflect tuned hyperparameters.
  </acceptance_criteria>
</task>

<task id="3" type="feature">
  <title>Implement API Resiliency for News and Gemini</title>
  <description>Add exponential backoff retries to NewsIngestor and FundamentalAgent, and implement a fallback mechanism to prevent the backtest from crashing on persistent API failures.</description>
  <read_first>
    - ingestion/fundamental.py
    - agents/genai_agent.py
    - core/orchestrator.py
  </read_first>
  <action>
    - Add exponential backoff (e.g., using `@retry` or `tenacity`) to NewsIngestor fetches and Gemini API calls in FundamentalAgent/Orchestrator.
    - Catch unrecoverable API exceptions after retries are exhausted.
    - Return a fallback neutral sentiment score (0.0) with rationale 'API failure' instead of bubbling up the exception.
    - Log failures appropriately without crashing the orchestrator loop.
  </action>
  <acceptance_criteria>
    - NewsIngestor and FundamentalAgent automatically retry on API errors using exponential backoff.
    - If all retries fail, a sentiment score of 0.0 and rationale 'API failure' is returned.
    - Backtest survives simulated API rate limits or network failures without crashing.
  </acceptance_criteria>
  <checkpoint:decision>
    - Confirmed: the neutral sentiment fallback of 0.0 is mathematically safe, as it correctly neutralizes the multiplicative tilt (1 + 0) and smoothly defaults to the base inverse-volatility allocation.
  </checkpoint:decision>
</task>

## Verification

**Verification Criteria:**
- The `QUANT-02`, `INGEST-04`, and `BACK-01/INGEST-03` audit gaps are completely resolved.
- End-to-end backtest runs to completion covering the final 21 days of data.
- The `QuantAgent.optimize()` method runs exactly once per run.
- Simulated API failures in News or Gemini endpoints gracefully fall back to 0.0 sentiment.

**Must-Haves (Goal-Backward):**
- Data slicing moved inside Orchestrator.
- Orchestrator takes a ticker string in initialization.
- Optuna tuning wired into the flow.
- Exponential backoff mechanism present for both News and Gemini.
- Sentiment fallback to 0.0 implemented and active.

## Artifacts this phase produces
- The new `ticker` parameter and field added to the `Orchestrator` class.
- The `prepare_agents()` method created in `Orchestrator` to invoke `QuantAgent.optimize()`.
- Exponential backoff retry decorators (e.g., `@retry` from `tenacity`) applied in `NewsIngestor` and `FundamentalAgent`.
