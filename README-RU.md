# Бот для автоматического фарминга Wonton

## Рекомендация перед использованием

🔥🔥 Версия PYTHON должна быть 3.10 или выше 🔥🔥

> 🇷 🇺 README на английском доступен [здесь](README.md)

## Функции

| Функция | Поддержка |
|:-------:|:---------:|
| Многопоточность | ✅ |
| Привязка прокси к сессии | ✅ |
| Авто-реферальная система | ✅ |
| Автоматическое выполнение задач | ✅ |
| Поддержка .session файлов pyrogram | ✅ |
| Автоматический фарминг | ✅ |
| Автоматическое получение ежедневной награды | ✅ |
| Автоматическая игра | ✅ |
| Автоматическое получение наград за приглашения | ✅ |

## Настройки

| Настройка | Описание |
|:---------:|:--------:|
| API_ID | Ваш Telegram API ID (целое число) |
| API_HASH | Ваш Telegram API Hash (строка) |
| REF_ID | Ваш реферальный ID |
| AUTO_FARMING | Включить автоматический фарминг (True / False) |
| AUTO_DAILY_REWARD | Автоматически получать ежедневные награды (True / False) |
| AUTO_PLAY_GAME | Автоматически играть в игры (True / False) |
| POINTS_COUNT | Диапазон очков для игр (например, [100, 300]) |
| AUTO_TASK | Автоматически выполнять задачи (True / False) |
| FAKE_USERAGENT | Использовать поддельный User-Agent для сессий (True / False) |
| AUTO_CLAIM_INVITE_REWARDS | Автоматически получать награды за приглашения (True / False) |
| USE_RANDOM_DELAY_IN_RUN | Использовать случайную задержку при запуске (True / False) |
| RANDOM_DELAY_IN_RUN | Диапазон для случайной задержки при запуске (например, [0, 15]) |
| USE_PROXY_FROM_FILE | Использовать прокси из файла (True / False) |

## Быстрый старт 📚

Для быстрой установки библиотек и запуска бота:
- На Windows: Откройте `run.bat`
- На Linux: Запустите `run.sh`

## Предварительные требования

Перед началом убедитесь, что у вас установлен Python 3.10 или выше.

## Получение API ключей

1. Перейдите на [my.telegram.org](https://my.telegram.org) и войдите в систему.
2. Нажмите на "API development tools" и заполните форму.
3. Сохраните API_ID и API_HASH в вашем файле `.env`.

## Установка

Клонируйте репозиторий и установите зависимости:

```shell
git clone https://github.com/nikhilpatidar/wonton-bot.git
cd wonton-bot
```
Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/wonton-bot >>> python3 main.py --action (1/2)
# Или
~/Tomarket >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/wonton-bot >>> python main.py --action (1/2)
# Или
~/wonton-bot >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
