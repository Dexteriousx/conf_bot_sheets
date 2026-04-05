from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    CONF_NAME, CONF_DATE_STR, CONF_PLACE, CONF_FORMAT,
    CONF_MAP, SUPPORT_USERNAME, WELCOME_TEXT,
    SPEAKERS, FAQ, CONF_TIME, CONF_STREAM, REGISTRATION_FORM_URL,
)
from sheets import find_row_by_email, confirm_participant, is_confirmed
from keyboards import main_menu, faq_keyboard, back_button

router = Router()


class Registration(StatesGroup):
    waiting_email = State()


def _registration_help_keyboard() -> InlineKeyboardMarkup | None:
    if not REGISTRATION_FORM_URL:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заполнить форму", url=REGISTRATION_FORM_URL)]
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    if is_confirmed(tg_id):
        await message.answer(
            f"👋 С возвращением! Ты уже зарегистрирован на <b>{CONF_NAME}</b>.\n\n"
            "Чем могу помочь?",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
        return

    await message.answer(
        WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=_registration_help_keyboard(),
    )
    await state.set_state(Registration.waiting_email)


@router.message(Registration.waiting_email)
async def process_email(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Отправь email обычным текстом.")
        return

    email = message.text.strip()

    if "@" not in email or "." not in email:
        await message.answer("⚠️ Это не похоже на email. Попробуй ещё раз:")
        return

    await message.answer("🔍 Проверяю регистрацию...")

    result = find_row_by_email(email)

    if result is None:
        await message.answer(
            "❌ <b>Email не найден</b> в списке участников.\n\n"
            "Убедись, что:\n"
            "• Ты заполнил форму на сайте\n"
            "• Email введён без ошибок\n\n"
            f"Если ещё не заполнял форму — сделай это, затем снова напиши /start.\n"
            f"Если проблема осталась — напиши в поддержку: {SUPPORT_USERNAME}",
            parse_mode="HTML",
            reply_markup=_registration_help_keyboard(),
        )
        return

    row_index, _ = result
    confirm_participant(row_index, message.from_user.id)
    await state.clear()

    await message.answer(
        f"✅ <b>Регистрация подтверждена!</b>\n\n"
        f"Добро пожаловать на <b>{CONF_NAME}</b> 🎉\n\n"
        f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
        f"⏰ <b>Время:</b> {CONF_TIME}\n"
        f"📍 <b>Место:</b> {CONF_PLACE}\n\n"
        "Я пришлю напоминания за 7, 3, 2 и 1 день до события.\n\n"
        "Выбери что тебя интересует 👇",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    if not is_confirmed(message.from_user.id):
        await message.answer("Сначала подтверди регистрацию — напиши /start")
        return
    await message.answer("Главное меню 👇", reply_markup=main_menu())


@router.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery):
    await call.message.edit_text("Главное меню 👇", reply_markup=main_menu())
    await call.answer()


@router.callback_query(F.data == "info")
async def cb_info(call: CallbackQuery):
    await call.message.edit_text(
        f"📅 <b>{CONF_NAME}</b>\n\n"
        f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
        f"⏰ <b>Время:</b> {CONF_TIME}\n"
        f"📍 <b>Место:</b> {CONF_PLACE}\n"
        f"🎥 <b>Формат:</b> {CONF_FORMAT}\n\n"
        f"🔗 <b>Трансляция:</b> {CONF_STREAM}",
        parse_mode="HTML",
        reply_markup=back_button(),
    )
    await call.answer()


@router.callback_query(F.data == "speakers")
async def cb_speakers(call: CallbackQuery):
    if not SPEAKERS:
        text = "🎤 <b>Спикеры конференции</b>\n\nСписок спикеров будет опубликован позже."
    else:
        lines = ["🎤 <b>Спикеры конференции:</b>\n"]
        for i, s in enumerate(SPEAKERS, 1):
            lines.append(f"{i}. <b>{s['name']}</b>\n   📌 {s['topic']}")
        text = "\n".join(lines)

    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_button(),
    )
    await call.answer()


@router.callback_query(F.data == "location")
async def cb_location(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть на карте", url=CONF_MAP)],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="menu")],
    ])
    await call.message.edit_text(
        f"📍 <b>Адрес:</b> {CONF_PLACE}\n\n"
        "Нажми кнопку ниже, чтобы открыть на карте 👇",
        parse_mode="HTML",
        reply_markup=kb,
    )
    await call.answer()


@router.callback_query(F.data == "faq")
async def cb_faq(call: CallbackQuery):
    await call.message.edit_text(
        "❓ <b>Часто задаваемые вопросы</b>\n\nВыбери вопрос 👇",
        parse_mode="HTML",
        reply_markup=faq_keyboard(FAQ),
    )
    await call.answer()


@router.callback_query(F.data.startswith("faq_"))
async def cb_faq_answer(call: CallbackQuery):
    idx = int(call.data.split("_")[1])
    item = FAQ[idx]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К вопросам", callback_data="faq")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
    ])
    await call.message.edit_text(
        f"❓ <b>{item['q']}</b>\n\n{item['a']}",
        parse_mode="HTML",
        reply_markup=kb,
    )
    await call.answer()


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    await call.message.edit_text(
        f"📞 <b>Поддержка</b>\n\n"
        f"По всем вопросам пишите: {SUPPORT_USERNAME}\n\n"
        "Время работы: пн–пт, 10:00–18:00",
        parse_mode="HTML",
        reply_markup=back_button(),
    )
    await call.answer()


@router.message()
async def unknown(message: Message):
    if is_confirmed(message.from_user.id):
        await message.answer("Используй меню 👇", reply_markup=main_menu())
    else:
        await message.answer(
            "Напиши /start чтобы начать.",
            reply_markup=_registration_help_keyboard(),
        )
