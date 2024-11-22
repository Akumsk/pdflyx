from datetime import datetime
import re
from langchain.schema import Document, HumanMessage, AIMessage


def messages_to_langchain_messages(chat_history_texts):

    # Convert chat_history_texts to list of HumanMessage and AIMessage
    chat_history = []
    for msg in chat_history_texts:
        if msg.startswith("HumanMessage:"):
            content = msg[len("HumanMessage:") :].strip()
            chat_history.append(HumanMessage(content=content))
        elif msg.startswith("AIMessage:"):
            content = msg[len("AIMessage:") :].strip()
            chat_history.append(AIMessage(content=content))

    return chat_history


def current_timestamp():
    date_time = (
        datetime.now().date().strftime("%Y-%m-%d")
        + ", "
        + datetime.now().time().strftime("%H:%M:%S")
    )
    return date_time

def parser_html(text):
    """
    Convert markdown-like text from the LLM into HTML-formatted text compatible with Telegram.
    """
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        # Handle headings by making them bold
        heading_match = re.match(r'^(#+)\s+(.*)', line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            # Use bold for headings
            html_lines.append(f'<b>{heading_text}</b>')
            continue

        # Handle numbered lists
        num_list_match = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
        if num_list_match:
            indent = len(num_list_match.group(1))
            number = num_list_match.group(2)
            list_item = num_list_match.group(3).strip()
            list_item = convert_bold_italic(list_item)
            # Use plain text numbering
            html_lines.append(f'{number}. {list_item}')
            continue

        # Handle bullet lists
        bullet_list_match = re.match(r'^(\s*)-\s+(.*)', line)
        if bullet_list_match:
            indent = len(bullet_list_match.group(1))
            list_item = bullet_list_match.group(2).strip()
            list_item = convert_bold_italic(list_item)
            # Use bullet points
            html_lines.append(f'• {list_item}')
            continue

        # Handle empty lines
        if line.strip() == '':
            html_lines.append('')
            continue

        # Handle regular text
        paragraph = convert_bold_italic(line.strip())
        html_lines.append(paragraph)

    return '\n'.join(html_lines)

def convert_bold_italic(text):
    """
    Convert markdown-like bold and italic markers to HTML tags.
    """
    # Convert bold (**text**)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert italic (*text*)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text

def get_language_code(language_name):
    """
    Maps language names to their respective language codes.
    """
    mapping = {
        "English": "en",
        "Russian": "ru",
        "Indonesian": "id",
        # Add more mappings as needed
    }
    return mapping.get(language_name, "en")