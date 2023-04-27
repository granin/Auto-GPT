
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def on_output_file_updated(content):
    global chat_id, bot_instance
    if chat_id:
        bot_instance.send_message(chat_id=chat_id, text=f"File updated: {content}")
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

app = ApplicationBuilder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("agree", agree))
app.add_handler(CommandHandler("start", start))
app.run_polling()