import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, ChatMemberHandler, CommandHandler, filters
from flask import Flask
import threading

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_group(chat_id, title):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?, ?)', (chat_id, title))
    conn.commit()
    conn.close()

def remove_group(chat_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM groups WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()

def get_all_groups():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM groups')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Initialize database on start
init_db()

# --- FLASK SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 with Database!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT HANDLERS ---

# 1. Track Groups & Save to DB
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result:
        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            if result.new_chat_member.status in ["member", "administrator"]:
                add_group(chat.id, chat.title)
                print(f"Group saved to DB: {chat.title} (ID: {chat.id})")
            elif result.new_chat_member.status in ["left", "kicked"]:
                remove_group(chat.id)
                print(f"Group removed from DB: {chat.title}")

# 2. Auto-reply for private chats
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("Hello! Main ek auto-reply bot hoon. Aapke message ke liye shukriya.")

# 3. Promote Command (Sends link to all saved groups)
async def promote_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kripya link ke sath command dein. Jaise:\n/promote https://yourlink.com")
        return

    promo_message = "📢 **Special Promotion:**\n\n" + " ".join(context.args)
    
    group_ids = get_all_groups()
    success_count = 0
    fail_count = 0

    for chat_id in group_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=promo_message, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            fail_count += 1

    await update.message.reply_text(f"Promotion Sent!\n✅ Success: {success_count}\n❌ Failed: {fail_count}")

if __name__ == '__main__':
    # Start Flask server in a separate thread
    t = threading.Thread(target=run_web)
    t.start()

    TOKEN = os.environ.get("BOT_TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("promote", promote_link))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_reply))

    print("Telegram Bot start ho chuka hai with SQLite Database...")
    application.run_polling()
    
