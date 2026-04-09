from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def start_keyboard(lang: str, form_url: str | None = None) -> InlineKeyboardMarkup:
    open_form_text = "📝 Заполнить форму" if lang == "ru" else "📝 Fill out the form"
    filled_text = "✅ Я уже заполнил форму" if lang == "ru" else "✅ I already filled out the form"

    rows = []

    if form_url:
        rows.append([InlineKeyboardButton(text=open_form_text, url=form_url)])

    rows.append([InlineKeyboardButton(text=filled_text, callback_data="already_filled")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu(lang: str) -> InlineKeyboardMarkup:
    if lang == "en":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 About the conference", callback_data="info"),
                InlineKeyboardButton(text="🎤 Speakers", callback_data="speakers"),
            ],
            [
                InlineKeyboardButton(text="📍 Location", callback_data="location"),
                InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
            ],
            [
                InlineKeyboardButton(text="📞 Support", callback_data="support"),
            ],
        ])

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 О конференции", callback_data="info"),
            InlineKeyboardButton(text="🎤 Спикеры", callback_data="speakers"),
        ],
        [
            InlineKeyboardButton(text="📍 Локация", callback_data="location"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
        ],
        [
            InlineKeyboardButton(text="📞 Поддержка", callback_data="support"),
        ],
    ])


def faq_keyboard(faq_list: list[dict], lang: str) -> InlineKeyboardMarkup:
    buttons = []

    for i, item in enumerate(faq_list):
        q = item["q_en"] if lang == "en" else item["q_ru"]
        buttons.append([InlineKeyboardButton(text=f"❓ {q}", callback_data=f"faq_{i}")])

    back_text = "◀️ Back to menu" if lang == "en" else "◀️ Назад в меню"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_button(lang: str) -> InlineKeyboardMarkup:
    text = "◀️ Back to menu" if lang == "en" else "◀️ Назад в меню"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="menu")]
    ])


def faq_answer_keyboard(lang: str) -> InlineKeyboardMarkup:
    to_faq = "◀️ Back to FAQ" if lang == "en" else "◀️ К вопросам"
    to_menu = "🏠 Menu" if lang == "en" else "🏠 В меню"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=to_faq, callback_data="faq")],
        [InlineKeyboardButton(text=to_menu, callback_data="menu")],
    ])


def location_keyboard(lang: str, url: str) -> InlineKeyboardMarkup:
    open_map = "🗺 Open map" if lang == "en" else "🗺 Открыть карту"
    back = "◀️ Back" if lang == "en" else "◀️ Назад"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=open_map, url=url)],
        [InlineKeyboardButton(text=back, callback_data="menu")],
    ])