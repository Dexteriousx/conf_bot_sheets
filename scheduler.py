import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from config import CONF_DATE, REMINDERS
from sheets import get_unreminded_participants, mark_reminded

scheduler = AsyncIOScheduler(timezone="Asia/Almaty")


def start_scheduler(bot: Bot):
    scheduler.add_job(
        send_reminders,
        trigger="cron",
        hour=10,
        minute=0,
        args=[bot],
        id="daily_reminder",
        replace_existing=True,
    )
    scheduler.start()
    logging.info("Планировщик напоминаний запущен ✅")


async def send_reminders(bot: Bot):
    today = datetime.now().date()
    conf_day = CONF_DATE.date()
    days_left = (conf_day - today).days

    logging.info(f"[Scheduler] До конференции: {days_left} дней")

    if days_left not in REMINDERS:
        return

    text = REMINDERS[days_left]
    participants = get_unreminded_participants(days_left)

    sent = 0
    for row_index, tg_id in participants:
        try:
            await bot.send_message(tg_id, text, parse_mode="HTML")
            mark_reminded(row_index, days_left)
            sent += 1
        except Exception as e:
            logging.warning(f"Не удалось отправить {tg_id}: {e}")

    logging.info(f"[Scheduler] Напоминание за {days_left} дней → отправлено {sent} участникам")