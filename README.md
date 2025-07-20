# Telegram Bot — Freight Price Calculator & Support

Этот Telegram-бот предназначен для расчёта стоимости доставки и связи с менеджером. Работает на Python, использует Aiogram и SQLite. Развёрнут на VPS под Ubuntu, запускается как systemd-сервис и функционирует 24/7.

---

## 📌 Основные возможности

- 📦 Расчёт стоимости доставки из Европы
- 📗 Сбор пользовательских заявок в SQLite-базу (`bot.db`)
- 🤖 Поддержка команд:
  - `/start` — запускает бота с выбором действия
  - `Рассчитать стоимость` — вызывает форму для расчёта
  - `Менеджер` — отправляет ссылку на контакт Telegram
  - `FAQ` — часто задаваемые вопросы

---

## ⚙️ Стек технологий

- Python 3.8+ (используется venv)
- Aiogram (Telegram Bot API framework)
- SQLite3 (база данных)
- systemd (для автозапуска бота)

---

## 📁 Структура проекта

```bash
idk/                        # Рабочая директория бота
├── core_bot_ftp.py         # Главный скрипт запуска
├── .env                    # Переменные окружения (API токены и ключи)
├── bot.db                  # SQLite база данных
└── venv/                   # Виртуальное окружение Python
```

---

## 🧑‍💻 Как развернуть бота

### 1. Клонировать проект на VPS (Ubuntu)

```bash
git clone <repo_url>
cd idk
```

### 2. Создать и активировать виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env` файл

```env
BOT_TOKEN=your_bot_token
FREECURRENCY_API_KEY=your_api_key
```

### 5. Настроить systemd-сервис

Создай файл `/etc/systemd/system/telegrambot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/idk
ExecStart=/home/botuser/idk/venv/bin/python3 core_bot_ftp.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. Включить и запустить сервис

```bash
sudo systemctl daemon-reexec
sudo systemctl enable telegrambot
sudo systemctl start telegrambot
```

Проверка:

```bash
systemctl status telegrambot
```

---

## 🧪 Работа с базой данных

Подключение:

```bash
sqlite3 bot.db
```

Команды:

```sql
.tables                   -- список таблиц
SELECT * FROM request_details LIMIT 5;  -- просмотр первых записей
.quit                    -- выход
```

---

## 🔒 Безопасность

- 🛑 Root-вход по SSH отключён
- 🔑 Авторизация через SSH-ключи
- 🦼️ Удалены ненужные пакеты
- 🕒 Настроен KeepAlive для предотвращения обрыва SSH

---

> 📮 Поддержка и вопросы — [@lil\_georgii](https://t.me/lil_georgii)

