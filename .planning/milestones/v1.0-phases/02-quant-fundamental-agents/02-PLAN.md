---
wave: 1
depends_on: ["01-data-ingestion"]
files_modified:
  - "agents/quant_agent.py"
  - "agents/genai_agent.py"
autonomous: true
---

# Phase 02 Plan: Quant & Fundamental Agents

**Goal:** As a quant trader, I want to predict volatility with LightGBM and extract sentiment via Gemini, so that I can use these signals for risk-allocated portfolio trading.
**Mode:** mvp (Tracer-First Decomposition Active)

*Note: Specless probe fallback is disabled this run (no probe-derived predicates generated for SPEC-absent sections).*

## Tasks

<task id="task-1" type="tracer">
  <title>Tracer: End-to-End Base Quant and Fundamental Agents</title>
  <read_first>
    Read .agents/GEMINI.md and .planning/phases/02-quant-fundamental-agents/02-CONTEXT.md. 
    Review Phase 1 outputs to understand data schemas. Note the strict `asyncio` architecture constraints.
    Modify files: `agents/quant_agent.py`, `agents/genai_agent.py`
  </read_first>
  <action>
    Create `agents/quant_agent.py` and `agents/genai_agent.py`. 
    Implement `QuantAgent` with a custom objective function signature defaulting to standard Mean Squared Error (MSE), capable of training a basic LightGBM model and predicting 21-day Realized Volatility (QUANT-01).
    Implement `FundamentalAgent` inside `genai_agent.py` with an async method to call the Gemini API via the `google-genai` SDK, using Temperature 0.0 and a strict JSON schema for Structured Outputs (FUND-01).
    Ensure both agents can run successfully end-to-end on sample data payloads, returning expected basic types.
  </action>
  <acceptance_criteria>
    - `agents/quant_agent.py` and `agents/genai_agent.py` exist.
    - `QuantAgent` successfully trains on a standard Pandas DataFrame and returns a prediction using MSE.
    - `FundamentalAgent` asynchronously calls the Gemini API without blocking the event loop.
    - `FundamentalAgent` returns a valid JSON object matching the defined schema.
  </acceptance_criteria>
</task>

<task id="task-2">
  <title>Quant Engine Expansion: CV and Optuna Tuning</title>
  <read_first>
    Review requirements QUANT-02 and QUANT-03.
    Modify file: `agents/quant_agent.py`
    <checkpoint:decision>
      Determine the exact gap size for the Purged Time-Series Split. This is a critical one-way door to ensure no lookahead bias exists between the training set and validation set given the 21-day RV calculation.
    </checkpoint:decision>
  </read_first>
  <action>
    Enhance `QuantAgent` with a hyperparameter tuning pipeline using `optuna`. 
    Implement a Purged Time-Series Split (Gap TimeSeriesSplit) for cross-validation to explicitly prevent lookahead bias when optimizing hyperparameters.
  </action>
  <acceptance_criteria>
    - `QuantAgent` exposes an `optimize` method utilizing Optuna for tuning hyperparameters.
    - Cross-validation within optimization strictly applies a gap-based time-series split.
    - Tests or assertions confirm zero overlap between training targets and validation inputs.
  </acceptance_criteria>
</task>

<task id="task-3">
  <title>Fundamental Engine Expansion: N-day Batching and Sentiment Extraction</title>
  <read_first>
    Review requirements FUND-02, FUND-03 and 02-CONTEXT.md regarding N-day batch evaluation.
    Modify file: `agents/genai_agent.py`
  </read_first>
  <action>
    Enhance `FundamentalAgent` to process a batched group of news headlines spanning N days for a given equity. 
    Refine the system prompt and JSON schema to strictly enforce the output of a continuous sentiment float in the range [-1.0, 1.0] and a factual string rationale (FUND-02, FUND-03).
  </action>
  <acceptance_criteria>
    - Agent accepts a sequence of news headlines grouped by ticker over N days.
    - The JSON output strictly validates against the schema: `{"sentiment": float, "rationale": str}`.
    - Sentiment score property is bounded between -1.0 and 1.0 inclusive.
    - Rationale property contains extracted factual text.
  </acceptance_criteria>
</task>

## Verification Criteria

1. **Quant Agent (LightGBM)**
   - The model can train on historical dataset and output predictions for 21-day realized volatility.
   - Optuna efficiently searches for hyperparameters without causing data leakage.
   - The Purged Time-Series Split confirms zero lookahead bias.
2. **Fundamental Agent (Gemini)**
   - The model returns a strictly formatted JSON structure on every call.
   - The sentiment score falls between -1.0 and 1.0.
   - The architecture is strictly asynchronous (`asyncio`).

## Must Haves (Goal-Backward Verification)

- **Must have** a `QuantAgent` class with an explicit MSE objective that can be swapped later.
- **Must have** Optuna integration for the QuantAgent.
- **Must have** a `FundamentalAgent` class calling Gemini API asynchronously with Temperature 0.0.
- **Must have** strict JSON validation for sentiment [-1.0, 1.0] and rationale string.
- **Must have** a mechanism for batching N-days of news to the FundamentalAgent.

## Artifacts this phase produces

- `agents/quant_agent.py`: `QuantAgent` class, `optimize` method. Implementation of the LightGBM volatility forecaster.
- `agents/genai_agent.py`: `FundamentalAgent` class, asynchronous extraction method. Implementation of the async Gemini fundamental sentiment extractor.
