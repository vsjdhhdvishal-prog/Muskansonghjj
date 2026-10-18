    @staticmethod
    async def execute_secure_promotion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            await update.message.reply_text("⛔ Access Denied: Is command ki permission sirf owner ke paas hai!")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Kripya apni post/link ko **Reply** karke `/promotion` command bhejein!")
            return

        # Smart Sync: Current chat me bhi check karega agar group hai toh save kar lega
        current_chat = update.effective_chat
        if current_chat and current_chat.type in ["group", "supergroup"]:
            DB_INSTANCE.add_group(current_chat.id, current_chat.title)

        group_id_list = DB_INSTANCE.fetch_all_groups()
        if not group_id_list:
            await update.message.reply_text("⚠️ Database me abhi koi group registered nahi hai!")
            return

        success_tally, failure_tally = 0, 0
        target_msg_id = update.message.reply_to_message.message_id
        source_chat_id = current_chat.id

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

        await status_notice.edit_text(
            f"📢 **Promotion Report**\n\n✅ Success: {success_tally}\n❌ Failed: {failure_tally}\n📊 Total: {len(group_id_list)}"
        )
        
