import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "8389489228:AAEFzeN2I7UNob9iEHrBQkhDkoNYfK7WyYI")

# ID таблицы Google Sheets (из URL: docs.google.com/spreadsheets/d/ВОТ_ЭТО/edit)
SPREADSHEET_ID = "1VCzRlf1-TN7tcOMfGvEj4-nN3HfBzKK6p9na7JyI0Wo"

# Путь к JSON-ключу сервисного аккаунта Google
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")

# Ссылка на Google Form / форму регистрации
REGISTRATION_FORM_URL = os.getenv("REGISTRATION_FORM_URL", "https://forms.gle/WXGnNbbsZZtbKUYc8")

# ─── КОНФЕРЕНЦИЯ ──────────────────────────────────────────────────────────────

CONF_DATE     = datetime(2026, 4, 18)
CONF_NAME     = "Toastmasters 2026 International Conference"
CONF_TAGLINE  = "Nomads of the Digital Era: Drive Change with Human Skills"
CONF_DATE_STR = "18 апреля 2026"
CONF_TIME     = "10:00–18:00"
CONF_PLACE    = "Алматы, University of International Business (UIB)"
CONF_FORMAT   = "Гибридный формат: офлайн + онлайн-трансляция"
CONF_STREAM   = "Ссылка на трансляцию будет отправлена позже"
CONF_MAP      = "https://maps.google.com/?q=University+of+International+Business+Almaty"
CONF_LANG     = "Русский, английский и казахский"
SUPPORT_USERNAME = "@conference_support"

WELCOME_TEXT = (
    "👋 Привет! Я бот конференции\n\n"
    f"<b>{CONF_NAME}</b>\n"
    f"<i>«{CONF_TAGLINE}»</i>\n\n"
    "Конференция посвящена лидерству, публичным выступлениям, "
    "коммуникации и развитию human skills в цифровую эпоху.\n\n"
    f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
    f"📍 <b>Место:</b> {CONF_PLACE}\n"
    f"🎥 <b>Формат:</b> {CONF_FORMAT}\n\n"
    "Для подтверждения участия введи <b>email</b>, "
    "который ты указал при регистрации на сайте 👇"
)

PROGRAM_TRACKS = [
    {"track": "🤖 AI & Technology",             "desc": "Искусственный интеллект и будущее технологий"},
    {"track": "🏆 Leadership & Future of Work", "desc": "Лидерство и рынок труда завтрашнего дня"},
    {"track": "🗣 Communication & Influence",    "desc": "Коммуникация, влияние и публичные выступления"},
]

PROGRAM_FORMATS = [
    "🎤 Keynote-выступления",
    "💬 Панельные дискуссии",
    "🛠 Воркшопы",
    "💼 Career Corner — карьерная мастерская",
    "🏅 Конкурсы Toastmasters",
]

ORGANIZERS = [
    "Almaty Toastmasters",
    "Astana Toastmasters",
    "Kazakh Toastmasters",
]

SPEAKERS = [
    # {"name": "Имя Фамилия", "topic": "Тема доклада"},
]

FAQ = [
    {
        "q": "Что это за конференция?",
        "a": (
            f"<b>{CONF_NAME}</b> — «{CONF_TAGLINE}».\n\n"
            "Конференция посвящена лидерству, публичным выступлениям, "
            "коммуникации и развитию human skills в цифровую эпоху."
        ),
    },
    {
        "q": "Когда и где пройдёт?",
        "a": f"🗓 <b>{CONF_DATE_STR}</b>\n📍 {CONF_PLACE}",
    },
    {
        "q": "Это офлайн или онлайн?",
        "a": "Гибридный формат: офлайн в Алматы + онлайн-трансляция для всех желающих.",
    },
    {
        "q": "На каком языке будет мероприятие?",
        "a": f"Мероприятие пройдёт на трёх языках: {CONF_LANG}.",
    },
    {
        "q": "Для кого эта конференция?",
        "a": (
            "Конференция будет интересна:\n"
            "• Специалистам 25+\n"
            "• Предпринимателям\n"
            "• Менеджерам и руководителям\n"
            "• Всем, кто развивает навыки коммуникации и лидерства"
        ),
    },
    {
        "q": "Какие темы будут на конференции?",
        "a": (
            "Три основных трека:\n"
            "🤖 AI & Technology\n"
            "🏆 Leadership & Future of Work\n"
            "🗣 Communication & Influence"
        ),
    },
    {
        "q": "Что будет в программе?",
        "a": (
            "В программе конференции:\n"
            "🎤 Keynote-выступления\n"
            "💬 Панельные дискуссии\n"
            "🛠 Воркшопы\n"
            "💼 Career Corner — карьерная мастерская\n"
            "🏅 Конкурсы Toastmasters\n\n"
            "Подробная программа будет объявлена позже."
        ),
    },
    {
        "q": "Кто организатор?",
        "a": (
            "Конференцию организует Toastmasters community Казахстана:\n"
            "• Almaty Toastmasters\n"
            "• Astana Toastmasters\n"
            "• Kazakh Toastmasters"
        ),
    },
    {
        "q": "Как связаться с организаторами?",
        "a": f"Напишите нам: {SUPPORT_USERNAME}",
    },
]

REMINDERS = {
    7: (
        f"📅 До <b>{CONF_NAME}</b> осталась одна неделя!\n\n"
        f"🗓 <b>Дата:</b> {CONF_DATE_STR}\n"
        f"📍 <b>Место:</b> {CONF_PLACE}\n"
        f"🎥 <b>Формат:</b> {CONF_FORMAT}\n\n"
        "Программа и детали — в меню бота. До встречи! 🚀"
    ),
    3: (
        f"⏳ До <b>{CONF_NAME}</b> осталось 3 дня!\n\n"
        f"📍 <b>Адрес:</b> {CONF_PLACE}\n\n"
        "Готовь вопросы для спикеров и не забудь пригласить коллег 💬"
    ),
    2: (
        f"🔔 Послезавтра — <b>{CONF_NAME}</b>!\n\n"
        f"📍 {CONF_PLACE}\n\n"
        "Не забудь зарядить телефон и взять хорошее настроение 😊"
    ),
    1: (
        f"🚀 Завтра — <b>{CONF_NAME}</b>!\n\n"
        f"📍 <b>Место:</b> {CONF_PLACE}\n\n"
        "Ждём тебя! До встречи завтра 👋"
    ),
}

COL_TIMESTAMP   = 0
COL_EMAIL       = 1
COL_NAME        = 2
COL_PHONE       = 3
COL_CONFIRMED   = 9
COL_REM_7       = 10
COL_REM_3       = 11
COL_REM_2       = 12
COL_REM_1       = 13
COL_TELEGRAM_ID = 14

SHEET_NAME = "Ответы на форму (1)"
