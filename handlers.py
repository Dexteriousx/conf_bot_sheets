from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    CONF_NAME,
    CONF_DATE_STR,
    CONF_PLACE,
    CONF_FORMAT,
    CONF_MAP,
    SUPPORT_USERNAME,
    CONF_TIME,
    CONF_STREAM,
    SPEAKERS,
)
from sheets import find_row_by_email, confirm_participant, is_confirmed
from keyboards import (
    language_keyboard,
    start_keyboard,
    main_menu,
    faq_keyboard,
    back_button,
    faq_answer_keyboard,
    location_keyboard,
)

router = Router()

REGISTRATION_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdXaAirAz2iyyYAUu3v0AIa2nrO34xe81Jr_qOb4J6uPQUZRA/viewform?usp=dialog"

user_lang: dict[int, str] = {}


FAQ_ITEMS = [
    {
        "q_ru": "Что это за конференция?",
        "a_ru": (
            f"<b>{CONF_NAME}</b>\n\n"
            "Конференция посвящена лидерству, публичным выступлениям, "
            "коммуникации и развитию human skills в цифровую эпоху."
        ),
        "q_en": "What is this conference about?",
        "a_en": (
            f"<b>{CONF_NAME}</b>\n\n"
            "This conference is dedicated to leadership, public speaking, "
            "communication, and human skills development in the digital era."
        ),
    },
    {
        "q_ru": "Когда и где пройдет мероприятие?",
        "a_ru": f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n📍 <b>Место:</b> {CONF_PLACE}",
        "q_en": "When and where will the event take place?",
        "a_en": f"🗓 <b>Date:</b> {CONF_DATE_STR}\n📍 <b>Location:</b> {CONF_PLACE}",
    },
    {
        "q_ru": "Это офлайн или онлайн?",
        "a_ru": "Формат мероприятия — гибридный: офлайн + онлайн.",
        "q_en": "Is it offline or online?",
        "a_en": "The event format is hybrid: offline + online.",
    },
    {
        "q_ru": "На каком языке будет мероприятие?",
        "a_ru": "Конференция проходит на русском и английском языках.",
        "q_en": "What languages will be used at the event?",
        "a_en": "The conference will be held in Russian and English.",
    },
    {
        "q_ru": "Сколько стоит участие?",
        "a_ru": "Участие бесплатное, регистрация обязательна.",
        "q_en": "How much does participation cost?",
        "a_en": "Participation is free, but registration is required.",
    },
    {
        "q_ru": "Как связаться с организаторами?",
        "a_ru": f"Напишите нам: {SUPPORT_USERNAME}",
        "q_en": "How can I contact the organizers?",
        "a_en": f"Write to us: {SUPPORT_USERNAME}",
    },
]


class Registration(StatesGroup):
    waiting_email = State()


def get_lang(user_id: int) -> str:
    return user_lang.get(user_id, "ru")


def tr(user_id: int, ru: str, en: str) -> str:
    return en if get_lang(user_id) == "en" else ru


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите язык / Choose language",
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.in_({"lang_ru", "lang_en"}))
async def cb_set_language(call: CallbackQuery, state: FSMContext):
    lang = "ru" if call.data == "lang_ru" else "en"
    user_lang[call.from_user.id] = lang
    tg_id = call.from_user.id

    if is_confirmed(tg_id):
        await state.clear()
        await call.message.edit_text(
            tr(
                tg_id,
                "👋 С возвращением! Ты уже подтвержден в системе.\n\nВыбери, что тебя интересует 👇",
                "👋 Welcome back! You are already confirmed.\n\nChoose what you need 👇",
            ),
            reply_markup=main_menu(lang),
        )
        return

    await call.message.edit_text(
        tr(
            tg_id,
            "👋 Добро пожаловать в официальный бот конференции\n\n"
            f"<b>{CONF_NAME}</b>\n\n"
            "Чтобы подтвердить участие, сделай 2 шага:\n\n"
            "1. Сначала заполни регистрационную форму\n"
            "2. Затем нажми кнопку <b>«Я уже заполнил форму»</b> и отправь сюда свой email\n\n"
            "⚠️ Важно: после заполнения формы нужно ещё раз написать свою почту в боте для подтверждения.",
            "👋 Welcome to the official conference bot\n\n"
            f"<b>{CONF_NAME}</b>\n\n"
            "To confirm your participation, please complete 2 steps:\n\n"
            "1. First fill out the registration form\n"
            "2. Then tap <b>“I already filled out the form”</b> and send your email here\n\n"
            "⚠️ Important: after submitting the form, you still need to send your email in the bot to confirm your participation.",
        ),
        parse_mode="HTML",
        reply_markup=start_keyboard(lang, REGISTRATION_FORM_URL),
    )


@router.callback_query(F.data == "already_filled")
async def cb_already_filled(call: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.waiting_email)
    await call.message.answer(
        tr(
            call.from_user.id,
            "📩 Теперь просто отправь сюда email, который ты указал в форме.\n\nПример: <code>example@gmail.com</code>",
            "📩 Now simply send the email address you used in the form.\n\nExample: <code>example@gmail.com</code>",
        ),
        parse_mode="HTML",
    )


@router.message(Registration.waiting_email)
async def process_email(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            tr(
                message.from_user.id,
                "⚠️ Пожалуйста, отправь email текстом.",
                "⚠️ Please send your email as text.",
            )
        )
        return

    email = message.text.strip()

    if "@" not in email or "." not in email:
        await message.answer(
            tr(
                message.from_user.id,
                "⚠️ Это не похоже на email. Попробуй ещё раз:",
                "⚠️ This does not look like an email. Please try again:",
            )
        )
        return

    await message.answer(
        tr(
            message.from_user.id,
            "🔍 Проверяю регистрацию...",
            "🔍 Checking registration...",
        )
    )

    result = find_row_by_email(email)

    if result is None:
        await message.answer(
            tr(
                message.from_user.id,
                "❌ <b>Email не найден</b> в списке участников.\n\n"
                "Убедись, что:\n"
                "• ты заполнил форму\n"
                "• email введён без ошибок\n\n"
                f"Если проблема осталась — напиши: {SUPPORT_USERNAME}",
                "❌ <b>Email not found</b> in the participant list.\n\n"
                "Please make sure that:\n"
                "• you filled out the form\n"
                "• the email is entered correctly\n\n"
                f"If the problem remains, contact: {SUPPORT_USERNAME}",
            ),
            parse_mode="HTML",
            reply_markup=start_keyboard(get_lang(message.from_user.id), REGISTRATION_FORM_URL),
        )
        return

    row_index, _ = result
    confirm_participant(row_index, message.from_user.id)
    await state.clear()

    await message.answer(
        tr(
            message.from_user.id,
            f"✅ <b>Регистрация подтверждена!</b>\n\n"
            f"Добро пожаловать на <b>{CONF_NAME}</b> 🎉\n\n"
            f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
            f"⏰ <b>Время:</b> {CONF_TIME}\n"
            f"📍 <b>Место:</b> {CONF_PLACE}\n\n"
            "Я пришлю напоминания перед событием.\n\n"
            "Выбери, что тебя интересует 👇",
            f"✅ <b>Registration confirmed!</b>\n\n"
            f"Welcome to <b>{CONF_NAME}</b> 🎉\n\n"
            f"🗓 <b>Date:</b> {CONF_DATE_STR}\n"
            f"⏰ <b>Time:</b> {CONF_TIME}\n"
            f"📍 <b>Location:</b> {CONF_PLACE}\n\n"
            "I will send reminders before the event.\n\n"
            "Choose what you need 👇",
        ),
        parse_mode="HTML",
        reply_markup=main_menu(get_lang(message.from_user.id)),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    if not is_confirmed(message.from_user.id):
        await message.answer(
            tr(
                message.from_user.id,
                "Сначала подтверди регистрацию — нажми /start",
                "Please confirm your registration first — press /start",
            )
        )
        return

    await message.answer(
        tr(message.from_user.id, "Главное меню 👇", "Main menu 👇"),
        reply_markup=main_menu(get_lang(message.from_user.id)),
    )


@router.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery):
    await call.message.edit_text(
        tr(call.from_user.id, "Главное меню 👇", "Main menu 👇"),
        reply_markup=main_menu(get_lang(call.from_user.id)),
    )


@router.callback_query(F.data == "info")
async def cb_info(call: CallbackQuery):
    await call.message.edit_text(
        tr(
            call.from_user.id,
            f"📅 <b>{CONF_NAME}</b>\n\n"
            f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
            f"⏰ <b>Время:</b> {CONF_TIME}\n"
            f"📍 <b>Место:</b> {CONF_PLACE}\n"
            f"🎥 <b>Формат:</b> {CONF_FORMAT}\n\n"
            f"🔗 <b>Трансляция:</b> {CONF_STREAM}",
            f"📅 <b>{CONF_NAME}</b>\n\n"
            f"🗓 <b>Date:</b> {CONF_DATE_STR}\n"
            f"⏰ <b>Time:</b> {CONF_TIME}\n"
            f"📍 <b>Location:</b> {CONF_PLACE}\n"
            f"🎥 <b>Format:</b> {CONF_FORMAT}\n\n"
            f"🔗 <b>Stream:</b> {CONF_STREAM}",
        ),
        parse_mode="HTML",
        reply_markup=back_button(get_lang(call.from_user.id)),
    )


@router.callback_query(F.data == "speakers")
async def cb_speakers(call: CallbackQuery):
    lang = get_lang(call.from_user.id)

    if not SPEAKERS:
        text = (
            "🎤 <b>Спикеры будут объявлены позже.</b>"
            if lang == "ru"
            else "🎤 <b>Speakers will be announced later.</b>"
        )
        await call.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=back_button(lang),
        )
        return

    lines = ["🎤 <b>Спикеры конференции:</b>\n"] if lang == "ru" else ["🎤 <b>Conference speakers:</b>\n"]

    for i, s in enumerate(SPEAKERS, 1):
        lines.append(f"{i}. <b>{s['name']}</b>\n   📌 {s['topic']}")

    await call.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_button(lang),
    )


@router.callback_query(F.data == "location")
async def cb_location(call: CallbackQuery):
    await call.message.edit_text(
        tr(
            call.from_user.id,
            f"📍 <b>Адрес:</b> {CONF_PLACE}\n\nНажми кнопку ниже, чтобы открыть карту 👇",
            f"📍 <b>Address:</b> {CONF_PLACE}\n\nTap the button below to open the map 👇",
        ),
        parse_mode="HTML",
        reply_markup=location_keyboard(get_lang(call.from_user.id), CONF_MAP),
    )


@router.callback_query(F.data == "faq")
async def cb_faq(call: CallbackQuery):
    lang = get_lang(call.from_user.id)

    await call.message.edit_text(
        "❓ <b>Часто задаваемые вопросы</b>\n\nВыбери вопрос 👇"
        if lang == "ru"
        else "❓ <b>Frequently Asked Questions</b>\n\nChoose a question 👇",
        parse_mode="HTML",
        reply_markup=faq_keyboard(FAQ_ITEMS, lang),
    )


@router.callback_query(F.data.startswith("faq_"))
async def cb_faq_answer(call: CallbackQuery):
    lang = get_lang(call.from_user.id)
    idx = int(call.data.split("_")[1])
    item = FAQ_ITEMS[idx]

    question = item["q_ru"] if lang == "ru" else item["q_en"]
    answer = item["a_ru"] if lang == "ru" else item["a_en"]

    await call.message.edit_text(
        f"❓ <b>{question}</b>\n\n{answer}",
        parse_mode="HTML",
        reply_markup=faq_answer_keyboard(lang),
    )


@router.callback_query(F.data == "support")
async def cb_support(call: CallbackQuery):
    await call.message.edit_text(
        tr(
            call.from_user.id,
            f"📞 <b>Поддержка</b>\n\n"
            f"По всем вопросам пишите: {SUPPORT_USERNAME}\n\n"
            "Время ответа: пн–пт, 10:00–18:00",
            f"📞 <b>Support</b>\n\n"
            f"For any questions, contact: {SUPPORT_USERNAME}\n\n"
            "Response time: Mon–Fri, 10:00–18:00",
        ),
        parse_mode="HTML",
        reply_markup=back_button(get_lang(call.from_user.id)),
    )


@router.message()
async def unknown(message: Message):
    if is_confirmed(message.from_user.id):
        await message.answer(
            tr(message.from_user.id, "Используй меню 👇", "Use the menu 👇"),
            reply_markup=main_menu(get_lang(message.from_user.id)),
        )
    else:
        await message.answer(
            tr(
                message.from_user.id,
                "Нажми /start, чтобы начать.",
                "Press /start to begin.",
            )
        )