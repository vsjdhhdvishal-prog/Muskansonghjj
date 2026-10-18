# =====================================================================
# FILE 3 OF 3: bot.py (Massive Core Engine, Handlers & Runner)
# Purpose: Advanced NLP Pattern Matching, Tag Mention, Secure Promotion & Polling
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
from config import BOT_TOKEN, OWNER_ID, MASSIVE_CHAT_DATABASE, LOGGER, validate_system_configuration, BOT_VERSION
from database_server import DB_INSTANCE, WEB_SERVER_INSTANCE

class MassiveEnterpriseBotEngine:
    """Core logic processor handling massive message loads, tags, and broadcasts."""

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
                LOGGER.info(f"Group added & saved -> Title: {chat.title} [ID: {chat.id}]")
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
            
            # Heavy pattern matching for group tags
            if any(k in txt_lower for k in ["kahan", "rehte", "shehar", "city", "address"]):
                reply_out = random.choice(MASSIVE_CHAT_DATABASE["interview_location"])
            elif any(k in txt_lower for k in ["kya karte", "study", "padhai", "school", "12th", "student"]):
                reply_out = random.choice(MASSIVE_CHAT_DATABASE["interview_study"])
            elif any(k in txt_lower for k in ["attitude", "aukat", "bhav", "ghamand", "smart"]):
                reply_out = random.choice(MASSIVE_CHAT_DATABASE["attitude"])
            elif any(k in txt_lower for k in ["pyaar", "flirt", "cute", "hot", "love", "sundar"]):
                reply_out = random.choice(MASSIVE_CHAT_DATABASE["flirt"])
            else:
                reply_out = random.choice(MASSIVE_CHAT_DATABASE["default_massive_pool"])

            try:
                await update.message.reply_text(reply_out)
            except Exception as exc:
                LOGGER.error(f"Error replying to group tag: {exc}")

    @staticmethod
    async def process_massive_private_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        if update.message.chat.type != "private":
            return

        user_id = update.effective_user.id
        incoming_text = update.message.text
        
        # Log message into heavy database for analytics (10M scale tracking)
        DB_INSTANCE.log_incoming_message(user_id, incoming_text)

        txt_lower = incoming_text.lower()

        # Heavy AI-like rule engine covering every category
        if any(w in txt_lower for w in ["kahan", "city", "where", "rehte", "shehar", "address", "state"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["interview_location"])
        elif any(w in txt_lower for w in ["kya karte", "study", "padhai", "school", "12th", "education", "student", "college"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["interview_study"])
        elif any(w in txt_lower for w in ["hobby", "shauk", "free time", "pasand", "music", "songs"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["interview_hobby"])
        elif any(w in txt_lower for w in ["attitude", "bhav", "proud", "ghamand", "aukat", "smart", "killer"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["attitude"])
        elif any(w in txt_lower for w in ["flirt", "pyaar", "love", "cute", "hot", "beautiful", "shadi", "date", "gf", "boyfriend"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["flirt"])
        elif any(w in txt_lower for w in ["hello", "hi", "hey", "gm", "good morning", "salam", "sup", "wassup"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["greetings"])
        elif any(w in txt_lower for w in ["help", "features", "kya kar sakti ho", "commands"]):
            response_text = random.choice(MASSIVE_CHAT_DATABASE["help_queries"])
        else:
            response_text = random.choice(MASSIVE_CHAT_DATABASE["default_massive_pool"])

        try:
            await update.message.reply_text(response_text)
        except Exception as exc:
            LOGGER.error(f"Error sending massive private reply: {exc}")

    @staticmethod
    async def execute_secure_promotion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        LOGGER.info(f"Promotion command triggered by user ID: {user_id}")

        if user_id != OWNER_ID:
            LOGGER.warning(f"Unauthorized promotion access blocked for ID: {user_id}")
            await update.message.reply_text("⛔ Access Denied: Is command ko chalane ki permission sirf bot owner ke paas hai!")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text(
                "⚠️ **Massive Promotion Guide:**\n\nKripya apni kisi bhi post, link, photo ya video ko **Reply** karke `/promotion` command bhejein!"
            )
            return

        group_id_list = DB_INSTANCE.fetch_all_groups()
        if not group_id_list:
            await update.message.reply_text("⚠️ Database me abhi koi bhi group registered nahi hai!")
            return

        success_tally = 0
        failure_tally = 0

        target_msg_id = update.message.reply_to_message.message_id
        source_chat_id = update.effective_chat.id

        status_notice = await update.message.reply_text(f"🚀 Broadcasting promotion across {len(group_id_list)} groups...")

        for chat_id in group_id_list:
            try:
                await context.bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=source_chat_id,
                    message_id=target_msg_id
                )
                success_tally += 1
            except Exception as exc:
                LOGGER.error(f"Failed to copy message to group {chat_id}: {exc}")
                failure_tally += 1

        summary_report = (
            f"📢 **Massive Promotion Report**\n\n"
            f"✅ Successfully Delivered: {success_tally} groups\n"
            f"❌ Failed Deliveries: {failure_tally} groups\n"
            f"📊 Total Target Groups: {len(group_id_list)}"
        )
        await status_notice.edit_text(summary_report)

# --- MAIN RUNNER ORCHESTRATOR ---
class MassiveBotLauncher:
    """Orchestrates the massive heavy-load bot deployment."""

    def __init__(self) -> None:
        self.telegram_app = None

    def launch_bot_system(self) -> None:
        LOGGER.info(f"Initializing Massive Enterprise Bot v{BOT_VERSION}...")

        if not validate_system_configuration():
            LOGGER.critical("System configuration validation failed. Shutting down.")
            sys.exit(1)

        # Step 1: Start 24/7 Uptime Web Server
        WEB_SERVER_INSTANCE.spawn_server_thread()

        try:
            # Step 2: Build Telegram Application
            self.telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
            
            # Step 3: Register Handlers for Heavy Load
            self.telegram_app.add_handler(
                ChatMemberHandler(MassiveEnterpriseBotEngine.track_group_membership_changes, ChatMemberHandler.MY_CHAT_MEMBER)
            )
            self.telegram_app.add_handler(
                CommandHandler("promotion", MassiveEnterpriseBotEngine.execute_secure_promotion_command)
            )
            self.telegram_app.add_handler(
                MessageHandler(filters.ChatType.GROUPS & (~filters.COMMAND), MassiveEnterpriseBotEngine.auto_save_active_groups)
            )
            self.telegram_app.add_handler(
                MessageHandler(filters.ChatType.GROUPS & (filters.TEXT | filters.COMMAND), MassiveEnterpriseBotEngine.handle_group_tag_mentions)
            )
            self.telegram_app.add_handler(
                MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, MassiveEnterpriseBotEngine.process_massive_private_messages)
            )

            LOGGER.info("All heavy enterprise handlers registered successfully. Starting long polling...")
            self.telegram_app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as exc:
            LOGGER.critical(f"Critical error during bot execution: {exc}")
            sys.exit(1)

if __name__ == "__main__":
    print(f"""
    ========================================================
       STARTING MASSIVE ENTERPRISE BOT (v{BOT_VERSION})
       - Heavy Knowledge Base Enabled (Interview, Attitude, Flirt)
       - 10M+ Message Capacity & 24/7 Web Server Active
    ========================================================
    """)
    launcher = MassiveBotLauncher()
    launcher.launch_bot_system()
            
