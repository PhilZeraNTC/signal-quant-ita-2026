<!-- GSD:project-start source:PROJECT.md -->

## Project

**Signal Quant**

A Multi-Agent Portfolio Manager operating on S&P 500 equities for the Itaú Asset Quant AI 2026 Challenge. It's written strictly in Python with an asynchronous architecture (`asyncio`) to prevent I/O bottlenecks.

**Core Value:** Generate highly performant risk-adjusted returns by leveraging a LightGBM quant agent for volatility forecasting and a Gemini 1.5 Pro fundamental agent for deterministic sentiment extraction, integrated via volatility targeting.

### Constraints

- **Tech Stack**: Python strictly with `asyncio` — To prevent I/O bottlenecks.
- **Tech Stack**: LightGBM and Optuna — For the quant agent.
- **Data Integrity**: Strict Lookahead Bias handling (Gap TimeSeriesSplit, t_close vs t+1_open) — Essential for robust quant models.
- **Cost/Budget**: Zero-budget data sources (`yfinance`) — Challenge restriction.
- **Execution Strategy**: Risk Bands limit operations to 1-2 times per month — Controls transaction costs.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

- **Language:** Python
- **Dependencies:** None yet (`requirements.txt` is empty)
- **Frameworks:** Skeleton for a quant trading or analysis system (inferred from `core/`, `agents/`, `ingestion/`)

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

- Python codebase. No code written yet to establish style or conventions.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

- **Core:** `core/orchestrator.py`, `core/backtester.py`, `core/config.py`
- **Agents:** `agents/genai_agent.py`, `agents/quant_agent.py`, `agents/risk_agent.py`
- **Ingestion:** `ingestion/market_data.py`, `ingestion/fundamental.py`

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
