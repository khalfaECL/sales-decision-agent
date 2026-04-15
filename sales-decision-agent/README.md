# 🤖 Sales Decision Agent

> AI-powered decision agent for sales data analysis, built with **Anthropic Claude API** and the **ReAct pattern** (Reasoning + Acting).

The agent autonomously queries sales data through tools, identifies trends, anomalies, and opportunities, then delivers actionable business recommendations backed by data.

---

## Architecture

```
sales-decision-agent/
│
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── agent.py              # 🧠 Agent brain — ReAct loop + Anthropic API
│   ├── tools.py              # 🔧 Tool definitions + execution dispatch
│   ├── sales_api.py          # 📊 Simulated sales data API
│   └── config.py             # ⚙️  Configuration & constants
│
└── main.py                   # 🚀 Entry point
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   ReAct Loop                         │
│                                                      │
│  User Question                                       │
│       ↓                                              │
│  ┌─────────┐    ┌──────────┐    ┌─────────────────┐ │
│  │ THINK   │───→│ ACT      │───→│ OBSERVE         │ │
│  │ (LLM    │    │ (call a  │    │ (read tool      │ │
│  │ reasons)│    │  tool)   │    │  results)       │ │
│  └────┬────┘    └──────────┘    └────────┬────────┘ │
│       │                                   │          │
│       │         ┌──────────┐              │          │
│       └─────────│ ANSWER   │←─────────────┘          │
│                 │ (enough  │  (need more data        │
│                 │ data →   │   → loop again)         │
│                 │ respond) │                          │
│                 └──────────┘                          │
└─────────────────────────────────────────────────────┘
```

### Agent Tools

| Tool | Description |
|------|-------------|
| `get_sales_summary` | High-level KPIs: revenue, profit, margin, return rate (filterable by month) |
| `get_sales_by_product` | Per-product breakdown: revenue, margin %, return rate % |
| `get_sales_by_region` | Per-region breakdown with month-over-month trend |
| `get_product_trend` | Monthly evolution of a specific product (revenue, qty, returns) |

### Hidden Trends the Agent Should Detect

The simulated data contains 4 hidden patterns:
1. **Ergo Chair spike** — 2.5x sales in January (New Year resolutions)
2. **Occitanie decline** — Region losing 5% revenue per month
3. **Headset returns** — 13% return rate vs 3% baseline (quality issue?)
4. **USB-C Hub margin** — 79.5% margin, highest in catalog (growth opportunity)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/sales-decision-agent.git
cd sales-decision-agent

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env and add your Anthropic API key

# 4. Run
python main.py
```

## Example Output

```
🧠 AGENT STARTED
📝 Question: Quels sont les plus gros risques dans nos données de ventes ?

--- Iteration 1/10 ---
   🔧 Tool call: get_sales_summary({})
   📊 Result preview: {"period": "all", "total_revenue": 1893111, ...}

--- Iteration 2/10 ---
   🔧 Tool call: get_sales_by_product({})
   📊 Result preview: [{"product_name": "Laptop Pro X1", ...}]

--- Iteration 3/10 ---
   🔧 Tool call: get_sales_by_region({})
   📊 Result preview: [{"region_name": "Île-de-France", ...}]

✅ AGENT FINISHED after 4 iteration(s)

📋 RÉPONSE FINALE DE L'AGENT:
**Key Findings**: ...
**Risk Alerts**: ...
**Recommendations**: ...
```

---

## Tech Stack

- **Python 3.10+**
- **Anthropic Claude API** (claude-sonnet-4-20250514) — LLM brain
- **ReAct pattern** — Reasoning + Acting loop
- **Tool Use** — Anthropic native function calling

## Next Steps

- [ ] Phase 2: Migrate to **n8n** for visual workflow orchestration
- [ ] Add real database (PostgreSQL) instead of simulated API
- [ ] Add more tools (email alerts, PDF report generation)
- [ ] Deploy as webhook-triggered service

---

## License

MIT
