import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, COL_TELEGRAM_ID, COL_CONFIRMED
from handlers import router
from scheduler import start_scheduler
from sheets import _get_all_rows, _safe_get

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)


async def send_once(bot: Bot):
    text = (
        "🎥 <b>Conference livestream</b>\n\n"
        "Dear all, here is the link to the Conference:\n\n"
        "🔗 https://www.youtube.com/live/qzH4AagHM1I?si=P0IZSQ-glFSksRHv"
    )

    rows = _get_all_rows()
    sent = 0

    for row in rows[1:]:
        tg_id = _safe_get(row, COL_TELEGRAM_ID, "").strip()
        confirmed = _safe_get(row, COL_CONFIRMED, "").strip().upper()

        if tg_id.isdigit() and confirmed == "TRUE":
            try:
                await bot.send_message(int(tg_id), text, parse_mode="HTML")
                sent += 1
            except Exception as e:
                logging.warning(f"Broadcast failed for {tg_id}: {e}")

    logging.info(f"Broadcast finished. Sent to {sent} users")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await send_once(bot)   # ВРЕМЕННО: разовая рассылка

    start_scheduler(bot)

    logging.info("Бот запущен ✅")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())