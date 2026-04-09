# 🤖 Telegram бот конференции — Google Sheets версия

## Структура проекта

```
conf_bot/
├── bot.py            # Точка входа
├── config.py         # ⚙️ ВСЕ НАСТРОЙКИ ЗДЕСЬ
├── sheets.py         # Работа с Google Sheets
├── handlers.py       # Команды и кнопки бота
├── keyboards.py      # Клавиатуры
├── scheduler.py      # Автонапоминания
├── requirements.txt
├── Procfile          # Для Railway
└── credentials.json  # (создать самому — инструкция ниже)
```

---

## Шаг 1 — Создать Telegram бота

1. Открыть Telegram → найти `@BotFather`
2. Написать `/newbot` → придумать имя и username
3. Скопировать **API Token**
4. Настроить команды через `/setcommands`:
   ```
   start - Начать / подтвердить регистрацию
   menu - Главное меню
   ```

---

## Шаг 2 — Настроить Google Sheets

### 2.1 Создать таблицу

1. Открыть [Google Sheets](https://sheets.google.com) → создать новую таблицу
2. Добавить заголовки в первую строку (именно в таком порядке):

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| Метка времени | Email | Имя | Телефон | Telegram ID | Confirmed | Reminded 7 | Reminded 3 | Reminded 2 | Reminded 1 |

3. Скопировать **ID таблицы** из URL:
   ```
   https://docs.google.com/spreadsheets/d/ВОТ_ЭТО_ID/edit
   ```

### 2.2 Создать Google Form и связать с таблицей

1. Открыть [Google Forms](https://forms.google.com) → создать форму
2. Добавить поля: **Email**, **Имя**, **Телефон**
3. В форме: **Ответы → значок таблицы → Выбрать существующую таблицу**
4. Выбрать таблицу из шага 2.1

> Теперь каждая отправка формы = новая строка в таблице.

---

## Шаг 3 — Создать сервисный аккаунт Google

1. Открыть [console.cloud.google.com](https://console.cloud.google.com)
2. Создать новый проект (или выбрать существующий)
3. Включить **Google Sheets API**:
   - Меню → APIs & Services → Enable APIs → найти "Google Sheets API" → Enable
4. Создать сервисный аккаунт:
   - APIs & Services → Credentials → Create Credentials → Service Account
   - Имя: `conf-bot` → Create → Done
5. Открыть созданный аккаунт → вкладка **Keys** → Add Key → JSON
6. Скачать JSON-файл → переименовать в `credentials.json` → положить в папку бота
7. Скопировать **email** сервисного аккаунта (вида `conf-bot@project.iam.gserviceaccount.com`)
8. Открыть Google Sheets таблицу → **Поделиться** → вставить этот email → роль **Редактор**

---

## Шаг 4 — Заполнить config.py

```python
BOT_TOKEN      = "токен от BotFather"
SPREADSHEET_ID = "ID таблицы из URL"

CONF_DATE      = datetime(2025, 9, 15)   # дата конференции
CONF_NAME      = "Название конференции"
CONF_PLACE     = "Адрес"
CONF_STREAM    = "https://ссылка_на_трансляцию"
SUPPORT_USERNAME = "@ваш_support"
```

Также заполни `SPEAKERS` и `FAQ`.

---

## Шаг 5 — Запустить локально

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
python bot.py
```

---

## Шаг 6 — Деплой на Railway.app

1. Залить папку бота на GitHub
2. Открыть [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. В проекте → **Variables** → добавить переменные:
   ```
   BOT_TOKEN      = ваш_токен
   SPREADSHEET_ID = id_таблицы
   ```
4. Файл `credentials.json` загрузить через:
   - Settings → Volumes или добавить содержимое как переменную `GOOGLE_CREDS_JSON`

> ⚠️ Не коммить `credentials.json` в GitHub! Добавь его в `.gitignore`.

---

## Как работает флоу

```
Google Form → Google Sheets (строка с email, именем, телефоном)
                    ↓
Пользователь → /start в боте → вводит email
                    ↓
Бот ищет email в Sheets → находит → записывает Telegram ID → подтверждает ✅
                    ↓
Каждый день в 10:00 → проверяет дату → рассылает напоминания за 7/3/2/1 день
                    ↓
После отправки → ставит отметку в Sheets (Reminded = TRUE)
```

---

## Редактировать FAQ и спикеров

Всё в `config.py`:

```python
SPEAKERS = [
    {"name": "Имя Фамилия", "topic": "Тема доклада"},
]

FAQ = [
    {"q": "Вопрос?", "a": "Ответ."},
]
```

Сохрани и перезапусти бота.
