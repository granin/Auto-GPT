import os
import platform
import time
import threading
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from capture_utils import get_human_feedback


async def start_and_monitor_autogpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id

    # Start Auto-GPT
    ai_settings_path = write_ai_settings()
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
    monitor_thread.start()

def write_ai_settings():
    global ai_config_values

    ai_settings_path = "/Users/m/git/1ai/Auto-GPT/ai_settings.yaml"

    with open(ai_settings_path, "w") as outfile:
        outfile.write("ai_name: {}\n".format(ai_config_values["name"]))
        outfile.write("ai_role: {}\n".format(ai_config_values["role"]))
        outfile.write("ai_goals:\n")
        for goal in ai_config_values["goals"]:
            outfile.write("- '{}'\n".format(goal))

    return ai_settings_path


async def start_autogpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ai_config_values

    if not ai_config_values:
        await update.message.reply_text("AI configuration is not set. Please use /set_ai_config command to set the AI configuration.")
        return

    ai_settings_path = write_ai_settings()

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
async def restart_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_settings_path = "/Users/m/git/1ai/Auto-GPT/ai_settings.yaml"

    if not os.path.exists(ai_settings_path):
        await update.message.reply_text("AI configuration is not set. Please use /set_ai_config or /start_all command to set the AI configuration.")
        return

    await start_and_monitor_autogpt(update, context)

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

    await start_and_monitor_autogpt(update, context)

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
    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context, bot_event_loop, start_event))
    monitor_thread.start()

app = Application.builder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("disagree", disagree))
app.add_handler(CommandHandler("run_continuous_commands", run_continuous_commands))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_human_feedback))
app.add_handler(CommandHandler("start_all", start_all))
app.add_handler(CommandHandler("restart_all", restart_all))



app.run_polling()