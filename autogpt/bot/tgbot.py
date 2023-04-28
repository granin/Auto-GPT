import os
import time
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def monitor_file_changes(context):
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    last_mtime = None
    last_content = None
    user_input_expected = False

    while True:
        if os.path.exists(output_filename):
            current_mtime = get_file_mtime(output_filename)

            if last_mtime is None or current_mtime != last_mtime:
                with open(output_filename, "r") as f:
                    content = f.read()
                    if content != last_content and content.strip() != "":
                        user_input_expected = on_output_file_updated(content, context)
                        last_content = content
                        last_mtime = current_mtime
                    else:
                        user_input_expected = False

        else:
            last_mtime = None

        time.sleep(0.5)


def on_output_file_updated(content, context):
    global chat_id
    if chat_id:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(context.bot.send_message(chat_id=chat_id, text=f"File updated: {content}"))
    return True
def get_user_input():
    return "y"  # This will be replaced by the Telegram command

def on_exit():
    print("Stopped monitoring file.")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open("Processed_Input.txt", "w") as input_file:
        input_file.write("y")
    await update.message.reply_text('Agreed to continue')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id
    chat_id = update.message.chat_id
    await update.message.reply_text('Monitoring started')

    monitor_thread = threading.Thread(target=monitor_file_changes, args=(context,))
    monitor_thread.start()


app = ApplicationBuilder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("start", start))
app.run_polling()