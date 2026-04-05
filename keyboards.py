from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 О конференции", callback_data="info"),
            InlineKeyboardButton(text="🎤 Спикеры",       callback_data="speakers"),
        ],
        [
            InlineKeyboardButton(text="📍 Как добраться", callback_data="location"),
            InlineKeyboardButton(text="❓ FAQ",            callback_data="faq"),
        ],
        [
            InlineKeyboardButton(text="📞 Поддержка",     callback_data="support"),
        ],
    ])


def faq_keyboard(faq_list: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"❓ {item['q']}", callback_data=f"faq_{i}")]
        for i, item in enumerate(faq_list)
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")]
    ])
