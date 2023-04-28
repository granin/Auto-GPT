import os
import time
import threading
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio


output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

def rename_old_session_files(file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    new_file_name = f"{file_path}_session_{timestamp}.txt"
    os.rename(file_path, new_file_name)

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def monitor_file_changes(context, bot_event_loop, start_event):
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    last_mtime = None
    last_content = None
    last_input_mtime = None
    last_input_content = None
    user_input_expected = False

    # Wait for the start event to be set
    start_event.wait()

    while True:
        if os.path.exists(output_filename):
            current_mtime = get_file_mtime(output_filename)

            if last_mtime is None or current_mtime != last_mtime:
                with open(output_filename, "r") as f:
                    content = f.read()
                    if content != last_content and content.strip() != "":
                        user_input_expected = on_output_file_updated(content, context, bot_event_loop)
                        last_content = content
                        last_mtime = current_mtime
                    else:
                        user_input_expected = False

        else:
            last_mtime = None

        # Check if input file is updated correctly
        if os.path.exists(input_filename):
            current_input_mtime = get_file_mtime(input_filename)

            if last_input_mtime is None or current_input_mtime != last_input_mtime:
                with open(input_filename, "r") as input_file:
                    input_content = input_file.read()
                    if input_content != last_input_content and input_content.strip() != "":
                        print(f"Input file content: {input_content}")
                        last_input_content = input_content
                        last_input_mtime = current_input_mtime

        time.sleep(0.5)

def on_output_file_updated(content, context, bot_event_loop):
    global chat_id
    if chat_id:
        async def send_message():
            await context.bot.send_message(chat_id=chat_id, text=f"File updated: {content}")

        future = asyncio.run_coroutine_threadsafe(send_message(), bot_event_loop)
        future.result()
    return True



def get_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = update.message.text.strip().lower()
    return user_input

def on_exit():
    print("Stopped monitoring file.")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(input_filename, "w") as input_file:
        input_file.write("y")
    await update.message.reply_text('Agreed to continue')

async def two_steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(input_filename, "w") as input_file:
        input_file.write("y -2")
    await update.message.reply_text('Running 2 continuous commands')

async def disagree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(input_filename, "w") as input_file:
        input_file.write("n")
    await update.message.reply_text('Exit program')

async def run_continuous_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = get_user_input(update, context)
    if user_input.startswith("y -"):
        try:
            num_commands = int(user_input.split(" ")[1])
            with open(input_filename, "w") as input_file:
                input_file.write(f"y -{num_commands}")
            await update.message.reply_text(f'Running {num_commands} continuous commands')
        except ValueError:
            await update.message.reply_text('Invalid input format. Use "y -N" where N is the number of continuous commands')


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


app = ApplicationBuilder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("2", two_steps))
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("disagree", disagree))
app.add_handler(CommandHandler("run_continuous_commands", run_continuous_commands))
app.add_handler(CommandHandler("start", start))
app.run_polling()
