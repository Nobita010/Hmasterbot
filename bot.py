import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# Constants
ADMIN_UID = '5976479963'  # Replace with your Telegram user ID
USERS = set()

# Define stages
SELECTING_GAME, ENTERING_AMOUNT = range(2)

# Game data
games = {
    1: {'title': 'Chain Cube 2048', 'token': 'd1690a07-3780-4068-810f-9b5bbf2931b2', 'promo_id': 'b4170868-cef0-424f-8eb9-be0622e8e8e3'},
    2: {'title': 'Train Miner', 'token': '82647f43-3f87-402d-88dd-09a90025313f', 'promo_id': 'c4480ac7-e178-4973-8061-9ed5b2e17954'},
    3: {'title': 'Merge Away', 'token': '8d1cc2ad-e097-4b86-90ef-7a27e19fb833', 'promo_id': 'dc128d28-c45b-411c-98ff-ac7726fbaea4'},
    4: {'title': 'Twerk Race 3D', 'token': '61308365-9d16-4040-8bb0-2f4a4c69074c', 'promo_id': '61308365-9d16-4040-8bb0-2f4a4c69074c'},
    5: {'title': 'Polysphere', 'token': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71', 'promo_id': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71'},
    6: {'title': 'Mow and Trim', 'token': 'ef319a80-949a-492e-8ee0-424fb5fc20a6', 'promo_id': 'ef319a80-949a-492e-8ee0-424fb5fc20a6'},
    7: {'title': 'Cafe Dash', 'token': 'bc0971b8-04df-4e72-8a3e-ec4dc663cd11', 'promo_id': 'bc0971b8-04df-4e72-8a3e-ec4dc663cd11'},
    8: {'title': 'Zoopolis', 'token': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b', 'promo_id': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b'},
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | Line %(lineno)d - %(message)s',
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    USERS.add(user_id)

    if str(user_id) == ADMIN_UID:
        await update.message.reply_text("Welcome Admin! Use /admin to see the number of users.")
    else:
        await update.message.reply_text("Welcome! Use /generate to start generating keys.")

    # Notify the admin
    if str(user_id) != ADMIN_UID:
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
    application = ApplicationBuilder().token(os.getenv('6719489487:AAFzVleCX-JJhoQBkvhAuynl1qvTGK9T9Ik')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={
            SELECTING_GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_game)],
            ENTERING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("admin", admin))

    application.run_polling()

if __name__ == "__main__":
    main()
