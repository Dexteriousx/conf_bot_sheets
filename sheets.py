"""
sheets.py — вся работа с Google Sheets
"""
import os
import json
import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    SPREADSHEET_ID,
    GOOGLE_CREDS_FILE,
    SHEET_NAME,
    COL_EMAIL,
    COL_TELEGRAM_ID,
    COL_CONFIRMED,
    COL_REM_7,
    COL_REM_3,
    COL_REM_2,
    COL_REM_1,
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    creds_json = os.getenv("GOOGLE_CREDS_JSON")

    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(
            info,
            scopes=SCOPES,
        )
    else:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDS_FILE,
            scopes=SCOPES,
        )

    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _get_all_rows() -> list[list]:
    try:
        service = _get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=SPREADSHEET_ID,
                range=SHEET_NAME,
            )
            .execute()
        )
        return result.get("values", [])
    except HttpError as e:
        logging.error(f"Sheets read error: {e}")
        return []
    except Exception as e:
        logging.error(f"Sheets unexpected read error: {e}")
        return []


def _write_cell(row_index: int, col_index: int, value: str):
    sheet_row = row_index + 2
    col_letter = chr(ord("A") + col_index)
    cell_range = f"'{SHEET_NAME}'!{col_letter}{sheet_row}"

    try:
        service = _get_service()
        (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=SPREADSHEET_ID,
                range=cell_range,
                valueInputOption="RAW",
                body={"values": [[value]]},
            )
            .execute()
        )
    except HttpError as e:
        logging.error(f"Sheets write error: {e}")
    except Exception as e:
        logging.error(f"Sheets unexpected write error: {e}")


def _safe_get(row: list, col: int, default: str = "") -> str:
    try:
        return row[col]
    except IndexError:
        return default


def find_row_by_email(email: str) -> tuple[int, list] | None:
    rows = _get_all_rows()
    if not rows:
        return None

    email = email.strip().lower()

    for i, row in enumerate(rows[1:], start=0):
        current_email = _safe_get(row, COL_EMAIL, "").strip().lower()
        if current_email == email:
            return i, row

    return None


def confirm_participant(row_index: int, telegram_id: int):
    _write_cell(row_index, COL_TELEGRAM_ID, str(telegram_id))
    _write_cell(row_index, COL_CONFIRMED, "TRUE")


def get_unreminded_participants(days: int) -> list[tuple[int, int]]:
    col_map = {
        7: COL_REM_7,
        3: COL_REM_3,
        2: COL_REM_2,
        1: COL_REM_1,
    }

    reminder_col = col_map.get(days)
    if reminder_col is None:
        return []

    rows = _get_all_rows()
    if not rows:
        return []

    result = []

    for i, row in enumerate(rows[1:], start=0):
        confirmed = _safe_get(row, COL_CONFIRMED, "").strip().upper()
        tg_id_str = _safe_get(row, COL_TELEGRAM_ID, "").strip()
        reminded = _safe_get(row, reminder_col, "").strip().upper()

        if confirmed == "TRUE" and tg_id_str.isdigit() and reminded != "TRUE":
            result.append((i, int(tg_id_str)))

    return result


def mark_reminded(row_index: int, days: int):
    col_map = {
        7: COL_REM_7,
        3: COL_REM_3,
        2: COL_REM_2,
        1: COL_REM_1,
    }

    reminder_col = col_map.get(days)
    if reminder_col is not None:
        _write_cell(row_index, reminder_col, "TRUE")


def get_participant_by_telegram_id(telegram_id: int) -> tuple[int, list] | None:
    rows = _get_all_rows()
    if not rows:
        return None

    tg_id_str = str(telegram_id)

    for i, row in enumerate(rows[1:], start=0):
        current_tg_id = _safe_get(row, COL_TELEGRAM_ID, "").strip()
        if current_tg_id == tg_id_str:
            return i, row

    return None


def is_confirmed(telegram_id: int) -> bool:
    result = get_participant_by_telegram_id(telegram_id)
    if result is None:
        return False

    _, row = result
    return _safe_get(row, COL_CONFIRMED, "").strip().upper() == "TRUE"