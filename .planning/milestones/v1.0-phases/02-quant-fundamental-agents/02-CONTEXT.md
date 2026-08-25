---
phase: 2
---

# Phase 2 Context: Quant & Fundamental Agents

## Domain
Build the predictive engines (LightGBM for volatility and Gemini for sentiment).

## Implementation Decisions

### 1. LightGBM Objective Function
- **Decision:** Start with Standard Mean Squared Error (MSE) for MVP to ensure stable convergence.
- **Implementation Detail:** Explicitly architect the `QuantAgent` training pipeline to accept a custom objective function so we can transition to an asymmetric loss function later without refactoring.

### 2. Fundamental Agent Output Format
- **Decision:** Strict JSON Structured Outputs.
- **Implementation Detail:** Use the Gemini API's Structured Outputs feature to enforce a deterministic schema (e.g. `{"sentiment": Float, "rationale": String}`), eliminating the need for regex-based text parsing.

### 3. Fundamental Agent Context Scope
- **Decision:** Batch evaluation over N days.
- **Implementation Detail:** Group the headlines from the last N days for a given stock and feed them as a single batch to Gemini, allowing the agent to infer broader sentiment trends rather than reacting to isolated headlines.

## Canonical Refs
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
