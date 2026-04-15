"""
config.py — Configuration centralisée.

Charge les variables d'environnement depuis .env
et expose les constantes du projet.

En production : c'est ici qu'on centralise TOUTE la config
(clés API, noms de modèles, limites, URLs...).
Jamais de valeurs hardcodées dans le code métier.
"""

import os
from dotenv import load_dotenv

# Charger le fichier .env (cherche dans le dossier courant puis remonte)
load_dotenv()

# --- API ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")

# --- Agent ---
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
