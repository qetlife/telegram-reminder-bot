# Telegram Reminder Bot

A Telegram bot that helps you set and manage reminders for yourself and other users.

## Features

- Set reminders with flexible time formats
- Manage contacts
- Send reminders to other users
- Persistent storage of reminders and contacts

## Installation & Setup

There are two ways to run this bot:

### 1. Using Docker (Recommended)

#### Prerequisites
- Docker installed on your system
- Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))

#### Steps
1. Clone the repository:
```bash
git clone https://github.com/qetlife/telegram-reminder-bot.git
cd telegram-reminder-bot
```

2. Build the Docker image:
```bash
docker build -t telegram-reminder-bot .
```

3. Run the container:
```bash
docker run -d --name telegram-reminder-bot -e TELEGRAM_TOKEN="your-token-here" telegram-reminder-bot
```

#### Docker Management Commands
```bash
# View logs
docker logs telegram-reminder-bot

# Stop the bot
docker stop telegram-reminder-bot

# Start the bot again
docker start telegram-reminder-bot

# Remove the container
docker rm telegram-reminder-bot
```

### 2. Using Python Directly

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Steps
1. Clone the repository:
```bash
git clone https://github.com/qetlife/telegram-reminder-bot.git
cd telegram-reminder-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
TELEGRAM_TOKEN=your-token-here
```

4. Run the bot:
```bash
python bot.py
```

## Bot Commands

- `/start` - Get started with the bot
- `/remind` - Set a reminder
- `/add_contact` - Add a new contact
- `/help` - General Help

### Time Format Examples

- `1h` - 1 hour from now
- `30m` - 30 minutes from now
- `2d` - 2 days from now
- `15:30` - Today at 15:30
- `25-12-2024 14:30` - Specific date and time