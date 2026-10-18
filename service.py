import json
from pathlib import Path

import httpx
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"


def get_documents() -> list[dict]:
    url = "https://www.greatcircus.ru/api/avisodev/list/1?lang=en&onlyvisible=1"
    response = httpx.get(url=url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_tomorrow_document_id() -> int | None:
    tomorrow_date = (date.today() + timedelta(days=1)).isoformat()
    documents = get_documents()
    for document in documents:
        if document.get('document_date') == tomorrow_date:
            return document.get('id')
    return None


def load_last_document_id() -> int | None:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("last_document_id")
    except FileNotFoundError:
        return None


def save_last_document_id(document_id: int) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump({"last_document_id": document_id}, file, indent=4)
