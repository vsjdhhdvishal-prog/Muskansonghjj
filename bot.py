import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, ChatMemberHandler, CommandHandler, filters
from flask import Flask
import threading

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CONNECTED_GROUPS = set()

# 1. Render ke liye Mini Flask Server (Taaki Render service active rahe)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Track Groups
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result:
        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            if result.new_chat_member.status in ["member", "administrator"]:
                CONNECTED_GROUPS.add(chat.id)
                print(f"Group me add ho gaya: {chat.title}")
            elif result.new_chat_member.status in ["left", "kicked"]:
                CONNECTED_GROUPS.discard(chat.id)

# 3. Auto-reply for private chats
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("Hello! Main ek auto-reply bot hoon.")

# 4. Promote Command
async def promote_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kripya link ke sath command dein. Jaise: /promote https://yourlink.com")
        return

    promo_message = "📢 **Special Promotion:**\n\n" + " ".join(context.args)
    
    success_count = 0
    for chat_id in CONNECTED_GROUPS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=promo_message, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

    await update.message.reply_text(f"Promotion sent to {success_count} groups!")

if __name__ == '__main__':
    # Flask server ko alag thread me chalana
    t = threading.Thread(target=run_web)
    t.start()

    TOKEN = os.environ.get("BOT_TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("promote", promote_link))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_reply))

    print("Telegram Bot start ho chuka hai...")
    application.run_polling()
    
