import os
import datetime
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from telegram.error import BadRequest

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

REMINDERS_FILE = 'reminders.txt'
CONTACTS_FILE = 'contacts.txt'

active_reminders = {}

class Reminder:
    def __init__(self, remindee_chat_id, victim_chat_id, victim_name, message, remind_time):
        self.remindee_chat_id = remindee_chat_id
        self.victim_chat_id = victim_chat_id
        self.victim_name = victim_name
        self.message = message
        self.remind_time = remind_time



def save_reminder(reminder):
    with open(REMINDERS_FILE, 'a') as f:
        f.write(f"{reminder.remindee_chat_id}|{reminder.victim_chat_id}|{reminder.victim_name}|{reminder.message}|{reminder.remind_time.strftime('%d-%m-%Y %H:%M')}\n")

def load_reminders():
    if not os.path.exists(REMINDERS_FILE):
        return []
    
    reminders = []
    with open(REMINDERS_FILE, 'r') as f:
        for line in f.readlines():
            if line.strip():
                remindee_chat_id, victim_chat_id, victim_name, message, remind_time = line.strip().split('|')
                reminders.append(Reminder(
                    int(remindee_chat_id),
                    int(victim_chat_id),
                    victim_name,
                    message,
                    datetime.datetime.strptime(remind_time, '%d-%m-%Y %H:%M')
                ))
    return reminders

def save_contact(user_id: int, contact_id: int, contact_name: str):
    with open(CONTACTS_FILE, 'a') as f:
        f.write(f"{user_id}|{contact_id}|{contact_name}\n")

def get_contacts(user_id: int):
    if not os.path.exists(CONTACTS_FILE):
        return {}
    
    contacts = {}
    with open(CONTACTS_FILE, 'r') as f:
        for line in f.readlines():
            if line.strip():
                owner_id, contact_id, contact_name = line.strip().split('|')
                if int(owner_id) == user_id:
                    contacts[contact_name] = int(contact_id)
    return contacts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    await update.message.reply_text(
        f'Hi! Your user ID is `{user_id}`. I can help you set reminders.\n\n'
        'Available commands:\n'
        '/remind <time> <message> - Set a reminder\n'
        '/add_contact <id> <name> - Add a contact\n\n'
        'Time format: 1h, 2d, 30m, etc.\n'
        'Or you can add a date: 2024-12-08 18:19\n'
        'Example: /remind 1h Take a break'
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Available commands:\n'
        '/remind <time> <message> - Set a reminder\n'
        '/add_contact <id> <name> - Add a contact\n\n'
        'To get the user ID, use /start command.\n'
        'If you want to add a contact, you need to ask them to use /start command to get their ID.\n'
        'Time format: 1h, 2d, 30m, etc.\n'
        'Or you can add a date: 2024-12-08 18:19\n'
        'Date must follow the format: dd-MM-yyyy HH:mm or just HH:mm\n'
        'Example: /remind 1h Take a break'
        'Example: /remind 15:30 Take a break'
        'Example: /remind 25-12-2024 15:30 Take a break'
    )

async def add_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a contact with their Telegram ID and name."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide contact ID and name.\n"
            "Example: /add_contact 123456789 John"
        )
        return

    try:
        contact_id = int(context.args[0])
        contact_name = ' '.join(context.args[1:])
        user_id = update.effective_user.id

        save_contact(user_id, contact_id, contact_name)
        
        await update.message.reply_text(
            f"Contact {contact_name} (ID: {contact_id}) has been added successfully!"
        )

    except ValueError:
        await update.message.reply_text(
            "Invalid contact ID! Please provide a valid numeric ID.\n"
            "You can ask your contact to use /start command to get their ID."
        )

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set a reminder."""
    user_id = update.effective_user.id
    contacts = get_contacts(user_id)

    if not contacts:
        await update.message.reply_text("You have no contacts saved. Please add contacts first.")
        return

    buttons = [[
        InlineKeyboardButton(contact_name, callback_data=f"{contact_id}|{contact_name}")
        for contact_name, contact_id in contacts.items()
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text("Please select a contact:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses for contacts."""
    query = update.callback_query
    contact_id, contact_name = query.data.split('|')
    await query.answer() 

    await query.message.reply_text("Please provide the time (e.g., 1h) and the message.")

    context.user_data['contact_id'] = contact_id
    context.user_data['contact_name'] = contact_name
async def process_reminder_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the reminder details after contact selection."""
    if 'contact_id' not in context.user_data or 'contact_name' not in context.user_data:
        await update.message.reply_text("No contact selected. Please start again.")
        return
    
    contact_id = context.user_data['contact_id']
    contact_name = context.user_data['contact_name']
    
    args = update.message.text
    
    if not args or len(args) < 2:
        await update.message.reply_text("Please provide both time and message.\n"
                                          "Example: 1h Take a break")
        return
    
    if'-' in args or '/' in args:
        time_str = args.split(' ')[0] + ' ' + args.split(' ')[1]
        message = ' '.join(args.split(' ')[2:])
    else:
        time_str = args.split(' ')[0]
        message = ' '.join(args.split(' ')[1:])

    if(message == ''):
        await update.message.reply_text("Please provide a message.")
        return

    if'-' in time_str or '/' in time_str:
        try:
            remind_time = datetime.datetime.strptime(time_str, '%d-%m-%Y %H:%M')
        except ValueError:
            await update.message.reply_text("Invalid time format! Example: /remind 1h Take a break or use a date")
            return
    elif ':' in time_str:
        try:
            now = datetime.datetime.now()
            remind_time = now.replace(hour=int(time_str.split(':')[0]), minute=int(time_str.split(':')[1]), second=0, microsecond=0)
            if remind_time < now:
                remind_time += datetime.timedelta(days=1) 
        except ValueError:
            await update.message.reply_text("Invalid time format! Example: /remind 1h Take a break or use a date")
            return
    else:
        try:
            unit = time_str[-1].lower()
            amount = int(time_str[:-1])
            
            if unit == 'm' or unit == 'min':
                delta = datetime.timedelta(minutes=amount)
            elif unit == 'h':
                delta = datetime.timedelta(hours=amount)
            elif unit == 'd':
                delta = datetime.timedelta(days=amount)
            else:
                await update.message.reply_text("Invalid time format! Use m for minutes, h for hours, or d for days.")
                return

            remind_time = datetime.datetime.now() + delta
            
  
        except ValueError:
            await update.message.reply_text("Invalid time format! Example: /remind 1h Take a break or use a date")
            return
        
    reminder = Reminder(
        remindee_chat_id=update.effective_chat.id,
        victim_chat_id=contact_id,
        victim_name=contact_name,
        message=message,
        remind_time=remind_time
    )    
    
    save_reminder(reminder)
    await update.message.reply_text(
        f"I'll remind {contact_name} about '{message}' on {remind_time.strftime('%d-%m-%Y %H:%M')}"
    )

async def send_reminders(context, reminder):
    """Send reminders at 1-second intervals, max 10 messages."""
    active_reminders[reminder.victim_chat_id] = True
    message_count = 0
    max_messages = 10
    
    context.job_queue.run_once(
        send_single_reminder,
        1,  # run immediately
        data={
            'reminder': reminder,
            'message_count': message_count,
            'max_messages': max_messages
        }
    )

async def send_single_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send a single reminder and schedule the next one if needed."""
    job = context.job
    reminder = job.data['reminder']
    message_count = job.data['message_count']
    max_messages = job.data['max_messages']

    try:
        if active_reminders.get(reminder.victim_chat_id, False):
            await context.bot.send_message(
                chat_id=reminder.victim_chat_id,
                text=f"Reminder: {reminder.message})",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("OK", callback_data='stop_reminders')
                ]])
            )

            if message_count == 0 and reminder.remindee_chat_id != reminder.victim_chat_id:
                await context.bot.send_message(
                    chat_id=reminder.remindee_chat_id,
                    text=f"I reminded {reminder.victim_name} about: {reminder.message})",
                )
            
            message_count += 1
            
            if message_count < max_messages and active_reminders.get(reminder.victim_chat_id, False):
                context.job_queue.run_once(
                    send_single_reminder,
                    10,  # 1 second delay
                    data={
                        'reminder': reminder,
                        'message_count': message_count,
                        'max_messages': max_messages
                    }
                )
            elif message_count >= max_messages:
                active_reminders[reminder.victim_chat_id] = False
                await context.bot.send_message(
                    chat_id=reminder.victim_chat_id,
                    text="Maximum number of reminders reached. Stopping reminders."
                )
    except BadRequest:
        active_reminders[reminder.victim_chat_id] = False

async def stop_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop sending reminders."""
    query = update.callback_query
    chat_id = query.message.chat_id
    
    active_reminders[chat_id] = False
    
    await query.answer()
    
    await query.edit_message_text(
        text=f"{query.message.text}\n\nReminders stopped.",
        reply_markup=None
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Reminders have been stopped successfully."
    )

async def task(context: ContextTypes.DEFAULT_TYPE):
    """Check reminders at the start of every minute."""
    current_time = datetime.datetime.now()
    reminders = load_reminders()
    
    new_reminders = []
    
    for reminder in reminders:
        if current_time >= reminder.remind_time:
            try:
                await send_reminders(context, reminder)
            except BadRequest:
                pass
        else:
            new_reminders.append(reminder)
    
    with open(REMINDERS_FILE, 'w') as f:
        for reminder in new_reminders:
            f.write(f"{reminder.user_id}|{reminder.chat_id}|{reminder.message}|{reminder.remind_time}\n")

    context.job_queue.run_once(task, when=60-datetime.datetime.now().second)
    

def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("remind", remind))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("add_contact", add_contact))

    application.add_handler(CallbackQueryHandler(stop_reminders, pattern='^stop_reminders$')) 
    application.add_handler(CallbackQueryHandler(button_handler))  

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_reminder_details))

    job_queue = application.job_queue
    job_queue.run_once(task, when=60-datetime.datetime.now().second)

    application.run_polling()

if __name__ == '__main__':
    print("Bot is running...")
    main()

