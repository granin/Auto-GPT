# Auto-GPT/autogpt/bot/tgbot.py
import platform
import os
import time
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
import asyncio
from bot import write_ai_settings, get_file_mtime, rename_old_session_files
from capture_utils import get_human_feedback
import subprocess
ai_config_values = None

async def start_autogpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    ai_settings_path = "/Users/m/git/1ai/Auto-GPT/autogpt/bot/ai_settings_custom.yaml"
    #
    if not os.path.exists(ai_settings_path):
        await update.message.reply_text("AI configuration file not found. Please use /set_ai_config command to set the AI configuration.")
        return

    run_sh_path = "/Users/m/git/1ai/Auto-GPT/run.sh"
    script_dir = os.path.dirname(run_sh_path)
    ai_settings_abs_path = os.path.abspath(ai_settings_path)
    command = f"cd {os.path.dirname(ai_settings_abs_path)} && ./run.sh --ai-settings {ai_settings_abs_path}"
    system = platform.system()
    if system == "Darwin" or system == "Linux":
        os.system(f"gnome-terminal -- bash -c '{command}; exec bash'" if system == "Linux" else f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'")
        await update.message.reply_text("Auto-GPT process started in a new terminal.")
    else:
        await update.message.reply_text(f"Unsupported platform. Run the following command in a separate terminal:\n\n{command}")

output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

global chat_id
chat_id = None
def monitor_file_changes(context, bot_event_loop, start_event, user_id: int):
    last_mtime = None
    last_content = None

    # Wait for the start event to be set
    start_event.wait()

    while True:
        if os.path.exists(output_filename):
            current_mtime = get_file_mtime(output_filename)

            if last_mtime is None or current_mtime != last_mtime:
                with open(output_filename, "r") as f:
                    content = f.read()
                    if content != last_content and content.strip() != "":
                        on_output_file_updated(content, context, bot_event_loop, user_id)
                        last_content = content
                        last_mtime = current_mtime

        time.sleep(0.5)

def on_output_file_updated(content, context, bot_event_loop, user_id: int):

    global chat_id
    if chat_id:
        async def send_message():
            await context.bot.send_message(chat_id=chat_id, text=f"File updated: {content}")

        future = asyncio.run_coroutine_threadsafe(send_message(), bot_event_loop)
        future.result()

async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(input_filename, "w") as input_file:
        input_file.write("y")
    await update.message.reply_text('Agreed to continue')

async def disagree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(input_filename, "w") as input_file:
        input_file.write("n")
    await update.message.reply_text('Exit program')

async def set_ai_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def restart_autogpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ai_config_values

    # Write AI settings to file
    ai_settings_path = write_ai_settings(ai_config_values)

    run_sh_path = "/Users/m/git/1ai/Auto-GPT/run.sh"
    script_dir = os.path.dirname(run_sh_path)
    ai_settings_abs_path = os.path.abspath(ai_settings_path)
    command = f"cd {os.path.dirname(ai_settings_abs_path)} && ./run.sh --ai-settings {ai_settings_abs_path}"
    system = platform.system()
    if system == "Darwin" or system == "Linux":
        os.system(f"gnome-terminal -- bash -c '{command}; exec bash'" if system == "Linux" else f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'")
        await update.message.reply_text("Auto-GPT process started in a new terminal.")
    else:
        await update.message.reply_text(f"Unsupported platform. Run the following command in a separate terminal:\n\n{command}")

async def start_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    # Write AI settings to file
    ai_settings_path = write_ai_settings(ai_config_values)  # Pass ai_config_values as an argument

    # Start Auto-GPT
    run_sh_path = "/Users/m/git/1ai/Auto-GPT/run.sh"
    script_dir = os.path.dirname(run_sh_path)
    ai_settings_abs_path = os.path.abspath(ai_settings_path)
    command = f"cd {os.path.dirname(ai_settings_abs_path)} && ./run.sh --ai-settings {ai_settings_abs_path}"
    system = platform.system()
    if system == "Darwin" or system == "Linux":
        os.system(f"gnome-terminal -- bash -c '{command}; exec bash'" if system == "Linux" else f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'")
        await update.message.reply_text("Auto-GPT process started in a new terminal.")
    else:
        await update.message.reply_text(f"Unsupported platform. Run the following command in a separate terminal:\n\n{command}")

    # Start monitoring
    global chat_id
    chat_id = update.message.chat_id
    user_id = chat_id
    await update.message.reply_text('Monitoring started')

    # Rename old session files
    if os.path.exists(output_filename):
        rename_old_session_files(output_filename)
    if os.path.exists(input_filename):
        rename_old_session_files(input_filename)

    # Create new empty files for the new session
    open(output_filename, "w").close()
    open(input_filename, "w").close()

    # Create the start event
    start_event = threading.Event()
    start_event.set()

    bot_event_loop = asyncio.get_event_loop()
    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context, bot_event_loop, start_event, user_id))
    monitor_thread.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id
    chat_id = update.message.chat_id
    await update.message.reply_text('Monitoring started')

    # Rename old session files
    if os.path.exists(output_filename):
        rename_old_session_files(output_filename)
    if os.path.exists(input_filename):
        rename_old_session_files(input_filename)

    # Create new empty files for the new session
    open(output_filename, "w").close()
    open(input_filename, "w").close()

    # Create the start event
    start_event = threading.Event()
    start_event.set()

    bot_event_loop = asyncio.get_event_loop()
    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context, bot_event_loop, start_event, user_id))
    monitor_thread.start()

app = Application.builder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()

app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("disagree", disagree))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_human_feedback))
app.add_handler(CommandHandler("start_all", start_all))

app.run_polling()
