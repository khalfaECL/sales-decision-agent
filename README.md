# Sales Decision Agent

AI-powered decision agent for sales data analysis using the ReAct pattern (Reasoning + Acting). The agent autonomously queries sales data through tools, identifies trends and anomalies, and delivers actionable business recommendations.

---

## Architecture

```
sales-decision-agent/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── agent.py        # Agent core — ReAct loop
│   ├── tools.py        # Tool definitions and execution
│   ├── sales_api.py    # Simulated sales data API
│   └── config.py       # Configuration and constants
│
└── main.py             # Entry point
```

## How It Works

The agent follows a Thought → Action → Observation loop until it has enough data to produce a final answer:

```
User Question
     |
  [THINK] → [ACT: call tool] → [OBSERVE: read result]
     |                                  |
     └──────────── loop ────────────────┘
     |
  [ANSWER]
```

### Available Tools

| Tool | Description |
|------|-------------|
| `get_sales_summary` | High-level KPIs: revenue, profit, margin, return rate |
| `get_sales_by_product` | Per-product breakdown: revenue, margin %, return rate % |
| `get_sales_by_region` | Per-region breakdown with month-over-month trend |
| `get_product_trend` | Monthly evolution for a specific product |

### Hidden Patterns in the Simulated Data

The dataset contains four embedded signals the agent should detect:

1. **Ergo Chair spike** — 2.5x sales in January
2. **Occitanie decline** — Region losing 5% revenue per month
3. **Headset returns** — 13% return rate vs. 3% baseline
4. **USB-C Hub margin** — 79.5% margin, highest in catalog

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/sales-decision-agent.git
cd sales-decision-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your Groq API key (https://console.groq.com/keys)

# 4. Run
python main.py
```

---

## Tech Stack

- **Python 3.10+**
- **Groq API** with `llama-3.3-70b-versatile` — LLM inference
- **ReAct pattern** — iterative reasoning and tool use loop
- **n8n** — visual workflow orchestration (production implementation)

---

## Roadmap

- [ ] Connect to a real database (PostgreSQL or BigQuery)
- [ ] Add alert tools: email notifications, Slack messages
- [ ] PDF report generation from agent output
- [ ] Expose agent as a webhook-triggered service
- [ ] Add memory across sessions (conversation history)
- [ ] Support multi-agent workflows (specialist sub-agents per region or product line)

---

## License

MIT
