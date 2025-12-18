
# 🧠 Strategy Overview

This project implements a **simple trend-following trading system** designed to mirror day-to-day quantitative execution work.

- **Signal logic:** EMA-based trend detection combined with a momentum (RSI) filter  
- **Positioning:** Long / Flat only (no shorting)  
- **Design goal:** Maximum clarity, transparency, and observability rather than aggressive optimization  

The focus is on demonstrating clean strategy logic, execution flow, risk controls, and logging rather than producing a production-ready alpha model.

---

# ⚙️ How to Run (Paper Trading)

Activate your environment and run the main loop:

```bash
conda activate <env>
python main.py
````

All strategy, execution, and risk parameters are controlled via:

```
config.yaml
```

Logs will be written incrementally to a CSV file during execution.

---

# 🧪 Testnet vs Paper Mode

* **Paper mode:**
  Uses live market prices from Hyperliquid and simulates execution using the live order book, including slippage estimation.

* **Testnet execution:**
  Testnet execution was explored; however, due to access and funding constraints during the evaluation window, the final implementation uses paper trading.
  The architecture is designed such that testnet execution can be enabled with minimal changes.

---

# ⚠️ Safety Notes

* **Do not run with real capital**
* Position sizes are capped using USD notional limits per asset
* Risk controls include:

  * Maximum trades per asset
  * Portfolio-level drawdown limit
* This system is intended strictly for research and demonstration purposes

---

# 🤖 AI Usage Disclosure

AI tools were used as a coding assistant to help structure modules, refactor code, and reason about execution and risk logic.
Strategy design, parameter choices, debugging decisions, and evaluation were performed by me.
