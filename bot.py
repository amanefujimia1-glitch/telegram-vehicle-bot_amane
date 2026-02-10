import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

authorized_users = set()


def is_joined(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_joined(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{context.bot.get_chat(CHANNEL_ID).username}")]
        ]
        update.message.reply_text(
            "⚠️ Bot use করতে হলে আগে channel join করো",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if user_id != OWNER_ID and user_id not in authorized_users:
        update.message.reply_text("❌ তুমি authorized না")
        return

    update.message.reply_text("✅ Welcome! Bot ready 🚀")


def adduser(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        update.message.reply_text("Usage: /adduser user_id")
        return

    user_id = int(context.args[0])
    authorized_users.add(user_id)
    update.message.reply_text(f"✅ User {user_id} authorized")


def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/start - Start bot\n"
        "/adduser <id> - Authorize user (Owner only)"
    )


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("adduser", adduser))
    dp.add_handler(CommandHandler("help", help_cmd))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()