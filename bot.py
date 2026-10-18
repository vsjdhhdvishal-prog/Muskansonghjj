import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, ChatMemberHandler, CommandHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Groups ki chat ID save karne ke liye ek set (yeh memory me save rahega)
# Note: Agar bot restart hoga toh yeh list khali ho jayegi. Bade level par database use hota hai.
CONNECTED_GROUPS = set()

# 1. Jab bot kisi group me add hoga, uska ID save ho jayega
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result:
        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            if result.new_chat_member.status in ["member", "administrator"]:
                CONNECTED_GROUPS.add(chat.id)
                print(f"Group me add ho gaya: {chat.title} (ID: {chat.id})")
            elif result.new_chat_member.status in ["left", "kicked"]:
                CONNECTED_GROUPS.discard(chat.id)
                print(f"Group se nikal diya gaya: {chat.title}")

# 2. Personal chat ke liye Auto-Reply
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sirf personal chat (private chat) me auto-reply karega
    if update.message.chat.type == "private":
        reply_text = "Hello! Main ek auto-reply bot hoon. Aapke message ke liye shukriya."
        await update.message.reply_text(reply_text)

# 3. Promotion Command (/promote <link>)
async def promote_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yeh command sirf aap (admin/owner) chala sakein, iske liye aap apni Telegram User ID yahan daal sakte hain
    owner_id = 123456789  # Yahan apni Telegram ID daalein (Optional)
    
    if update.effective_user.id != owner_id and owner_id != 123456789:
        await update.message.reply_text("Aapko yeh command chalane ki permission nahi hai!")
        return

    # Check karein ki link diya gaya hai ya nahi
    if not context.args:
        await update.message.reply_text("Kripya link ke sath command dein. Jaise: /promote https://t.yourlink.com")
        return

    promo_message = "📢 **Special Promotion:**\n\n" + " ".join(context.args)
    
    success_count = 0
    fail_count = 0

    # Sabhi saved groups me message bhejna
    for chat_id in CONNECTED_GROUPS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=promo_message, parse_mode="Markdown")
            success_count += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            fail_count += 1

    await update.message.reply_text(f"Promotion sent successfully!\n✅ Success: {success_count}\n❌ Failed: {fail_count}")

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers add karna
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("promote", promote_link))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_reply))

    print("Bot start ho chuka hai...")
    application.run_polling()
  
