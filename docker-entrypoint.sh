#!/bin/bash

# Check if TELEGRAM_TOKEN is provided
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "Error: TELEGRAM_TOKEN environment variable is required"
    exit 1
fi

# Create .env file
echo "TELEGRAM_TOKEN=$TELEGRAM_TOKEN" > .env

# Run the bot
exec python bot.py 