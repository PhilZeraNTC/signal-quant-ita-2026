# Signal Quant 🏆 Top 5% Itaú Asset Quant AI 2026

Um *Multi-Agent Portfolio Manager* operando ações do S&P 500, classificado no **Top 5%** do Desafio Itaú Asset Quant AI 2026. 

📊 **[Clique aqui para ler o Relatório Executivo Final (PDF)](https://github.com/PhilZeraNTC/signal-quant-ita-2026/blob/main/AAHV.pdf)**

Este projeto explora a intersecção entre Inteligência Artificial Generativa (*Spec-Driven Development*), Machine Learning (*Gradient Boosting*) e finanças quantitativas para isolar o alfa direcional do ruído de mercado.

## A Arquitetura (GSD Core & Multi-Agentes)
O desenvolvimento foi inteiramente orquestrado pelo framework **GSD Core**, garantindo isolamento de contexto e prevenindo alucinações. O repositório retém o histórico de decisões da IA no diretório `.planning/`.

1. **Quant Agent (LightGBM & Optuna):** Motor de previsão de volatilidade (janela de 21 dias) com *Purged Time-Series Split* para blindagem contra *data leakage*.
2. **Fundamental Agent (GenAI):** Extração determinística de sentimento (Temperature 0.0) de manchetes financeiras via `yfinance`.
3. **Risk Agent:** Dimensionamento dinâmico de posição (*Volatility Targeting*).

## Resultados do Backtest (Out-of-Sample: 2024)
O backtest puro revelou excelente captura de alfa, mas expôs gargalos estruturais documentados e diagnosticados pela nossa engenharia:

*   **Retorno Acumulado:** +47.42% (vs +26.04% do SPY)
*   **Sharpe Ratio:** 1.84 (vs 1.91 do SPY)
*   **Max Drawdown:** -14.35%
*   **Turnover Anual:** 11.63x

## Análise Crítica e Próximos Passos
A transparência analítica é um pilar deste repositório. O elevado turnover (11.63x) evidenciou uma falha de acoplamento na simulação de execução: o portfólio sofreu de *Drift* contínuo, forçando o backtester a realizar micro-arbitragens diárias e gerando sangria via custos transacionais (5.0 bps). 

**Roadmap de Correções:**
*   Implementação de *Deadbands* percentuais no motor de execução para ignorar oscilações de ruído e travar o limite real de rebalanceamento.
*   Substituição do *Data Feed* gratuito por APIs institucionais para sanar os buracos no histórico textual do GenAI durante choques de mercado.
