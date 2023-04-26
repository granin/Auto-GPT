from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from bot import run_bot
from input_processing import process_input
import threading

def on_output_file_updated(content):
    global chat_id, bot_instance
    if chat_id:
        bot_instance.send_message(chat_id=chat_id, text=f"File updated: {content}")
    return True

def get_user_input():
    return "y"  # This will be replaced by the Telegram command

def on_exit():
    print("Stopped monitoring file.")

def monitor_bot():
    output_filename = 'Assistant_Reply.txt'
    input_filename = 'Processed_Input.txt'

    run_bot(output_filename, input_filename, on_output_file_updated, get_user_input, process_input, on_exit)

def start(update: Update, context: CallbackContext) -> None:
    global chat_id
    chat_id = update.message.chat_id
    update.message.reply_text('Monitoring started')

def agree(update: Update, context: CallbackContext) -> None:
    with open("Processed_Input.txt", "w") as input_file:
        input_file.write("y")
    update.message.reply_text('Agreed to continue')

TOKEN = "6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ"
chat_id = None
bot_instance = None

def main():
    global bot_instance
    updater = Updater(TOKEN)

    bot_instance = updater.bot

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("agree", agree))

    updater.start_polling()

    monitor_thread = threading.Thread(target=monitor_bot)
    monitor_thread.start()

    updater.idle()

if __name__ == "__main__":
    main()