import os
import time
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ========= CONFIG =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # example: -1003296016362

OWNER_NAME = "@amane_loyal_me"
CHANNEL_LINK = "https://t.me/YOUR_CHANNEL_USERNAME"  # change this
VEHICLE_API = "https://amane.djsouravrooj33.workers.dev/?rc="
USERS_FILE = "authorized_users.txt"

last_used = {}

# ========= USER STORAGE =========
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(int(x.strip()) for x in f if x.strip().isdigit())

def save_users(users):
    with open(USERS_FILE, "w") as f:
        for u in users:
            f.write(str(u) + "\n")

AUTHORIZED_USERS = load_users()

# ========= CHECKS =========
def is_owner(update: Update):
    return update.effective_user.id == OWNER_ID

def is_authorized(update: Update):
    return update.effective_user.id in AUTHORIZED_USERS or is_owner(update)

def anti_spam(user_id):
    now = time.time()
    last = last_used.get(user_id, 0)
    last_used[user_id] = now
    return now - last < 3

async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=update.effective_user.id
        )
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

def join_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔔 Join Channel", url=CHANNEL_LINK)]]
    )

# ========= COMMANDS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return

    if not await is_joined(update, context):
        await update.message.reply_text(
            "🔒 Bot ব্যবহার করতে হলে আগে channel join করতে হবে",
            reply_markup=join_button()
        )
        return

    await update.message.reply_text(
        f"✅ Vehicle Bot Active\n"
        f"👑 Owner: {OWNER_NAME}\n\n"
        f"🚗 RC number পাঠাও"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    await update.message.reply_text(
        "🤖 Vehicle Bot Help\n\n"
        "Commands:\n"
        "/start – Bot start\n"
        "/help – Help menu\n"
        "/adduser <id> – Owner only\n"
        "/removeuser <id> – Owner only\n\n"
        f"👑 Owner: {OWNER_NAME}"
    )

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /adduser <user_id>")
        return

    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user id")
        return

    AUTHORIZED_USERS.add(uid)
    save_users(AUTHORIZED_USERS)
    await update.message.reply_text(f"✅ Authorized: {uid}")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    try:
        uid = int(context.args[0])
    except:
        await update.message.reply_text("Usage: /removeuser <user_id>")
        return

    AUTHORIZED_USERS.discard(uid)
    save_users(AUTHORIZED_USERS)
    await update.message.reply_text(f"❌ Removed: {uid}")

# ========= SEARCH =========
async def vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not await is_joined(update, context):
        await update.message.reply_text(
            "🔒 আগে channel join করো",
            reply_markup=join_button()
        )
        return

    if anti_spam(update.effective_user.id):
        await update.message.reply_text("⚠️ Slow down")
        return

    rc = update.message.text.strip()
    if len(rc) < 5:
        await update.message.reply_text("❌ Invalid RC number")
        return

    try:
        r = requests.get(VEHICLE_API + rc, timeout=10)
        await update.message.reply_text(
            f"🚗 Vehicle Info\n\n"
            f"{r.text}\n\n"
            f"🔎 Search by: {OWNER_NAME}"
        )
    except:
        await update.message.reply_text("⚠️ API Error")

# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, vehicle))

    print("🔥 Bot running successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
