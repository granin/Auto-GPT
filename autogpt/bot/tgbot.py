import os
import time
import asyncio
import threading
import platform
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ContextTypes

ai_config_values = None
output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

# Dictionary to store chat_id as keys and their corresponding output/input files as values
chat_files = {}

def get_file_mtime(file_path: str) -> float:
    return os.stat(file_path).st_mtime

def monitor_file_changes(context, bot_event_loop, chat_id):
    last_mtime = None
    last_content = None
    chat_output_filename = chat_files[chat_id]["output"]
    chat_input_filename = chat_files[chat_id]["input"]

    while True:
        if os.path.exists(chat_output_filename):
            current_mtime = get_file_mtime(chat_output_filename)

            if last_mtime is None or current_mtime != last_mtime:
                with open(chat_output_filename, "r") as f:
                    content = f.read()
                    if content != last_content and content.strip() != "":
                        on_output_file_updated(content, context, bot_event_loop, chat_id)
                        last_content = content
                        last_mtime = current_mtime

        time.sleep(0.5)

def on_output_file_updated(content, context, bot_event_loop, chat_id):
    async def send_message():
        await context.bot.send_message(chat_id=chat_id, text=f"File updated: {content}")

    future = asyncio.run_coroutine_threadsafe(send_message(), bot_event_loop)
    future.result()

async def agree(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    chat_input_filename = chat_files[chat_id]["input"]
    with open(chat_input_filename, "w") as input_file:
        input_file.write("y")
    await update.message.reply_text('Agreed to continue')

async def disagree(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    chat_input_filename = chat_files[chat_id]["input"]
    with open(chat_input_filename, "w") as input_file:
        input_file.write("n")
    await update.message.reply_text('Exit program')

async def run_continuous_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().lower()
    if user_input.startswith("y -"):
        try:
            num_commands = int(user_input.split(" ")[1])
            with open(f"{input_filename}_{user_id}.txt", "w") as input_file:
                input_file.write(f"y -{num_commands}")
            await update.message.reply_text(f'Running {num_commands} continuous commands')
        except ValueError:
            await update.message.reply_text('Invalid input format. Use "y -N" where N is the number of continuous commands')

async def set_ai_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    global ai_config_values
    message_text = update.message.text
    _, name, role, *goals = message_text.split('|')
    ai_config_values = {
        'name': name.strip(),
        'role': role.strip(),
        'goals': [goal.strip() for goal in goals]
    }

    await update.message.reply_text(f"AI config set successfully:\n"
                                    f"Name: {name}\n"
                                    f"Role: {role}\n"
                                    f"Goals: {', '.join(goals)}")
async def restart_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    ai_settings_path = "/Users/m/git/1ai/Auto-GPT/ai_settings.yaml"

    if not os.path.exists(ai_settings_path):
        await update.message.reply_text("AI configuration is not set. Please use /set_ai_config or /start_all command to set the AI configuration.")
        return

    await start_and_monitor_autogpt(update, context)

async def start_all(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    _, name, role, *goals = message_text.split('|')

    if not goals:
        await update.message.reply_text("Please provide the AI Name, AI Role, and Goals in the format:\n"
                                        "/start_all | AI Name | AI Role | Goal 1 | Goal 2 | Goal 3")
        return

    # Set AI config
    global ai_config_values
    ai_config_values = {
        'name': name.strip(),
        'role': role.strip(),
        'goals': [goal.strip() for goal in goals]
    }


    await start_and_monitor_autogpt(update, context, user_id)  # Pass the user_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    chat_id = update.message.chat_id
    chat_files[chat_id] = {}
    chat_output_filename = f"Assistant_Reply_{chat_id}.txt"
    chat_input_filename = f"Processed_Input_{chat_id}.txt"
    chat_files[chat_id]["output"] = chat_output_filename
    chat_files[chat_id]["input"] = chat_input_filename

    await update.message.reply_text('Monitoring started')

    # Rename old session files
    if os.path.exists(chat_output_filename):
        rename_old_session_files(chat_output_filename)
    if os.path.exists(chat_input_filename):
        rename_old_session_files(chat_input_filename)

    # Create new empty files for the new session
    open(chat_output_filename, "w").close()
    open(chat_input_filename, "w").close()

    # Create the start event
    start_event = threading.Event()
    start_event.set()

    bot_event_loop = asyncio.get_event_loop()
    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context, bot_event_loop, chat_id))
    monitor_thread.start()



app = Application.builder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("disagree", disagree))
app.add_handler(CommandHandler("run_continuous_commands", run_continuous_commands))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_human_feedback))
app.add_handler(CommandHandler("start_all", start_all))
app.add_handler(CommandHandler("restart_all", restart_all))



app.run_polling()