"""
main.py — Point d'entrée de l'agent.

Usage:
  1. cp .env.example .env
  2. Edit .env → add your ANTHROPIC_API_KEY
  3. python main.py
"""

from src.agent import run_agent


def main():
    # --- Questions business à tester ---
    # Décommente celle que tu veux, ou écris la tienne.

    queries = [
        "What are the biggest risks in our sales data? Give me actionable recommendations.",
        # "Which product should we push as a priority and why?",
        # "Is the Occitanie region profitable? What do you recommend?",
        # "Give me an action plan to improve our margins across all products.",
        # "Compare our product return rates and flag any anomalies.",
    ]

    for query in queries:
        result = run_agent(query, verbose=True)
        print(f"\n{'='*60}")
        print("📋 FINAL AGENT RESPONSE:")
        print(f"{'='*60}")
        print(result)


if __name__ == "__main__":
    main()
