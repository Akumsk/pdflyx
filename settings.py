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

MAX_TOKENS_IN_CONTEXT = 128000

knowledge_base_paths = {
    "Российские стандарты": r"E:\knowledge_base\russian_regulations",
    "Indonesian Regulations": r"E:\knowledge_base\indonesian_regulations",
    "ISO Regulations": r"E:\knowledge_base\iso_regulations",
}

SUPPORTED_LANGUAGES = ["English", "Russian", "Indonesian"]

CHAT_HISTORY_LEVEL = 10
DOCS_IN_RETRIEVER = 5
