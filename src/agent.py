"""
agent.py — Le cerveau de l'agent (boucle ReAct) — Version Groq.

DIFFÉRENCES vs version Anthropic :
┌──────────────────────┬──────────────────────┬──────────────────────┐
│                      │ ANTHROPIC            │ GROQ (OpenAI)        │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ Client               │ anthropic.Anthropic  │ groq.Groq            │
│ System prompt        │ system=...           │ message role="system" │
│ Stop reason          │ response.stop_reason │ finish_reason         │
│ Tool call signal     │ "tool_use"           │ "tool_calls"          │
│ Tool call location   │ response.content[]   │ message.tool_calls[]  │
│ Tool call args       │ block.input (dict)   │ tc.function.arguments │
│                      │                      │ (JSON string!)        │
│ Tool result role     │ role="user" +        │ role="tool"           │
│                      │ type="tool_result"   │                      │
└──────────────────────┴──────────────────────┴──────────────────────┘

LA BOUCLE ReAct EST IDENTIQUE. Seul le "câblage" change.
C'est pour ça qu'en production on utilise des abstractions (LangChain, n8n)
qui cachent ces différences.
"""

import json
from groq import Groq
from src.tools import TOOL_DEFINITIONS, execute_tool
from src.config import GROQ_API_KEY, MODEL_NAME, MAX_ITERATIONS


# ============================================================
# SYSTEM PROMPT (identique — le prompt est agnostique du provider)
# ============================================================

SYSTEM_PROMPT = """You are a Senior Business Analyst AI Agent specialized in sales data analysis.

## YOUR ROLE
You help business leaders make data-driven decisions by analyzing sales data, 
identifying trends, anomalies, and opportunities, then providing actionable recommendations.

## YOUR METHODOLOGY
Follow this analytical framework for EVERY query:
1. START BROAD: First get the overall sales summary to understand the big picture.
2. DRILL DOWN: Based on what you see, investigate specific products or regions.
3. CROSS-REFERENCE: Compare metrics across dimensions (product vs region, month vs month).
4. CONCLUDE: Only after sufficient analysis, provide your recommendations.

## YOUR OUTPUT FORMAT
Structure every final answer as:
- **Key Findings**: The 2-3 most important discoveries from the data
- **Risk Alerts**: Any anomalies or negative trends that need attention
- **Recommendations**: Specific, actionable decisions with expected impact
- **Data Support**: The numbers backing each recommendation

## CONSTRAINTS
- Never guess — always use tools to get real data before making claims.
- If a tool call returns an error, RETRY the tool call. Do NOT invent data.
- NEVER fabricate numbers. Every number in your response must come from a tool result.
- If a question is ambiguous, analyze from multiple angles rather than asking for clarification.
- Always quantify your recommendations (percentages, amounts, comparisons).
- Flag any data limitations or caveats in your analysis.
"""


# ============================================================
# LA BOUCLE ReAct (adaptée au format Groq/OpenAI)
# ============================================================

def run_agent(user_query: str, verbose: bool = True) -> str:
    """
    Exécute l'agent sur une question utilisateur.

    Args:
        user_query: La question business de l'utilisateur
        verbose: Afficher les logs d'exécution

    Returns:
        La réponse finale de l'agent (texte)
    """

    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not set. Copy .env.example to .env and add your key."

    # --- Client Groq ---
    # Groq utilise l'interface OpenAI, donc le client ressemble à OpenAI
    client = Groq(api_key=GROQ_API_KEY)

    # --- Historique ---
    # DIFFÉRENCE : Chez Anthropic, le system prompt est un paramètre séparé.
    # Chez OpenAI/Groq, c'est un message avec role="system".
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    if verbose:
        print(f"\n{'='*60}")
        print(f"🧠 AGENT STARTED")
        print(f"📝 Question: {user_query}")
        print(f"{'='*60}")

    # --- BOUCLE ReAct ---
    for iteration in range(1, MAX_ITERATIONS + 1):

        if verbose:
            print(f"\n--- Iteration {iteration}/{MAX_ITERATIONS} ---")

        # ÉTAPE 1 : Appel au LLM
        # DIFFÉRENCE : "tools" au lieu de "tools" (pareil ici), mais le format
        # des tools est différent (voir tools.py)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=4096,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Extraire le message de la réponse
        # DIFFÉRENCE : Chez Anthropic → response.content (liste de blocks)
        #              Chez Groq     → response.choices[0].message
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if verbose:
            print(f"   Finish reason: {finish_reason}")

        # ============================
        # CAS A : Le LLM a fini (stop)
        # ============================
        # DIFFÉRENCE : "end_turn" chez Anthropic → "stop" chez OpenAI/Groq
        if finish_reason == "stop":
            if verbose:
                print(f"\n✅ AGENT FINISHED after {iteration} iteration(s)")
            return message.content or ""

        # ============================
        # CAS B : Le LLM veut utiliser des tools (tool_calls)
        # ============================
        # DIFFÉRENCE : Chez Anthropic, les tool calls sont dans response.content[]
        #              Chez Groq, ils sont dans message.tool_calls[]
        if finish_reason == "tool_calls":

            # 1. Ajouter le message assistant à l'historique
            # DIFFÉRENCE : Chez Anthropic on construit manuellement le message.
            #              Chez Groq on peut directement ajouter l'objet message.
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # 2. Exécuter chaque tool call et ajouter les résultats
            for tc in message.tool_calls:
                tool_name = tc.function.name

                # DIFFÉRENCE CRITIQUE :
                # Chez Anthropic → tc.input est DÉJÀ un dict Python
                # Chez Groq      → tc.function.arguments est une STRING JSON
                # Il faut la parser avec json.loads() !
                #
                # EDGE CASE GROQ : quand un tool n'a pas de paramètres requis,
                # Groq peut envoyer None ou "" au lieu de "{}".
                # On doit gérer ça sinon json.loads(None) → crash.
                raw_args = tc.function.arguments
                if raw_args is None or raw_args.strip() == "":
                    tool_input = {}
                else:
                    tool_input = json.loads(raw_args)

                if verbose:
                    print(f"   🔧 Tool call: {tool_name}({tool_input})")

                result = execute_tool(tool_name, tool_input)

                if verbose:
                    print(f"   📊 Result preview: {result[:150]}...")

                # 3. Ajouter le résultat
                # DIFFÉRENCE : Chez Anthropic → role="user", type="tool_result"
                #              Chez Groq     → role="tool", tool_call_id=...
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

    return "⚠️ Agent stopped: maximum iterations reached. Analysis may be incomplete."
