"""
tools.py — Définition et exécution des outils de l'agent.

DIFFÉRENCE CLÉ vs Anthropic :
Groq utilise le format OpenAI pour les tools.

Format Anthropic :
  {"name": "...", "description": "...", "input_schema": {...}}

Format OpenAI (utilisé par Groq) :
  {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}

C'est une couche d'emballage en plus, mais la logique est IDENTIQUE.
En production avec LangChain ou n8n, cette différence est abstraite pour toi.
"""

import json
from src.sales_api import (
    get_sales_summary,
    get_sales_by_product,
    get_sales_by_region,
    get_product_trend,
)


# ============================================================
# DÉFINITIONS DES TOOLS (format OpenAI / Groq)
# ============================================================
# Chaque tool est wrappé dans {"type": "function", "function": {...}}
# Le contenu de "function" est quasi identique au format Anthropic :
# - name → pareil
# - description → pareil
# - parameters → c'était "input_schema" chez Anthropic

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_summary",
            "description": (
                "Retrieve a high-level overview of sales performance: "
                "total revenue, profit, margin percentage, units sold, "
                "total returns, and return rate. "
                "Can filter by a specific month (YYYY-MM) or return the full 6-month period. "
                "Use this tool FIRST to get a general picture before diving deeper."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": (
                            "Optional. Filter by month in YYYY-MM format "
                            "(e.g. '2025-12'). Omit to get all 6 months."
                        ),
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_by_product",
            "description": (
                "Break down sales performance by product. Returns for each product: "
                "name, category, total revenue, profit, margin %, quantity sold, "
                "returns count, and return rate %. "
                "Use this to identify best-sellers, highest-margin products, "
                "or products with abnormal return rates."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_by_region",
            "description": (
                "Break down sales performance by geographic region. Returns for each region: "
                "name, total revenue, profit, margin %, and a month-over-month trend percentage. "
                "A negative trend means declining sales. "
                "Use this to identify underperforming regions or growth opportunities."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_trend",
            "description": (
                "Get the monthly evolution of a specific product: revenue, quantity, "
                "and returns for each month. Use this to investigate seasonal patterns "
                "or anomalies spotted in the product summary. "
                "Requires a product_id (e.g. 'P001', 'P002', etc.)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID to investigate (e.g. 'P001').",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
]


# ============================================================
# EXÉCUTION DES TOOLS (inchangé — c'est du Python pur)
# ============================================================

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Reçoit le nom du tool + ses paramètres depuis le LLM,
    exécute la fonction correspondante, retourne le résultat en JSON string.
    """
    # Dans tools.py, dans execute_tool, ajouter au début :
    if tool_input is None:
        tool_input = {}
    tool_map = {
        "get_sales_summary": get_sales_summary,
        "get_sales_by_product": get_sales_by_product,
        "get_sales_by_region": get_sales_by_region,
        "get_product_trend": get_product_trend,
    }

    if tool_name not in tool_map:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        result = tool_map[tool_name](**tool_input)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})
