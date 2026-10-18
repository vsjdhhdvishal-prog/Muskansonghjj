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

init_db()

# --- FLASK SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT HANDLERS ---

# 1. Track when bot is added/removed
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result:
        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            if result.new_chat_member.status in ["member", "administrator"]:
                add_group(chat.id, chat.title)
                print(f"Group added: {chat.title}")
            elif result.new_chat_member.status in ["left", "kicked"]:
                remove_group(chat.id)
                print(f"Group removed: {chat.title}")

# 2. Smart Auto-Save: Agar group me koi bhi message karega, bot use database me save kar lega
async def auto_save_group_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and chat.type in ["group", "supergroup"]:
        add_group(chat.id, chat.title)

# 3. Auto-reply for private chats
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await update.message.reply_text("Hello! Main ek auto-reply bot hoon.")

# 4. Broadcast Command (Sends replied post to ALL saved groups)
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kripya apni post ya link ko **Reply** karke `/broadcast` command bhejein!")
        return

    group_ids = get_all_groups()
    
    if not group_ids:
        await update.message.reply_text("⚠️ Abhi tak koi group saved nahi hai!")
        return

    success_count = 0
    fail_count = 0

    target_message_id = update.message.reply_to_message.message_id
    from_chat_id = update.effective_chat.id

    for chat_id in group_ids:
        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=target_message_id
            )
            success_count += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            fail_count += 1

    await update.message.reply_text(
        f"📢 **Broadcast Finished!**\n\n✅ Sent to: {success_count} groups\n❌ Failed: {fail_count}"
    )

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()

    TOKEN = os.environ.get("BOT_TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("broadcast", broadcast_message))
    
    # Group messages ko sunkar auto-save karne ke liye handler
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & (~filters.COMMAND), auto_save_group_on_message))
    
    # Private chat auto-reply handler
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, auto_reply))

    print("Bot fully active with Auto-Save Broadcast...")
    application.run_polling()
    
