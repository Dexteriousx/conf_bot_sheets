"""
sheets.py — вся работа с Google Sheets

Таблица = источник правды.
Google Forms пишет строки → бот читает и дописывает Telegram ID / флаги.
"""
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    SPREADSHEET_ID, GOOGLE_CREDS_FILE, SHEET_NAME,
    COL_EMAIL, COL_TELEGRAM_ID, COL_CONFIRMED,
    COL_REM_7, COL_REM_3, COL_REM_2, COL_REM_1,
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _get_service():
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _get_all_rows() -> list[list]:
    """Возвращает все строки листа (включая заголовок)."""
    try:
        svc = _get_service()
        result = (
            svc.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME)
            .execute()
        )
        return result.get("values", [])
    except HttpError as e:
        logging.error(f"Sheets read error: {e}")
        return []


def _write_cell(row_index: int, col_index: int, value: str):
    """row_index — 0-based индекс строки данных (без заголовка)."""
    # Sheets API: строки с 1, +1 за заголовок → row_index + 2
    sheet_row = row_index + 2
    col_letter = chr(ord("A") + col_index)
    cell_range = f"{SHEET_NAME}!{col_letter}{sheet_row}"
    try:
        svc = _get_service()
        svc.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=cell_range,
            valueInputOption="RAW",
            body={"values": [[value]]},
        ).execute()
    except HttpError as e:
        logging.error(f"Sheets write error: {e}")


def _safe_get(row: list, col: int, default: str = "") -> str:
    try:
        return row[col]
    except IndexError:
        return default


# ─── Public API ───────────────────────────────────────────────────────────────

def find_row_by_email(email: str) -> tuple[int, list] | None:
    """
    Ищет строку по email (без учёта регистра).
    Возвращает (row_index, row) или None.
    row_index — 0-based, не считая заголовка.
    """
    rows = _get_all_rows()
    for i, row in enumerate(rows[1:], start=0):  # пропускаем заголовок
        if _safe_get(row, COL_EMAIL, "").strip().lower() == email.strip().lower():
            return i, row
    return None


def confirm_participant(row_index: int, telegram_id: int):
    """Записывает Telegram ID и отметку 'confirmed'."""
    _write_cell(row_index, COL_TELEGRAM_ID, str(telegram_id))
    _write_cell(row_index, COL_CONFIRMED, "TRUE")


def get_unreminded_participants(days: int) -> list[tuple[int, int]]:
    """
    Возвращает список (row_index, telegram_id) участников,
    которым ещё не отправляли напоминание за N дней.
    """
    col_map = {7: COL_REM_7, 3: COL_REM_3, 2: COL_REM_2, 1: COL_REM_1}
    col = col_map.get(days)
    if col is None:
        return []

    rows = _get_all_rows()
    result = []
    for i, row in enumerate(rows[1:], start=0):
        confirmed  = _safe_get(row, COL_CONFIRMED, "").upper()
        tg_id_str  = _safe_get(row, COL_TELEGRAM_ID, "")
        reminded   = _safe_get(row, col, "").upper()

        if confirmed == "TRUE" and tg_id_str.isdigit() and reminded != "TRUE":
            result.append((i, int(tg_id_str)))

    return result


def mark_reminded(row_index: int, days: int):
    col_map = {7: COL_REM_7, 3: COL_REM_3, 2: COL_REM_2, 1: COL_REM_1}
    col = col_map.get(days)
    if col is not None:
        _write_cell(row_index, col, "TRUE")


def get_participant_by_telegram_id(telegram_id: int) -> tuple[int, list] | None:
    rows = _get_all_rows()
    for i, row in enumerate(rows[1:], start=0):
        if _safe_get(row, COL_TELEGRAM_ID, "") == str(telegram_id):
            return i, row
    return None


def is_confirmed(telegram_id: int) -> bool:
    result = get_participant_by_telegram_id(telegram_id)
    if not result:
        return False
    _, row = result
    return _safe_get(row, COL_CONFIRMED, "").upper() == "TRUE"
