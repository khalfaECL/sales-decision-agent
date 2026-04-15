"""
agent.py — Le cerveau de l'agent (boucle ReAct).

CONCEPT CLÉ :
Le LLM ne génère pas juste du texte — il ORCHESTRE des actions.
À chaque itération il décide : "j'appelle un outil" ou "j'ai assez d'info, je réponds".

La boucle :
  1. Envoyer question + tools au LLM
  2. Si stop_reason == "tool_use"  → exécuter le tool, renvoyer le résultat, recommencer
  3. Si stop_reason == "end_turn"  → extraire la réponse finale, sortir
"""

import anthropic
from src.tools import TOOL_DEFINITIONS, execute_tool
from src.config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_ITERATIONS


# ============================================================
# SYSTEM PROMPT
# ============================================================
# La "personnalité" et la "méthodologie" de l'agent.
# En production, ce prompt détermine la qualité des décisions.

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
- If a question is ambiguous, analyze from multiple angles rather than asking for clarification.
- Always quantify your recommendations (percentages, amounts, comparisons).
- Flag any data limitations or caveats in your analysis.
"""


# ============================================================
# LA BOUCLE ReAct
# ============================================================

def run_agent(user_query: str, verbose: bool = True) -> str:
    """
    Exécute l'agent sur une question utilisateur.

    Args:
        user_query: La question business de l'utilisateur
        verbose: Afficher les logs d'exécution (True en dev, False en prod)

    Returns:
        La réponse finale de l'agent (texte)
    """

    # --- Vérification clé API ---
    if not ANTHROPIC_API_KEY:
        return "❌ ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."

    # --- Initialisation client ---
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # --- Historique de conversation ---
    # Accumule tous les échanges : le LLM a besoin de voir
    # tout ce qu'il a déjà fait pour décider la suite.
    messages = [
        {"role": "user", "content": user_query}
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
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if verbose:
            print(f"   Stop reason: {response.stop_reason}")

        # CAS A : Le LLM a fini → extraire la réponse
        if response.stop_reason == "end_turn":
            if verbose:
                print(f"\n✅ AGENT FINISHED after {iteration} iteration(s)")

            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text

            return final_text

        # CAS B : Le LLM veut utiliser un tool
        if response.stop_reason == "tool_use":

            # 1. Ajouter la réponse complète du LLM à l'historique
            assistant_message = {"role": "assistant", "content": []}
            tool_results = []

            for block in response.content:

                if block.type == "text":
                    if verbose:
                        print(f"   💭 Thinking: {block.text[:120]}...")
                    assistant_message["content"].append({
                        "type": "text",
                        "text": block.text,
                    })

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    if verbose:
                        print(f"   🔧 Tool call: {tool_name}({tool_input})")

                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": tool_use_id,
                        "name": tool_name,
                        "input": tool_input,
                    })

                    # 2. Exécuter le tool
                    result = execute_tool(tool_name, tool_input)

                    if verbose:
                        print(f"   📊 Result preview: {result[:150]}...")

                    # 3. Préparer le résultat
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })

            # 4. Mettre à jour l'historique
            messages.append(assistant_message)
            messages.append({"role": "user", "content": tool_results})

    # Sécurité : limite atteinte
    return "⚠️ Agent stopped: maximum iterations reached. Analysis may be incomplete."
