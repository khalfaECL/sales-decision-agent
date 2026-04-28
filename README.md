# Sales Decision Agent

AI agent for sales data analysis built with n8n, Groq (llama-3.3-70b-versatile), and the ReAct pattern. The agent autonomously queries sales data through tools, identifies trends and anomalies, and delivers actionable business recommendations via a chat interface.

---

## Architecture

The production implementation runs entirely in n8n:

```
Chat Input (n8n Chat Trigger)
        |
   [AI Agent Node]  <--  Groq Chat Model (llama-3.3-70b-versatile)
        |
   [Tool Calls] (ReAct loop: Think → Act → Observe → repeat)
        |
   ┌────────────────────┬──────────────────────┬───────────────────────┬──────────────────────┐
   │ get_sales_summary  │ get_sales_by_product │ get_sales_by_region  │ get_product_trend    │
   └────────────────────┴──────────────────────┴───────────────────────┴──────────────────────┘
        |
   Final Answer → Chat Response
```

### Workflow Nodes

| Node | Type | Role |
|------|------|------|
| When chat message received | Chat Trigger | Entry point — receives user question |
| AI Agent | LangChain Agent | Runs the ReAct reasoning loop |
| Groq Chat Model | LLM | `llama-3.3-70b-versatile` via Groq API |
| `get_sales_summary` | Code Tool | 6-month KPI overview (revenue, profit, margin, returns) |
| `get_sales_by_product` | Code Tool | Per-product breakdown (6 products) |
| `get_sales_by_region` | Code Tool | Per-region breakdown with trend % (5 French regions) |
| `get_product_trend` | Code Tool | Monthly evolution for a specific product (P001–P006) |

### Data Coverage

- **Period:** October 2025 – March 2026 (6 months)
- **Products:** Laptop Pro X1, Wireless Headset Z, Office Chair Ergo, Standing Desk Oak, USB-C Hub Ultra, Mechanical Keyboard
- **Regions:** Île-de-France, Auvergne-Rhône-Alpes, Nouvelle-Aquitaine, Hauts-de-France, Occitanie

### Hidden Patterns in the Data

The dataset contains four embedded signals the agent should detect:

1. **Ergo Chair spike** — 2.5x sales in January 2026 (seasonal demand)
2. **Occitanie decline** — Consistent revenue drop month over month (-54.6% trend)
3. **Headset returns** — 13.1% return rate vs. ~1.3% baseline (quality issue)
4. **USB-C Hub margin** — 79.5% margin, highest in catalog (growth opportunity)

---

## Agent System Prompt

The agent is instructed to follow this methodology:

1. Start broad — call `get_sales_summary` first for the big picture
2. Drill down — investigate specific products or regions based on what it finds
3. Cross-reference — compare metrics across dimensions
4. Conclude — only respond after sufficient analysis

Output format enforced: **Key Findings / Risk Alerts / Recommendations / Data Support**

---

## Quick Start (Python Prototype)

A Python prototype with the same tools and logic is also included in `sales-decision-agent/`.

```bash
cd sales-decision-agent
pip install -r requirements.txt
cp .env.example .env
# Add your Groq API key to .env (https://console.groq.com/keys)
python main.py
```

---

## Tech Stack

- **n8n** — workflow orchestration and agent runtime
- **Groq API** — LLM inference (`llama-3.3-70b-versatile`)
- **LangChain Agent node** — ReAct pattern implementation
- **Python 3.10+** — prototype implementation

---

## Roadmap

- [ ] Replace simulated data with a real database (PostgreSQL or BigQuery)
- [ ] Add alert tools: email notifications, Slack messages on anomaly detection
- [ ] PDF report generation from agent output
- [ ] Expose as a webhook-triggered service for external integrations
- [ ] Add memory across sessions (conversation history)
- [ ] Multi-agent setup: specialist sub-agents per region or product category
- [ ] Connect to live CRM or ERP data source

---

## License

MIT
