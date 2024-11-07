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

KNOWLEDGE_BASE_PATH = (
    r"G:\Shared drives\NUANU ARCHITECTS\LIB Library\LIB Standards and Regulations"
)

CHAT_HISTORY_LEVEL=10
DOCS_IN_RETRIEVER=5