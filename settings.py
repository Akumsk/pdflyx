# settings.py

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-4o"
"""
gpt-4o
gpt-4o-mini
"""

knowledge_base_paths = {
    "Российские стандарты": r"E:\knowledge_base\russian_regulations",
    "Indonesian Regulations": r"E:\knowledge_base\indonesian_regulations",
    "ISO Regulations": r"E:\knowledge_base\iso_regulations",
}

knowledge_base_language = {
    "Российские стандарты": r"Russian",
    "Indonesian Regulations": r"Indonesioan",
    "ISO Regulations": r"English",
}

SUPPORTED_LANGUAGES = ["English", "Russian", "Indonesian"]

CHAT_HISTORY_LEVEL = 5
DOCS_IN_RETRIEVER = 4
RELEVANCE_THRESHOLD_DOCS = 0.7
RELEVANCE_THRESHOLD_PROMPT = 0.8
