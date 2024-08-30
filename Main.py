import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram.ext.filters import Text

# Constants
ADMIN_UID = 'your_admin_uid'  # Replace with your Telegram user ID
USERS = set()

# Define stages
SELECTING_GAME, ENTERING_AMOUNT = range(2)

# Existing imports and code from your script...

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | Line %(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    USERS.add(user_id)

    if user_id == ADMIN_UID:
        await update.message.reply_text("Welcome Admin! Use /admin to see the number of users.")
    else:
        await update.message.reply_text("Welcome! Use /generate to start generating keys.")

    # Notify the admin
    if user_id != ADMIN_UID:
        await context.bot.send_message(ADMIN_UID, f"A new user has joined: {update.message.from_user.username} (ID: {user_id})")

async def generate(update: Update, context: CallbackContext):
    game_options = "\n".join([f"{k}: {v['title']}" for k, v in games.items()])
    await update.message.reply_text(f"Select a game by typing its number:\n{game_options}")
    return SELECTING_GAME

async def select_game(update: Update, context: CallbackContext):
    selected_game = int(update.message.text.strip())
    context.user_data['selected_game'] = selected_game
    await update.message.reply_text("Enter the number of keys to generate:")
    return ENTERING_AMOUNT

async def enter_amount(update: Update, context: CallbackContext):
    num_keys = int(update.message.text.strip())
    context.user_data['num_keys'] = num_keys

    selected_game = context.user_data['selected_game']
    game = games[selected_game]

    msg = f"Starting generation of {num_keys} key(s) for {game['title']}"
    logger.info(msg)
    await update.message.reply_text(msg)

    keys = await run_key_generation(selected_game, num_keys)
    if keys:
        key_list = "\n".join(keys)
        await update.message.reply_text(f"Generated keys:\n{key_list}")
    else:
        await update.message.reply_text("No keys were generated.")

    return ConversationHandler.END

async def admin(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if str(user_id) == ADMIN_UID:
        await update.message.reply_text(f"Number of users: {len(USERS)}")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

def main():
    application = ApplicationBuilder().token('YOUR_TELEGRAM_BOT_TOKEN').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={
            SELECTING_GAME: [MessageHandler(Filters.regex('^\d+$'), select_game)],
            ENTERING_AMOUNT: [MessageHandler(Filters.regex('^\d+$'), enter_amount)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("admin", admin))

    application.run_polling()

if __name__ == "__main__":
    main()
