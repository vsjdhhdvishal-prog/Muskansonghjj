# =====================================================================
# FILE 4 OF 5: handlers.py
# Purpose: Telegram Message Handlers and Interview Persona Engine
# Lines: ~300
# =====================================================================

import random
from telegram import Update
from telegram.ext import ContextTypes
from config import INTERVIEW_KNOWLEDGE_BASE, LOGGER, OWNER_ID
from database import DB_MANAGER

class EnterpriseBotHandlers:
    """Contains all core business logic for handling incoming Telegram events."""

    @staticmethod
    async def track_chats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Tracks when the bot is added to or removed from group chats."""
        result = update.my_chat_member
        if not result:
            return

        chat = result.chat
        if chat.type in ["group", "supergroup"]:
            new_status = result.new_chat_member.status
            if new_status in ["member", "administrator"]:
                DB_MANAGER.add_group(chat.id, chat.title)
                LOGGER.info(f"Bot added to group -> Title: {chat.title}, ID: {chat.id}")
            elif new_status in ["left", "kicked"]:
                DB_MANAGER.remove_group(chat.id)
                LOGGER.warning(f"Bot removed from group -> Title: {chat.title}, ID: {chat.id}")

    @staticmethod
    async def auto_save_on_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Smart Auto-Save: Ensures active groups are never missed if chat occurs."""
        chat = update.effective_chat
        if chat and chat.type in ["group", "supergroup"]:
            DB_MANAGER.add_group(chat.id, chat.title)

    @staticmethod
    async def interview_auto_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """High-performance private chat interview engine capable of handling massive message loads."""
        if not update.message or not update.message.text:
            return

        if update.message.chat.type != "private":
            return

        user_message = update.message.text.lower()
        LOGGER.debug(f"Processing private message from user {update.effective_user.id}: {user_message}")

        # Intelligent Persona Matching
        response_text = ""
        if any(keyword in user_message for keyword in ["kahan", "city", "where", "rehte", "shehar", "location"]):
            response_text = random.choice(INTERVIEW_KNOWLEDGE_BASE["location"])
        elif any(keyword in user_message for keyword in ["kya karte", "study", "padhai", "school", "12th", "education"]):
            response_text = random.choice(INTERVIEW_KNOWLEDGE_BASE["education"])
        elif any(keyword in user_message for keyword in ["naam", "name", "who are you", "kaun ho"]):
            response_text = random.choice(INTERVIEW_KNOWLEDGE_BASE["identity"])
        elif any(keyword in user_message for keyword in ["hello", "hi", "hey", "good morning", "salam"]):
            response_text = random.choice(INTERVIEW_KNOWLEDGE_BASE["greetings"])
        else:
            response_text = random.choice(INTERVIEW_KNOWLEDGE_BASE["default"])

        # Send response asynchronously
        try:
            await update.message.reply_text(response_text)
            DB_MANAGER.log_event("PRIVATE_REPLY", f"User: {update.effective_user.id}")
        except Exception as exc:
            LOGGER.error(f"Failed to send private auto-reply: {exc}")

    @staticmethod
    async def promotion_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Owner-only secure promotion command to broadcast posts to all registered groups."""
        user_id = update.effective_user.id
        LOGGER.info(f"Promotion command triggered by user ID: {user_id}")

        # Strict Owner Security Check
        if user_id != OWNER_ID:
            LOGGER.warning(f"Unauthorized promotion attempt by user ID: {user_id}")
            await update.message.reply_text("⛔ Access Denied: Yeh command chalane ki permission sirf bot owner ke paas hai!")
            return

        # Check if user replied to a message/post
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "⚠️ **Promotion Guide:**\n\nKripya apni kisi bhi post, link, photo ya video ko **Reply** karke `/promotion` command bhejein!"
            )
            return

        group_ids = DB_MANAGER.get_all_group_ids()
        if not group_ids:
            await update.message.reply_text("⚠️ Database me abhi koi bhi group registered nahi hai!")
            return

        success_count = 0
        fail_count = 0

        target_message_id = update.message.reply_to_message.message_id
        from_chat_id = update.effective_chat.id

        status_msg = await update.message.reply_text(f"🚀 Broadcasting promotion to {len(group_ids)} groups...")

        for chat_id in group_ids:
            try:
                await context.bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_id=target_message_id
                )
                success_count += 1
            except Exception as exc:
                LOGGER.error(f"Failed to broadcast to group {chat_id}: {exc}")
                fail_count += 1

        # Final Report
        report = (
            f"📢 **Promotion Broadcast Summary**\n\n"
            f"✅ Successfully Sent: {success_count} groups\n"
            f"❌ Failed Deliveries: {fail_count} groups\n"
            f"📊 Total Target Groups: {len(group_ids)}"
        )
        await status_msg.edit_text(report)
        DB_MANAGER.log_event("BROADCAST_COMPLETED", f"Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    LOGGER.info("Handlers module loaded successfully.")
  
