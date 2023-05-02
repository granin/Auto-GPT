import os
import time
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import yaml

from capture_utils import get_human_feedback
from bot import get_file_mtime, rename_old_session_files
import subprocess

def write_custom_ai_settings():
    ai_settings_custom = {
        "ai_name": "AI Name",
        "ai_role": "AI Role",
        "ai_goals": ["Goal 1", "Goal 2", "Goal 3"],
    }

    ai_settings_path = "ai_settings_custom.yaml"

    with open(ai_settings_path, "w") as outfile:
        outfile.write("ai_name: {}\n".format(ai_settings_custom["ai_name"]))
        outfile.write("ai_role: {}\n".format(ai_settings_custom["ai_role"]))
        outfile.write("ai_goals:\n")
        for goal in ai_settings_custom["ai_goals"]:
            outfile.write("- '{}'\n".format(goal))

    return ai_settings_path

import os
import platform

async def start_autogpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ai_config_values

    if not ai_config_values:
        await update.message.reply_text("AI configuration is not set. Please use /set_ai_config command to set the AI configuration.")
        return

    ai_settings_filename = "ai_settings_custom.yaml"
    ai_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ai_settings_custom.yaml')

    write_custom_ai_settings()

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

chat_id = None

def monitor_file_changes(context, bot_event_loop, start_event):
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
                        on_output_file_updated(content, context, bot_event_loop)
                        last_content = content
                        last_mtime = current_mtime

        time.sleep(0.5)

def on_output_file_updated(content, context, bot_event_loop):
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

async def run_continuous_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().lower()
    if user_input.startswith("y -"):
        try:
            num_commands = int(user_input.split(" ")[1])
            with open(input_filename, "w") as input_file:
                input_file.write(f"y -{num_commands}")
            await update.message.reply_text(f'Running {num_commands} continuous commands')
        except ValueError:
            await update.message.reply_text('Invalid input format. Use "y -N" where N is the number of continuous commands')
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    my_user_id = 37252140  # Replace with your Telegram user ID

    if update.message.from_user.id != my_user_id:
        await update.message.reply_text("Unauthorized access. This bot is for private use only.")
        return

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
    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context, bot_event_loop, start_event))
    monitor_threl triead.start()

app = Application.builder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("disagree", disagree))
app.add_handler(CommandHandler("run_continuous_commands", run_continuous_commands))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_human_feedback))
app.add_handler(CommandHandler("set_ai_config", set_ai_config))
app.add_handler(CommandHandler("start_autogpt", start_autogpt))

app.run_polling()

