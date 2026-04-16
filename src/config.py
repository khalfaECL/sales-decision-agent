"""
config.py — Configuration centralisée.

Charge les variables d'environnement depuis .env
et expose les constantes du projet.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Llama 3.3 70B — meilleur modèle gratuit sur Groq avec tool calling
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# --- Agent ---
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
