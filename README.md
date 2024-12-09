# Telegram Reminder Bot

A simple Telegram bot that helps you set reminders for yourself or others.

## Features

- Set reminders with custom messages
- Supports different time units (minutes, hours, days)
- Persists reminders in a text file
- Mentions users when their reminder is due

## Commands

- `/start` - Start the bot and get usage instructions
- `/remind <time> <message>` - Set a reminder
  - Time format: `<number><unit>`
    - Units: `m` (minutes), `h` (hours), `d` (days)
  - Example: `/remind 1h Take a break`
- `/add_contact <id> <name>` - Add a contact
  - Example: `/add_contact 123456789 John`

## Setup

1. Create a new Telegram bot by talking to [@BotFather](https://t.me/botfather)
2. Copy your bot token
3. Create a `.env` file and add your token:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   ```
4. Install required packages:
   ```
   pip install python-telegram-bot python-dotenv "python-telegram-bot[job-queue]"
   ```
5. Run the bot:
   ```
   python bot.py
   ```

## Requirements

- Python 3.8 or higher
- python-telegram-bot
- python-dotenv
