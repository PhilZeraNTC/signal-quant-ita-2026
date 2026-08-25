# Signal Quant

A Multi-Agent Portfolio Manager operating on S&P 500 equities for the **Itaú Asset Quant AI 2026 Challenge**.

This project implements an asynchronous (`asyncio`) architecture to prevent I/O bottlenecks, ensuring robust and performant trading signal generation and execution.

## Core Value Proposition

Signal Quant generates highly performant risk-adjusted returns by combining two specialized AI agents:
1. **Quant Agent (LightGBM & Optuna):** Handles volatility forecasting.
2. **Fundamental Agent (Gemini 1.5 Pro):** Extracts deterministic sentiment from market data.

These agents are integrated via dynamic **volatility targeting**, optimizing the risk-reward ratio across the portfolio.

## Architecture

The codebase is organized into the following core modules:

- **`core/`**: Central logic including the `orchestrator.py`, `backtester.py`, and `config.py`.
- **`agents/`**: Contains the intelligent actors: `genai_agent.py`, `quant_agent.py`, and `risk_agent.py`.
- **`ingestion/`**: Data gathering and preprocessing: `market_data.py` (via `yfinance`) and `fundamental.py`.

## Technical Constraints & Execution Strategy

- **Language:** Strictly Python utilizing `asyncio`.
- **Data Integrity:** Strict lookahead bias handling (Gap TimeSeriesSplit, t_close vs t+1_open). Essential for robust quant models.
- **Data Sources:** Zero-budget constraint met by utilizing `yfinance` exclusively.
- **Execution:** Operations are strictly limited to 1-2 times per month using Risk Bands to minimize transaction costs.

## Getting Started

*(Instructions for installation, environment configuration, and execution will be added here as the project evolves.)*