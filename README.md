# Wonton Auto Farming Bot

## Recommendation before use

🔥🔥 PYTHON version must be 3.10 or higher 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features

| Feature | Supported |
|:-------:|:---------:|
| Multithreading | ✅ |
| Proxy binding to session | ✅ |
| Auto Referral of your accounts | ✅ |
| Automatic task completion | ✅ |
| Support for pyrogram .session | ✅ |
| Auto farming | ✅ |
| Auto Daily Reward | ✅ |
| Auto Play Game | ✅ |
| Auto Claim Invite Rewards | ✅ |

## Settings

| Setting | Description |
|:-------:|:-----------:|
| API_ID | Your Telegram API ID (integer) |
| API_HASH | Your Telegram API Hash (string) |
| REF_ID | Your referral ID |
| AUTO_FARMING | Enable auto farming (True / False) |
| AUTO_DAILY_REWARD | Automatically claim daily rewards (True / False) |
| AUTO_PLAY_GAME | Automatically play games (True / False) |
| POINTS_COUNT | Range of points for games (e.g., [100, 300]) |
| AUTO_TASK | Automatically complete tasks (True / False) |
| FAKE_USERAGENT | Use a fake user agent for sessions (True / False) |
| AUTO_CLAIM_INVITE_REWARDS | Automatically claim invite rewards (True / False) |
| USE_RANDOM_DELAY_IN_RUN | Use random delay at startup (True / False) |
| RANDOM_DELAY_IN_RUN | Range for random delay at startup (e.g., [0, 15]) |
| USE_PROXY_FROM_FILE | Use proxies from a file (True / False) |

## Quick Start 📚

To quickly install libraries and run the bot:
- On Windows: Open `run.bat`
- On Linux: Run `run.sh`

## Prerequisites

Before you begin, ensure you have Python 3.10 or higher installed.

## Obtaining API Keys

1. Go to [my.telegram.org](https://my.telegram.org) and log in.
2. Click on "API development tools" and fill out the form.
3. Save the API_ID and API_HASH in your `.env` file.

## Installation

Clone the repository and install dependencies:

```shell
git clone https://github.com/nikhilpatidar/wonton-bot.git
cd wonton-bot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/wonton-bot >>> python3 main.py --action (1/2)
# Or
~/wonton-bot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/wonton-bto >>> python main.py --action (1/2)
# Or
~/wonton-bot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```
