import os
import datetime
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from input_processing import process_input

# Add the start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I am your GPT-4 Assistant. Ask me anything!")

# Add the help_command function
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Ask me anything! Just type your question and I'll try to help.")

# Add this function to handle user input via Telegram
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    if user_input.strip() != "":
        processed_input = process_input(user_input)
        await update.message.reply_text(processed_input)
    else:
        await update.message.reply_text("Please enter some text.")


# Replace your original main() function with this one
def main() -> None:
    application = Application.builder().token("6253259092:AAG6bPFPOEbo5WOcTcXrbs-S_RwtZBM7jKQ").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add the 'ask' command
    application.add_handler(CommandHandler("ask", ask))

    # Add a message handler for non-command text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
