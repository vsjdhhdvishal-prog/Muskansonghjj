# =====================================================================
# FILE: bot.py (Ultra Advance Promotion & Group Engine)
# =====================================================================

import sys
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import BOT_TOKEN, OWNER_ID, GROUP_KNOWLEDGE_BASE, LOGGER, validate_system_config, BOT_VERSION
from database_server import DB_INSTANCE, WEB_SERVER_INSTANCE

class EnterpriseBotEngine:

    @staticmethod
    async def track_group_membership_changes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        result = update.my_chat_member
        if not result:
            return
        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            member_status = result.new_chat_member.status
            if member_status in ["member", "administrator"]:
                DB_INSTANCE.add_group(chat.id, chat.title)
                LOGGER.info(f"Group registered -> Title: {chat.title} [ID: {chat.id}]")
            elif member_status in ["left", "kicked"]:
                DB_INSTANCE.remove_group(chat.id)
                LOGGER.warning(f"Group removed -> Title: {chat.title} [ID: {chat.id}]")

    @staticmethod
    async def auto_save_active_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat and chat.type in ["group", "supergroup"]:
            DB_INSTANCE.add_group(chat.id, chat.title)

    @staticmethod
    async def handle_group_tag_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        chat = update.effective_chat
        if not chat or chat.type not in ["group", "supergroup"]:
            return

        bot_username = context.bot.username
        msg_text = update.message.text
        is_tagged = bot_username and f"@{bot_username.lower()}" in msg_text.lower()
        is_reply_to_bot = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id

        if is_tagged or is_reply_to_bot:
            txt_lower = msg_text.lower()
            
            if any(k in txt_lower for k in ["kahan", "rehte", "shehar", "city", "address"]):
                reply_out = random.choice(GROUP_KNOWLEDGE_BASE["interview_location"])
            elif any(k in txt_lower for k in ["kya karte", "study", "padhai", "school", "12th", "student"]):
                reply_out = random.choice(GROUP_KNOWLEDGE_BASE["interview_study"])
            elif any(k in txt_lower for k in ["attitude", "aukat", "bhav", "ghamand"]):
                reply_out = random.choice(GROUP_KNOWLEDGE_BASE["attitude"])
            elif any(k in txt_lower for k in ["pyaar", "flirt", "cute", "love"]):
                reply_out = random.choice(GROUP_KNOWLEDGE_BASE["flirt"])
            else:
                reply_out = random.choice(GROUP_KNOWLEDGE_BASE["default_pool"])

            try:
                await update.message.reply_text(reply_out)
            except Exception as exc:
                LOGGER.error(f"Error replying to group tag: {exc}")

    @staticmethod
    async def execute_secure_promotion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            await update.message.reply_text("⛔ Access Denied: Is command ki permission sirf bot owner ke paas hai!")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ **Ultra Promotion Guide:**\n\nKripya apni kisi bhi post, link, photo ya video ko **Reply** karke `/promotion` command bhejein!")
            return

        group_id_list = DB_INSTANCE.fetch_all_groups()
        if not group_id_list:
            await update.message.reply_text("⚠️ Database me abhi koi bhi group registered nahi hai! Pehle bot ko groups me add karein.")
            return

        success_tally = 0
        failure_tally = 0

        target_msg_id = update.message.reply_to_message.message_id
        source_chat_id = update.effective_chat.id

        status_notice = await update.message.reply_text(f"🚀 Ultra-Broadcasting promotion across {len(group_id_list)} saved groups...")

        for chat_id in group_id_list:
            try:
                await context.bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=source_chat_id,
                    message_id=target_msg_id
                )
                success_tally += 1
            except Exception as exc:
                LOGGER.error(f"Failed to broadcast to group {chat_id}: {exc}")
                failure_tally += 1

        summary_report = (
            f"📢 **Ultra Promotion Report**\n\n"
            f"✅ Successfully Delivered: {success_tally} groups\n"
            f"❌ Failed (Bot removed/kicked): {failure_tally} groups\n"
            f"📊 Total Target Groups: {len(group_id_list)}"
        )
        await status_notice.edit_text(summary_report)

class MassiveBotLauncher:
    def launch_bot_system(self) -> None:
        if not validate_system_config():
            sys.exit(1)

        WEB_SERVER_INSTANCE.spawn_server_thread()

        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            
            app.add_handler(ChatMemberHandler(EnterpriseBotEngine.track_group_membership_changes, ChatMemberHandler.MY_CHAT_MEMBER))
            app.add_handler(CommandHandler("promotion", EnterpriseBotEngine.execute_secure_promotion_command))
            app.add_handler(MessageHandler(filters.ChatType.GROUPS & (~filters.COMMAND), EnterpriseBotEngine.auto_save_active_groups))
            app.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.TEXT | filters.COMMAND), EnterpriseBotEngine.handle_group_tag_mentions))

            LOGGER.info("Ultra Advance Bot Engine started successfully with robust broadcasting...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as exc:
            LOGGER.critical(f"Critical launcher error: {exc}")
            sys.exit(1)

if __name__ == "__main__":
    launcher = MassiveBotLauncher()
    launcher.launch_bot_system()
    
